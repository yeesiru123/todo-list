import React, { useEffect } from "react";
import { Todo } from "../model";
import { MdEdit, MdDelete, MdDone } from "react-icons/md";
import { useState } from "react";
import { useRef } from "react";
import { FaRegCheckCircle, FaCheckCircle } from "react-icons/fa";

// Props type for SingleTodo component
type Props = {
  todo: Todo; // The todo item to display
  todos: Todo[]; // The list of all todos
  setTodos: React.Dispatch<React.SetStateAction<Todo[]>>; // Function to update todos
};

// SingleTodo component displays and manages a single todo item
const SingleTodo = ({ todo, todos, setTodos }: Props) => {
  // State to track if the todo is in edit mode
  const [edit, setEdit] = useState<boolean>(false);
  // State to store the edited todo text
  const [editTodo, setEditTodo] = useState<string>(todo.todo);

  // Toggle the isDone status of the todo
  const handleDone = (id: number) => {
    setTodos(
      todos.map(
        (todo) => (todo.id === id ? { ...todo, isDone: !todo.isDone } : todo)
        //...todo mean copy all properties to newTodo but set new isDone value
      )
    );
  };

  // Delete the todo from the list
  const handleDelete = (id: number) => {
    setTodos(todos.filter((todo) => todo.id !== id));
  };

  // Handle editing the todo text
  const handleEdit = (e: React.FormEvent, id: number) => {
    e.preventDefault();
    setTodos(
      todos.map((todo) => (todo.id === id ? { ...todo, todo: editTodo } : todo))
    ); // Update the todo with the new text
    setEdit(false); // Exit edit mode
  };

  // Ref for the input element to focus it when editing
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus the input when entering edit mode
  useEffect(() => {
    inputRef.current?.focus();
  }, [edit]);

  return (
    // Form for editing the todo (pressing Enter saves changes)
    <form
      className="flex items-center my-3 place-content-between border-b-1 border-b-indigo-200 p-2"
      onSubmit={(e) => (edit ? handleEdit(e, todo.id) : e.preventDefault())}
    >
      {todo.isDone ? (
        <span onClick={() => handleDone(todo.id)}>
          <FaCheckCircle className="w-5 h-5 text-indigo-300"/>
        </span>
      ) : (
        <span onClick={() => handleDone(todo.id)}>
          <FaRegCheckCircle className="w-5 h-5 text-indigo-300"/>
        </span>
      )}

      {/* If in edit mode, show input; else show todo text */}
      {edit ? (
        <input
          ref={inputRef}
          value={editTodo}
          onChange={(e) => setEditTodo(e.target.value)}
          className="text-xl w-4/5 border-1 rounded-full pl-2"
        />
      ) : todo.isDone ? (
        <s className="text-xl w-4/5 text-indigo-300">{todo.todo}</s>
      ) : (
        <span className="text-xl w-4/5 text-indigo-300">{todo.todo}</span>
      )}

      {/* Action icons: Edit, Delete, Done */}
      <div className="flex gap-2">
        {/* Edit icon: only enables edit if not already editing and not done */}
        <span
          onClick={() => {
            if (!edit && !todo.isDone) {
              setEdit(!edit);
            }
          }}
        >
          <MdEdit className="w-5 h-5 text-indigo-300" />
        </span>
        {/* Delete icon: removes the todo */}
        <span className="w-5 h-5" onClick={() => handleDelete(todo.id)}>
          <MdDelete className="w-5 h-5 text-indigo-300" />
        </span>
      </div>
    </form>
  );
};

export default SingleTodo;
