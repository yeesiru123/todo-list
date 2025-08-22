import React, { useState } from "react";

interface Props {
  filter: "all" | "active" | "completed";
  setFilter: React.Dispatch<
    React.SetStateAction<"all" | "active" | "completed">
  >;
}

const Filter: React.FC<Props> = ({ filter, setFilter }) => {
  return (
    <div className="gap-3 flex place-content-center mt-3">
      <button
        className={`rounded-full p-2 border-1 border-indigo-100 text-indigo-300 ${
          filter === "all" ? "bg-indigo-300 text-white" : ""
        }`}
        onClick={() => setFilter("all")}
      >
        {" "}
        All{" "}
      </button>

      <button
        className={`rounded-full p-2 border-1 border-indigo-100 text-indigo-300 ${
          filter === "active" ? "bg-indigo-300 text-white" : ""
        }`}
        onClick={() => setFilter("active")}
      >
        {" "}
        Active{" "}
      </button>
      
      <button
        className={`rounded-full p-2 border-1 border-indigo-100 text-indigo-300 ${
          filter === "completed" ? "bg-indigo-300 text-white" : ""
        }`}
        onClick={() => setFilter("completed")}
      >
        {" "}
        Completed{" "}
      </button>
    </div>
  );
};

export default Filter;
