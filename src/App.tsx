import { useState } from 'react'
import './App.css'
import InputField from './components/InputField'
import TodoList from './components/TodoList'
import { Todo } from './model'


//React.FC = functional component
const App : React.FC = () => {

  const [todo, setTodo] = useState <string> ("");
  const [todos, setTodos] = useState <Todo[]> ([]);

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
      {<TodoList todos={todos} setTodos={setTodos}/>}
    </div>
  )
}

export default App
