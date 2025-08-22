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
    <div className="App p-7 bg-indigo-50 rounded-xl font-serif">
      <span className='title text-xl'> To Do List </span>
      <InputField todo={todo} setTodo={setTodo} handleAdd={handleAdd}/>
      {<Filter filter={filter} setFilter={setFilter}/>}
      {<TodoList todos={filteredTodos()} setTodos={setTodos}/>}
    </div>
  )
}

export default App
