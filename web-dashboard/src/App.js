import React, { useState, useEffect } from "react";
import "./App.css";
import Dashboard from "./components/Dashboard";
import Header from "./components/Header";

// Default values shown instantly while real data loads
const DEFAULT_STATUS = {
  success: false,
  workers: 0,
  queued: 0,
  processing: 0,
  dead: 0,
  running: false,
};

function App() {
  const [status, setStatus] = useState(DEFAULT_STATUS);
  const [error, setError] = useState(null);

  // Fetch with timeout wrapper (prevents infinite waiting)
  const fetchWithTimeout = (url, timeout = 8000) => {
    return Promise.race([
      fetch(url),
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error("TIMEOUT")), timeout)
      ),
    ]);
  };

  // Fetch backend status without blocking UI
  const fetchStatus = async () => {
    try {
      const response = await fetchWithTimeout(
        "http://localhost:5000/api/status",
        8000
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      // Merge with previous state (only update values)
      setStatus((prev) => ({
        ...prev,
        ...data,
        success: true,
      }));

      setError(null); // clear error on successful fetch
    } catch (err) {
      console.error("Error fetching status:", err);

      let msg = "Cannot reach backend at http://localhost:5000";

      if (err.message === "TIMEOUT") {
        msg = "Backend request timed out. Server may be too slow or offline.";
      }

      setError(msg);

      // We DO NOT clear or reset status to prevent UI flicker/stuck screens
    }
  };

  // Initial + continuous refreshing
  useEffect(() => {
    fetchStatus(); // data immediately

    const interval = setInterval(() => {
      fetchStatus(); // Refresh every 2 seconds
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="App">
      <Header />
      <Dashboard status={status} onRefresh={fetchStatus} />

      {/* Non-blocking error message */}
      {error && <div className="error">{error}</div>}
    </div>
  );
}

export default App;
