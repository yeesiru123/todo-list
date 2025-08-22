import { useState } from 'react'
import './App.css'
import InputField from './components/InputField'
import TodoList from './components/TodoList'
import Filter from './components/Filter'
import { Todo } from './model'


//React.FC = functional component
const App : React.FC = () => {

  //set initial value
  const [todo, setTodo] = useState <string> ("");
  const [todos, setTodos] = useState <Todo[]> ([]);
  const [filter, setFilter] = useState<"all" | "active" | "completed">("all");

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

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();

    if(todo){
      setTodos([...todos, {id:Date.now(), todo, isDone:false}]);
      setTodo("")
    }
  };

  console.log(todos);

  return (
    <div className="bg-indigo-50 grid py-4 min-h-screen font-serif">
      <div className='bg-white flex place-self-center w-3/5 md:max-w-3xl flex-col p-7 min-h-3/4 rounded-xl'>
        <span className='text-center my-6 text-3xl font-semibold text-indigo-300'> To Do List </span>
        <InputField todo={todo} setTodo={setTodo} handleAdd={handleAdd}/>
        {<Filter filter={filter} setFilter={setFilter}/>}
        {<TodoList todos={filteredTodos()} setTodos={setTodos}/>}
      </div>
    </div>
  )
}

export default App
