import React, { useRef } from "react";

interface Props {
  todo: string;
  setTodo: React.Dispatch<React.SetStateAction<string>>;
  handleAdd: (e: React.FormEvent) => void;
  disabled?: boolean;
}

const InputField: React.FC<Props> = ({ todo, setTodo, handleAdd, disabled = false }) => {
  //useRef()= allow to persist values between renders, not cause re-render
  const inputRef = useRef<HTMLInputElement>(null);

  return (
    <form
      className="flex items-center rounded-full bg-indigo-50"
      onSubmit={(e) => {
        handleAdd(e);
        //inputRef.current?.blur();
      }}
    >
      <input
        ref={inputRef}
        type="input"
        value={todo}
        onChange={(e) => setTodo(e.target.value)}
        placeholder="Add a new task"
        disabled={disabled}
        className="bg-transparent border-0 outline-none flex-1 h-14 pl-6 pr-2 placeholder:text-slate-400 disabled:opacity-50"
      />
      <button 
        type="submit" 
        disabled={disabled}
        className="border-none rounded-full bg-indigo-200 w-32 h-14 text-white text-lg font-medium cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Add
      </button>
    </form>
  );
};

export default InputField;