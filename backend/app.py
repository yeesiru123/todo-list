from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os
import uuid
import threading
from jose import jwt
from kafka import KafkaConsumer, KafkaProducer
import clickhouse_connect
from clickhouse_driver import Client

# Create ClickHouse clients
ch_client = clickhouse_connect.get_client(host='localhost', port=18123, username='default', password='mysecret')
clickhouse_client = Client(host='localhost', port=19000, user='default', password='mysecret')

# Create Kafka producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

# Create Kafka consumer
consumer = KafkaConsumer(
    'todo_events',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='todo_events_group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Initialize tables
def init_tables():
    # Create todos_stream table
    ch_client.command('''
    CREATE TABLE IF NOT EXISTS todos_stream (
       id UInt32,
       user_id String,
       todo String,
       isDone UInt8,
       updated_at DateTime DEFAULT now(),
       deleted UInt8 DEFAULT 0
    ) ENGINE = ReplacingMergeTree(updated_at)
    ORDER BY (user_id, id)
    ''')

    # Create events table
    clickhouse_client.execute('''
        CREATE DATABASE IF NOT EXISTS todo_db
    ''')

    clickhouse_client.execute('''
        CREATE TABLE IF NOT EXISTS todo_db.todo_events (
            event_id String,
            event_type String,
            todo_id String,
            title String,
            description String,
            is_done UInt8,
            user_id String,
            timestamp DateTime
        ) ENGINE = MergeTree()
        ORDER BY (timestamp, event_id)
    ''')

def publish_event(event_type, todo_data, user_id):
    event = {
        'event_id': str(uuid.uuid4()),
        'event_type': event_type,
        'todo_id': str(todo_data['id']),
        'title': todo_data['todo'],
        'is_done': bool(todo_data['isDone']),
        'user_id': user_id,
        'timestamp': datetime.now().isoformat()
    }
    producer.send('todo_events', event)

def process_event(event):
    event_data = {
        'event_id': event['event_id'],
        'event_type': event['event_type'],
        'todo_id': event['todo_id'],
        'title': event['title'],
        'description': '',
        'is_done': 1 if event.get('is_done', False) else 0,
        'user_id': event['user_id'],
        'timestamp': datetime.fromisoformat(event['timestamp'])
    }
    
    clickhouse_client.execute(
        '''
        INSERT INTO todo_db.todo_events (
            event_id, event_type, todo_id, title, description,
            is_done, user_id, timestamp
        ) VALUES
        ''',
        [event_data]
    )

def kafka_consumer_thread():
    print("Starting Kafka consumer...")
    print("Waiting for messages on topic 'todo_events'...")
    try:
        for message in consumer:
            try:
                print(f"\nReceived message: {json.dumps(message.value, indent=2)}")
                process_event(message.value)
                print(f"✓ Successfully processed {message.value['event_type']} event for todo {message.value['todo_id']}")
                print(f"  - Title: {message.value['title']}")
                print(f"  - User: {message.value['user_id']}")
                print(f"  - Timestamp: {message.value['timestamp']}")
            except Exception as e:
                print(f"❌ Error processing event: {e}")
    except KeyboardInterrupt:
        print("\nShutting down consumer...")
    finally:
        consumer.close()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_user_id_from_token(request):
    auth_header = request.headers.get('Authorization', None)
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.get_unverified_claims(token)
        return decoded.get('sub') or decoded.get('preferred_username')
    except Exception:
        return None

@app.route('/api/todos', methods=['GET'])
def get_todos():
    """Get all non-deleted todos from ClickHouse (ReplacingMergeTree)"""
    user_id = get_user_id_from_token(request)
    if not user_id:
        return jsonify({'error': 'Missing or invalid token'}), 401

    result = ch_client.query('''
        SELECT id, todo, isDone, updated_at FROM todos_stream
        WHERE deleted = 0 AND user_id = %(user_id)s
        ORDER BY id ASC, updated_at DESC
    ''', {'user_id': user_id})
    
    todos = {}
    for row in result.result_rows:
        todo_id = row[0]
        if todo_id not in todos:
            todos[todo_id] = dict(zip(result.column_names, row))
    return jsonify(list(todos.values()))

@app.route('/api/todos', methods=['POST'])
def create_todo():
    """Create a new todo in ClickHouse (ReplacingMergeTree)"""
    user_id = get_user_id_from_token(request)
    if not user_id:
        return jsonify({'error': 'Missing or invalid token'}), 401

    data = request.get_json()
    if not data or 'todo' not in data:
        return jsonify({'error': 'Todo text is required'}), 400

    result = ch_client.query('SELECT max(id) FROM todos_stream')
    max_id = result.result_rows[0][0] or 0
    new_id = int(max_id) + 1

    columns = ['id', 'user_id', 'todo', 'isDone']
    data_block = [(new_id, user_id, data['todo'], int(data.get('isDone', 0)))]
    ch_client.insert('todos_stream', data_block, column_names=columns)

    result = ch_client.query(f"""
        SELECT id, todo, isDone, updated_at
        FROM todos_stream
        WHERE id = {new_id} AND deleted = 0
        ORDER BY updated_at DESC
        LIMIT 1
    """)

    todo_row = result.result_rows[0]
    todo_dict = dict(zip(result.column_names, todo_row))
    
    publish_event('todo_created', todo_dict, user_id)
    return jsonify(todo_dict), 201

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update a specific todo in ClickHouse (ReplacingMergeTree)"""
    data = request.get_json()
    user_id = get_user_id_from_token(request)
    if not user_id:
        return jsonify({'error': 'Missing or invalid token'}), 401

    result = ch_client.query(f"""
            SELECT id, todo, isDone, updated_at
            FROM todos_stream
            WHERE id = {todo_id} AND user_id = %(user_id)s AND deleted = 0
            ORDER BY updated_at DESC LIMIT 1
        """, {'user_id': user_id})
    if not result.result_rows:
        return jsonify({'error': 'Todo not found'}), 404

    todo = dict(zip(result.column_names, result.result_rows[0]))
    now = datetime.now()

    updated_todo = {
        'id': todo_id,
        'user_id': user_id,
        'todo': data.get('todo', todo['todo']),
        'isDone': int(data.get('isDone', todo['isDone'])),
        'updated_at': now,
        'deleted': 0
    }

    columns = ['id', 'user_id', 'todo', 'isDone', 'updated_at', 'deleted']
    row = tuple(updated_todo[col] for col in columns)
    ch_client.insert('todos_stream', [row], column_names=columns)

    result = ch_client.query(f"""
        SELECT id, todo, isDone, updated_at
        FROM todos_stream
        WHERE id = {todo_id} AND user_id = %(user_id)s AND deleted = 0
        ORDER BY updated_at DESC LIMIT 1
    """, {'user_id': user_id})
    todo_row = result.result_rows[0]
    todo_dict = dict(zip(result.column_names, todo_row))
    
    publish_event('todo_updated', todo_dict, user_id)
    return jsonify(todo_dict)

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Logically delete a specific todo in ClickHouse (ReplacingMergeTree)"""
    user_id = get_user_id_from_token(request)
    if not user_id:
        return jsonify({'error': 'Missing or invalid token'}), 401

    result = ch_client.query(
        f"SELECT id, todo, isDone, updated_at FROM todos_stream WHERE id = {todo_id} AND user_id = %(user_id)s AND deleted = 0 ORDER BY updated_at DESC LIMIT 1",
        {'user_id': user_id}
    )
    if not result.result_rows:
        return jsonify({'error': 'Todo not found'}), 404

    todo_row = result.result_rows[0]
    todo_dict = dict(zip(result.column_names, todo_row))
    now = datetime.now()
    deleted_todo = {
        'id': todo_id,
        'user_id': user_id,
        'todo': todo_dict['todo'],
        'isDone': todo_dict['isDone'],
        'updated_at': now,
        'deleted': 1
    }
    columns = ['id', 'user_id', 'todo', 'isDone', 'updated_at', 'deleted']
    row = tuple(deleted_todo[col] for col in columns)
    ch_client.insert('todos_stream', [row], column_names=columns)
    
    publish_event('todo_deleted', todo_dict, user_id)
    return jsonify(todo_dict)

@app.route('/api/todos/<int:todo_id>/toggle', methods=['PATCH'])
def toggle_todo(todo_id):
    """Toggle the completion status of a specific todo in ClickHouse (ReplacingMergeTree)"""
    user_id = get_user_id_from_token(request)
    if not user_id:
        return jsonify({'error': 'Missing or invalid token'}), 401

    result = ch_client.query(
        f"SELECT id, todo, isDone, updated_at FROM todos_stream WHERE id = {todo_id} AND user_id = %(user_id)s AND deleted = 0 ORDER BY updated_at DESC LIMIT 1",
        {'user_id': user_id}
    )
    if not result.result_rows:
        return jsonify({'error': 'Todo not found'}), 404

    todo = dict(zip(result.column_names, result.result_rows[0]))
    now = datetime.now()
    toggled_todo = (
        todo_id,
        user_id,
        todo['todo'],
        0 if todo['isDone'] else 1,
        now,
        0
    )
    columns = ['id', 'user_id', 'todo', 'isDone', 'updated_at', 'deleted']
    ch_client.insert('todos_stream', [toggled_todo], column_names=columns)

    updated_query = f"""
        SELECT id, todo, isDone, updated_at
        FROM todos_stream
        WHERE id = {todo_id} AND user_id = %(user_id)s AND deleted = 0
        ORDER BY updated_at DESC
        LIMIT 1
    """
    updated_result = ch_client.query(updated_query, {'user_id': user_id})
    todo_dict = dict(zip(updated_result.column_names, updated_result.result_rows[0]))
    
    publish_event('todo_toggled', todo_dict, user_id)
    return jsonify(todo_dict)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get events from ClickHouse"""
    user_id = get_user_id_from_token(request)
    if not user_id:
        return jsonify({'error': 'Missing or invalid token'}), 401

    result = clickhouse_client.execute('''
        SELECT event_type, title, is_done, timestamp
        FROM todo_db.todo_events
        WHERE user_id = %(user_id)s
        ORDER BY timestamp DESC
        LIMIT 100
    ''', {'user_id': user_id})

    events = [
        {
            'event_type': row[0],
            'title': row[1],
            'is_done': bool(row[2]),
            'timestamp': row[3].isoformat()
        }
        for row in result
    ]
    return jsonify(events)

def main():
    # Initialize tables
    init_tables()
    
    # Start Kafka consumer in a separate thread
    consumer_thread = threading.Thread(target=kafka_consumer_thread, daemon=True)
    consumer_thread.start()
    
    # Start Flask application
    app.run(debug=True, port=5000, use_reloader=False)

if __name__ == '__main__':
    main()
