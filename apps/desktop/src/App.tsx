import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

const API_BASE = "http://127.0.0.1:8765";

function App() {
  const [status, setStatus] = useState("stopped");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`${API_BASE}/status`);
        setStatus(res.data.status);
      } catch (err) {
        console.error("API is not running.");
      }
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const toggleEngine = async () => {
    setLoading(true);
    try {
      if (status === "running") {
        await axios.post(`${API_BASE}/stop`);
        setStatus("stopped");
      } else {
        await axios.post(`${API_BASE}/start`, {
          target_wav: "target.wav",
          device: "cpu"
        });
        setStatus("running");
      }
    } catch (err) {
      alert("Failed to toggle engine. Check if backend is running.");
    }
    setLoading(false);
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>SYNORA // Live Studio</h1>
        <div className={`status-badge ${status}`}>
          {status.toUpperCase()}
        </div>
      </header>

      <main className="studio-console">
        <div className="panel input-panel">
          <h2>Voice Engine</h2>
          <div className="control-group">
            <label>Target Voice</label>
            <div className="dropdown">target.wav</div>
          </div>
          <div className="control-group">
            <label>Processing Device</label>
            <div className="dropdown">CPU (Ryzen 7 8745HS)</div>
          </div>
          
          <button 
            className={`action-button ${status === "running" ? "stop" : "start"}`}
            onClick={toggleEngine}
            disabled={loading}
          >
            {loading ? "PROCESSING..." : status === "running" ? "STOP ENGINE" : "START ENGINE"}
          </button>
        </div>

        <div className="panel monitor-panel">
          <h2>Telemetry</h2>
          <div className="metrics-grid">
            <div className="metric">
              <span>Engine Status</span>
              <strong>{status === "running" ? "Active" : "Idle"}</strong>
            </div>
            <div className="metric">
              <span>Estimated Latency</span>
              <strong>~130ms</strong>
            </div>
            <div className="metric">
              <span>Model</span>
              <strong>MeanVC2 (40ms)</strong>
            </div>
          </div>
          <div className="warning-box">
            ⚠️ Ensure headphones are connected to prevent audio feedback loops.
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
