from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory storage for todos (in production, use a database)
todos = []
next_id = 1

# File to persist todos
TODOS_FILE = 'todos.json'

def load_todos():
    """Load todos from file if it exists"""
    global todos, next_id
    if os.path.exists(TODOS_FILE):
        try:
            with open(TODOS_FILE, 'r') as f:
                data = json.load(f)
                todos = data.get('todos', [])
                next_id = data.get('next_id', 1)
        except (json.JSONDecodeError, FileNotFoundError):
            todos = []
            next_id = 1

def save_todos():
    """Save todos to file"""
    with open(TODOS_FILE, 'w') as f:
        json.dump({'todos': todos, 'next_id': next_id}, f, indent=2)

# Load todos on startup
load_todos()

@app.route('/api/todos', methods=['GET'])
def get_todos():
    """Get all todos"""
    return jsonify(todos)

@app.route('/api/todos', methods=['POST'])
def create_todo():
    """Create a new todo"""
    global next_id
    
    data = request.get_json()
    
    if not data or 'todo' not in data:
        return jsonify({'error': 'Todo text is required'}), 400
    
    new_todo = {
        'id': next_id,
        'todo': data['todo'],
        'isDone': data.get('isDone', False)
    }
    
    todos.append(new_todo)
    next_id += 1
    save_todos()
    
    return jsonify(new_todo), 201

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update a specific todo"""
    data = request.get_json()
    
    for todo in todos:
        if todo['id'] == todo_id:
            if 'todo' in data:
                todo['todo'] = data['todo']
            if 'isDone' in data:
                todo['isDone'] = data['isDone']
            save_todos()
            return jsonify(todo)
    
    return jsonify({'error': 'Todo not found'}), 404

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a specific todo"""
    global todos
    
    for i, todo in enumerate(todos):
        if todo['id'] == todo_id:
            deleted_todo = todos.pop(i)
            save_todos()
            return jsonify(deleted_todo)
    
    return jsonify({'error': 'Todo not found'}), 404

@app.route('/api/todos/<int:todo_id>/toggle', methods=['PATCH'])
def toggle_todo(todo_id):
    """Toggle the completion status of a specific todo"""
    for todo in todos:
        if todo['id'] == todo_id:
            todo['isDone'] = not todo['isDone']
            save_todos()
            return jsonify(todo)
    
    return jsonify({'error': 'Todo not found'}), 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':

    app.run(debug=True, port=5000)
