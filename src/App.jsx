import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import PageOne from "./pages/PageOne";
import PageTwo from "./pages/PageTwo";
import TodoBasic from "./pages/TodoBasic";
import { TodoProvider } from "./context/TodoContext";

export default function App() {
  return (
    <TodoProvider>
      <Router>
        <div className="min-h-screen bg-gray-200">
          <nav className="p-4 bg-gray-300 flex justify-center gap-4">
            <Link to="/" className="text-black font-bold">Page One</Link>
            <Link to="/pagetwo" className="text-black font-bold">Page Two</Link>
            <Link to="/todo" className="text-black font-bold">Todo</Link>
          </nav>
          <Routes>
            <Route path="/" element={<PageOne />} />
            <Route path="/pagetwo" element={<PageTwo />} />
            <Route path="/todo" element={<TodoBasic />} />
          </Routes>
        </div>
      </Router>
    </TodoProvider>
  );
}
