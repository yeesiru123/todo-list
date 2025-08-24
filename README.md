# Todo List with Flask Backend

A full-stack Todo List application with React frontend and Flask backend API.

## Features

- ✅ Add new todos
- ✅ Mark todos as complete/incomplete
- ✅ Edit todo text
- ✅ Delete todos
- ✅ Filter todos (All, Active, Completed)
- ✅ Persistent storage with JSON file
- ✅ REST API with JSON requests/responses
- ✅ Loading states and error handling

## Project Structure

```
todo-list/
├── backend/
│   ├── app.py              # Flask API server
│   ├── requirements.txt    # Python dependencies
│   └── todos.json         # Data persistence file (auto-generated)
├── src/
│   ├── api.ts             # API service layer
│   ├── App.tsx            # Main React component
│   ├── model.ts           # TypeScript interfaces
│   └── components/        # React components
├── package.json           # Node.js dependencies
└── README.md
```

## Setup Instructions

### Backend Setup (Flask API)

1. **Navigate to the backend directory:**
   ```powershell
   cd backend
   ```

2. **Create a Python virtual environment:**
   ```powershell
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   ```powershell
   venv\Scripts\Activate.ps1
   ```

4. **Install Python dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Run the Flask server:**
   ```powershell
   python app.py
   ```

   The API will be available at `http://localhost:5000`

### Frontend Setup (React)

1. **Navigate to the project root directory:**
   ```powershell
   cd ..
   ```

2. **Install Node.js dependencies:**
   ```powershell
   npm install
   ```

3. **Start the React development server:**
   ```powershell
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

## API Endpoints

The Flask backend provides the following REST API endpoints:

### GET /api/todos
- **Description:** Get all todos
- **Response:** Array of todo objects

### POST /api/todos
- **Description:** Create a new todo
- **Request Body:** 
  ```json
  {
    "todo": "Todo text",
    "isDone": false
  }
  ```
- **Response:** Created todo object

### PUT /api/todos/{id}
- **Description:** Update a specific todo
- **Request Body:** 
  ```json
  {
    "todo": "Updated text",
    "isDone": true
  }
  ```
- **Response:** Updated todo object

### DELETE /api/todos/{id}
- **Description:** Delete a specific todo
- **Response:** Deleted todo object

### PATCH /api/todos/{id}/toggle
- **Description:** Toggle the completion status of a todo
- **Response:** Updated todo object

### GET /api/health
- **Description:** Health check endpoint
- **Response:** 
  ```json
  {
    "status": "healthy",
    "timestamp": "2025-08-23T..."
  }
  ```

## Data Model

```typescript
interface Todo {
  id: number;
  todo: string;
  isDone: boolean;
}
```

## Running Both Servers

You need to run both the Flask backend and React frontend:

1. **Terminal 1 - Backend:**
   ```powershell
   cd backend
   venv\Scripts\Activate.ps1
   python app.py
   ```

2. **Terminal 2 - Frontend:**
   ```powershell
   npm run dev
   ```

## CORS Configuration

The Flask backend is configured with CORS to allow requests from the React frontend running on a different port.

## Data Persistence

Todos are persisted in a `todos.json` file in the backend directory. This file is automatically created and updated when you add, edit, or delete todos.

## Error Handling

- The frontend displays error messages when API requests fail
- Loading states are shown during API operations
- The backend returns appropriate HTTP status codes and error messages

## Development Notes

- The frontend automatically loads todos when the component mounts
- All CRUD operations are performed through the REST API
- The UI is disabled during loading states to prevent concurrent operations
- Error boundaries and try-catch blocks handle potential failures gracefully
