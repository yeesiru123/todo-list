

# Todo List with Flask, ClickHouse, and React

A full-stack Todo List application with React frontend, Flask backend API, and ClickHouse as the database (via Docker). Optionally supports Keycloak authentication.

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
│   ├── docker-compose.yml  # ClickHouse Docker Compose config
├── src/
│   ├── api.ts             # API service layer
│   ├── App.tsx            # Main React component
│   ├── model.ts           # TypeScript interfaces
│   └── components/        # React components
├── package.json           # Node.js dependencies
└── README.md
```

## Setup Instructions



### Backend, Database & Event Streaming Setup (Flask API + ClickHouse + Kafka)

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```


2. **Start ClickHouse, Kafka, and Zookeeper with Docker Compose:**
   ```bash
   sudo docker compose up -d
   ```
   This will start ClickHouse (ports 18123/19000), Kafka (port 29092), and Zookeeper (port 22181).

3. **Install Python & pip:**
   ```bash
   sudo apt install python3 python3-pip python3-venv -y
   ```

4. **Create a Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```


5. **Install backend dependencies:**
   ```bash
   pip install -r requirements.txt
   ```


6. **Run Flask App:**
   ```bash
   python3 app.py
   ```
   The API will be available at `http://localhost:5000`

#### Kafka Integration

- Kafka and Zookeeper are started via Docker Compose.
- The backend uses the `kafka-python` library to produce events to the `todos-events` topic on every create, update, delete, and toggle action.
- You can consume these events from Kafka for analytics, logging, or microservices.

#### (Optional) Keycloak Authentication
If you use Keycloak for authentication, start it with Docker:
```bash
docker run -p 8080:8080 -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=admin quay.io/keycloak/keycloak:24.0.3 start-dev
```
Configure your realm, client, and users as needed.

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



## Data Persistence & Event Streaming

- Todos are persisted in ClickHouse, a high-performance columnar database, running in Docker.
- All todo changes (create, update, delete, toggle) are also sent as events to Kafka (`todos-events` topic).

## Error Handling

- The frontend displays error messages when API requests fail
- Loading states are shown during API operations
- The backend returns appropriate HTTP status codes and error messages

## Development Notes

- The frontend automatically loads todos when the component mounts
- All CRUD operations are performed through the REST API
- The UI is disabled during loading states to prevent concurrent operations
- Error boundaries and try-catch blocks handle potential failures gracefully