import React, { useEffect } from "react";
import { Todo } from "../model";
import { MdEdit, MdDelete, MdDone } from "react-icons/md";
import { useState } from "react";
import { useRef } from "react";

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
      todos.map((todo) =>
        todo.id === id ? { ...todo, isDone: !todo.isDone } : todo
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
      className="flex w-3xs flex-wrap"
      onSubmit={(e) => (edit ? handleEdit(e, todo.id) : e.preventDefault())}
    >
      {/* If in edit mode, show input; else show todo text (strikethrough if done) */}
      {edit ? (
        <input
          ref={inputRef}
          value={editTodo}
          onChange={(e) => setEditTodo(e.target.value)}
        />
      ) : todo.isDone ? (
        <s className="w-1/2">{todo.todo}</s>
      ) : (
        <span className="w-1/2">{todo.todo}</span>
      )}

      {/* Action icons: Edit, Delete, Done */}
      <div className="flex">
        {/* Edit icon: only enables edit if not already editing and not done */}
        <span
          className="icon"
          onClick={() => {
            if (!edit && !todo.isDone) {
              setEdit(!edit);
            }
          }}
        >
          <MdEdit />
        </span>
        {/* Delete icon: removes the todo */}
        <span className="icon" onClick={() => handleDelete(todo.id)}>
          <MdDelete />
        </span>
        {/* Done icon: toggles the isDone status */}
        <span className="icon" onClick={() => handleDone(todo.id)}>
          <MdDone />
        </span>
      </div>
    </form>
  );
};

export default SingleTodo;
