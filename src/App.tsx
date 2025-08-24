import { useState, useEffect } from 'react'
import './App.css'
import InputField from './components/InputField'
import TodoList from './components/TodoList'
import Filter from './components/Filter'
import { Todo } from './model'
import { TodoAPI } from './api'


//React.FC = functional component
const App : React.FC = () => {

  //set initial value
  const [todo, setTodo] = useState <string> ("");
  const [todos, setTodos] = useState <Todo[]> ([]);
  const [filter, setFilter] = useState<"all" | "active" | "completed">("all");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load todos from API on component mount
  useEffect(() => {
    const loadTodos = async () => {
      try {
        setLoading(true);
        setError(null);
        const fetchedTodos = await TodoAPI.getAllTodos();
        setTodos(fetchedTodos);
      } catch (err) {
        setError('Failed to load todos. Please make sure the backend is running.');
        console.error('Error loading todos:', err);
      } finally {
        setLoading(false);
      }
    };

    loadTodos();
  }, []);

  const filteredTodos = () => {
    switch (filter) {
      case 'all':
        return todos;
      case 'active':
        return todos.filter(todo => !todo.isDone);
      case 'completed':
        return todos.filter(todo => todo.isDone);
      default:
        return todos;
    }
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();

    if(todo.trim()){
      try {
        setLoading(true);
        setError(null);
        const newTodo = await TodoAPI.createTodo(todo.trim());
        setTodos([...todos, newTodo]);
        setTodo("");
      } catch (err) {
        setError('Failed to add todo. Please try again.');
        console.error('Error adding todo:', err);
      } finally {
        setLoading(false);
      }
    }
  };

  console.log(todos);

  return (
    <div className="bg-indigo-50 grid py-4 min-h-screen font-serif">
      <div className='bg-white flex place-self-center w-3/5 md:max-w-3xl flex-col p-7 min-h-3/4 rounded-xl'>
        <span className='text-center my-6 text-3xl font-semibold text-indigo-300'> To Do List </span>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <InputField todo={todo} setTodo={setTodo} handleAdd={handleAdd} disabled={loading}/>
        {<Filter filter={filter} setFilter={setFilter}/>}
        
        {loading ? (
          <div className="text-center py-4">
            <span className="text-indigo-500">Loading...</span>
          </div>
        ) : (
          <TodoList todos={filteredTodos()} setTodos={setTodos}/>
        )}
      </div>
    </div>
  )
}

export default App
