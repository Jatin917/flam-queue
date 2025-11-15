import React, { useState, useEffect } from 'react';
import './Dashboard.css';
import StatsCards from './StatsCards';
import WorkersList from './WorkersList';
import JobsList from './JobsList';

function Dashboard({ status, onRefresh }) {
  const [jobs, setJobs] = useState([]);              // Always an array
  const [selectedState, setSelectedState] = useState('all');
  const [isRefreshing, setIsRefreshing] = useState(false);

  const summary = status?.summary || {};
  const workers = status?.workers || [];

  // Fetch all jobs or jobs by state
  const fetchJobs = async (state = selectedState) => {
    try {
      setIsRefreshing(true);

      const endpoint =
        state === 'all'
          ? 'http://localhost:5000/api/jobs'
          : `http://localhost:5000/api/jobs/${state}`;

      const response = await fetch(endpoint);
      const data = await response.json();

      if (data && data.jobs) {
        setJobs(data.jobs);
      } else {
        setJobs([]);
      }
    } catch (err) {
      console.error("Error fetching jobs:", err);
      // Do not block UI or force loading screen
    } finally {
      setIsRefreshing(false);
    }
  };

  // Initial + repeated fetching
  useEffect(() => {
    fetchJobs(selectedState);

    const interval = setInterval(() => {
      fetchJobs(selectedState);
    }, 5000);

    return () => clearInterval(interval);
  }, [selectedState]);

  return (
    <div className="dashboard">
      <div className="dashboard-content">

        {/* Header */}
        <div className="dashboard-header">
          <h2>Queue Overview</h2>
          <button
            onClick={() => fetchJobs(selectedState)}
            className={`refresh-btn ${isRefreshing ? "refreshing" : ""}`}
            disabled={isRefreshing}
          >
            {isRefreshing ? "🔄 Refreshing..." : "🔄 Refresh"}
          </button>
        </div>

        {/* Stats Summary */}
        <StatsCards summary={summary} workerCount={workers.length} />

        <div className="dashboard-grid">

          {/* Workers */}
          <WorkersList workers={workers} />

          {/* Jobs Section */}
          <div className="jobs-section">
            <div className="section-header">
              <h3>Jobs</h3>

              <select
                value={selectedState}
                onChange={(e) => setSelectedState(e.target.value)}
                className="state-filter"
              >
                <option value="all">All Jobs</option>
                <option value="pending">Pending</option>
                <option value="processing">Processing</option>
                <option value="completed">Completed</option>
                <option value="dead">Dead</option>
                <option value="delayed">Delayed</option>
              </select>
            </div>

            {/* Jobs Table */}
            <JobsList jobs={jobs} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
