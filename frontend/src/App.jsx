import { BrowserRouter, Routes, Route } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import ImageDetection from "./pages/ImageDetection";
import VideoDetection from "./pages/VideoDetection";
import LiveMonitoring from "./pages/LiveMonitoring";
import DetectionHistory from "./pages/DetectionHistory";
import SessionDetails from "./pages/SessionDetails";

function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-slate-950 text-slate-200">
        <Sidebar />

        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/image-detection" element={<ImageDetection />} />
            <Route path="/video-detection" element={<VideoDetection />} />
            <Route path="/live-monitoring" element={<LiveMonitoring />} />
            <Route path="/history" element={<DetectionHistory />} />
            <Route path="/history/:id" element={<SessionDetails />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;