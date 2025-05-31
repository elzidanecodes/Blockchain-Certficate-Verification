import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Home from "./pages/Home";
import Generate from "./pages/Generate";
import Validation from "./pages/Validation";

function App() {
  return (
    <Router>
      <Route path="/verify/:certificate_id" element={<Validation />} />
      <div className="flex">
        <Sidebar />
        <div className="flex-1 bg-default h-full dark:bg-gray-900 overflow-y-auto select-none cursor-default">
          <Routes>
            <Route path="/" element={<Navigate to="/home" />} />
            <Route path="/home" element={<Home />} />
            <Route path="/generate" element={<Generate />} />
            <Route path="/validation" element={<Validation />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
