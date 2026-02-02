// App.jsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./component/Navbar";
import Homepage from "./pages/Homepage";
import Documentation from "./pages/Documentation";
import ResearchInfo from "./pages/ResearchInfo";
import Footer from "./component/Footer";

function App() {
  return (
    <BrowserRouter>
      <Navbar />

      <Routes>
        <Route path="/" element={<Homepage />} />
        <Route path="/documentation" element={<Documentation />} />
        <Route path="/research-info" element={<ResearchInfo />} />
      </Routes>
      <Footer />
    </BrowserRouter>
  );
}

export default App;
