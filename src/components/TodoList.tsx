import React from "react";
import { Todo } from "../model";
import SingleTodo from "./SingleTodo";

interface Props {
  todos: Todo[];
  setTodos: React.Dispatch<React.SetStateAction<Todo[]>>;
  token: string;
}
const TodoList: React.FC<Props> = ({ todos, setTodos, token }) => {
  return (
    <div className="">
      {todos.map((todo) => (
        <SingleTodo
          todo={todo}
          key={todo.id}
          todos={todos}
          setTodos={setTodos}
          token={token}
        />
      ))}
    </div>
  );
};

export default TodoList;
