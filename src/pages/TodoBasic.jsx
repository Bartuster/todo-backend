import { useState, useContext, useRef } from "react";
import { TodoContext } from "../context/TodoContext";

export default function TodoBasic() {
  const { todos, addTodo, removeTodo } = useContext(TodoContext);
  const [input, setInput] = useState("");
  const inputRef = useRef();

  const handleAdd = () => {
    if (input.trim() === "") return;
    addTodo(input);
    setInput("");
    inputRef.current.focus();
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-start p-8">
      <h1 className="text-2xl font-bold mb-4 text-black">Todo List</h1>
      <div className="flex mb-4">
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="p-2 border border-gray-400 rounded-l"
          placeholder="Dodaj zadanie..."
        />
        <button
          onClick={handleAdd}
          className="p-2 bg-black text-white rounded-r hover:bg-gray-800"
        >
          Dodaj
        </button>
      </div>
      <ul className="w-full max-w-md">
        {todos.map((todo) => (
          <li
            key={todo.id}
            className="flex justify-between items-center mb-2 p-2 bg-white rounded shadow"
          >
            <span className="text-black">{todo.text}</span>
            <button
              onClick={() => removeTodo(todo.id)}
              className="text-red-500 hover:text-red-700"
            >
              Usuń
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
