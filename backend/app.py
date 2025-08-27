from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os


# ClickHouse integration
import clickhouse_connect


# Create a ClickHouse client
ch_client = clickhouse_connect.get_client(host='localhost', port=18123, username='default', password='mysecret')


# Create todos_stream table with ReplacingMergeTree if not exists
ch_client.command('''
CREATE TABLE IF NOT EXISTS todos_stream (
   id UInt32,
   todo String,
   isDone UInt8,
   updated_at DateTime DEFAULT now(),
   deleted UInt8 DEFAULT 0
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY id
''')


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes




@app.route('/api/todos', methods=['GET'])
def get_todos():
   """Get all non-deleted todos from ClickHouse (ReplacingMergeTree)"""
   result = ch_client.query('''
       SELECT id, todo, isDone, updated_at FROM todos_stream
       WHERE deleted = 0
       ORDER BY id ASC, updated_at DESC
   ''')
   # Only keep the latest version per id
   todos = {}
   for row in result.result_rows:
       todo_id = row[0]
       if todo_id not in todos:
           todos[todo_id] = dict(zip(result.column_names, row))
   return jsonify(list(todos.values()))


@app.route('/api/todos', methods=['POST'])
def create_todo():
   """Create a new todo in ClickHouse (ReplacingMergeTree)"""
   from datetime import datetime
   data = request.get_json()
   if not data or 'todo' not in data:
       return jsonify({'error': 'Todo text is required'}), 400


   # Get the next id
   result = ch_client.query('SELECT max(id) FROM todos_stream')
   max_id = result.result_rows[0][0] or 0
   new_id = int(max_id) + 1


   now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


   columns = ['id', 'todo', 'isDone']
   data_block = [(new_id, data['todo'], int(data.get('isDone', 0)))]




   ch_client.insert('todos_stream', data_block, column_names=columns)


   # Fetch the inserted todo
   result = ch_client.query(f"""
       SELECT id, todo, isDone, updated_at
       FROM todos_stream
       WHERE id = {new_id} AND deleted = 0
       ORDER BY updated_at DESC
       LIMIT 1
   """)


   todo_row = result.result_rows[0]
   todo_dict = dict(zip(result.column_names, todo_row))
  
   return jsonify(todo_dict), 201


@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
   """Update a specific todo in ClickHouse (ReplacingMergeTree)"""
   from datetime import datetime
   data = request.get_json()


   # Fetch latest version
   result = ch_client.query(f"""
           SELECT id, todo, isDone, updated_at
           FROM todos_stream
           WHERE id = {todo_id} AND deleted = 0
           ORDER BY updated_at DESC LIMIT 1
       """)
   if not result.result_rows:
       return jsonify({'error': 'Todo not found'}), 404


   todo = dict(zip(result.column_names, result.result_rows[0]))
   now = datetime.now()  # keep as datetime object


   updated_todo = {
       'id': todo_id,
       'todo': data.get('todo', todo['todo']),
       'isDone': int(data.get('isDone', todo['isDone'])),
       'updated_at': now,
       'deleted': 0
   }


   columns = ['id', 'todo', 'isDone', 'updated_at', 'deleted']
   row = tuple(updated_todo[col] for col in columns)


   ch_client.insert('todos_stream', [row], column_names=columns)


   # Fetch updated todo
   result = ch_client.query(f"""
       SELECT id, todo, isDone, updated_at
       FROM todos_stream
       WHERE id = {todo_id} AND deleted = 0
       ORDER BY updated_at DESC LIMIT 1
   """)
   todo_row = result.result_rows[0]
   todo_dict = dict(zip(result.column_names, todo_row))
   return jsonify(todo_dict)




@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
   """Logically delete a specific todo in ClickHouse (ReplacingMergeTree)"""
   from datetime import datetime


   # Fetch todo before deleting
   result = ch_client.query(f"SELECT id, todo, isDone, updated_at FROM todos_stream WHERE id = {todo_id} AND deleted = 0 ORDER BY updated_at DESC LIMIT 1")
   if not result.result_rows:
       return jsonify({'error': 'Todo not found'}), 404


   todo_row = result.result_rows[0]
   todo_dict = dict(zip(result.column_names, todo_row))
   now = datetime.now()
  
   deleted_todo = {
       'id': todo_id,
       'todo': todo_dict['todo'],
       'isDone': todo_dict['isDone'],
       'updated_at': now,
       'deleted': 1
   }


   columns = ['id', 'todo', 'isDone', 'updated_at', 'deleted']
   row = tuple(deleted_todo[col] for col in columns)


   ch_client.insert('todos_stream', [row], column_names=columns)
   return jsonify(todo_dict)


@app.route('/api/todos/<int:todo_id>/toggle', methods=['PATCH'])
def toggle_todo(todo_id):
   """Toggle the completion status of a specific todo in ClickHouse (ReplacingMergeTree)"""
   from datetime import datetime


   # Fetch existing todo
   result = ch_client.query(f"SELECT id, todo, isDone, updated_at FROM todos_stream WHERE id = {todo_id} AND deleted = 0 ORDER BY updated_at DESC LIMIT 1")
   if not result.result_rows:
       return jsonify({'error': 'Todo not found'}), 404


   todo = dict(zip(result.column_names, result.result_rows[0]))
   now = datetime.now()
  
   toggled_todo = (
       todo_id,
       todo['todo'],
       0 if todo['isDone'] else 1,
       now,
       0
   )


   columns = ['id', 'todo', 'isDone', 'updated_at', 'deleted']
   ch_client.insert('todos_stream', [toggled_todo], column_names=columns)


   # Fetch updated todo
   updated_query = f"""
       SELECT id, todo, isDone, updated_at
       FROM todos_stream
       WHERE id = {todo_id} AND deleted = 0
       ORDER BY updated_at DESC
       LIMIT 1
   """
   updated_result = ch_client.query(updated_query)
   todo_dict = dict(zip(updated_result.column_names, updated_result.result_rows[0]))


   return jsonify(todo_dict)


@app.route('/api/health', methods=['GET'])
def health_check():
   """Health check endpoint"""
   return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':


   app.run(debug=True, port=5000)