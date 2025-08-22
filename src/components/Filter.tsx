import React, { useState } from "react";


interface Props{
    filter: "all" | "active" | "completed";
    setFilter: React.Dispatch<React.SetStateAction<"all" | "active" | "completed">>;
}

const Filter: React.FC <Props> = ( {filter, setFilter} ) => {
  return (
    <div className="">
      <button onClick={()=>setFilter("all")} > All </button>
      <button onClick={()=>setFilter("active")}> Active </button>
      <button onClick={()=>setFilter("completed")}> Completed </button>
    </div>
  );
};

export default Filter;
