import React from 'react';
import './JobsList.css';

function JobsList({ jobs, loading }) {
  // Only show loading on initial load, not on refreshes
  if (loading && (!jobs || jobs.length === 0)) {
    return <div className="loading-jobs">Loading jobs...</div>;
  }

  if (!jobs || jobs.length === 0) {
    return <div className="empty-jobs">No jobs found</div>;
  }

  const getStateColor = (state) => {
    const colors = {
      'pending': '#ff9800',
      'PENDING': '#ff9800',
      'processing': '#2196f3',
      'PROCESSING': '#2196f3',
      'completed': '#4caf50',
      'COMPLETED': '#4caf50',
      'dead': '#f44336',
      'DEAD': '#f44336',
      'delayed': '#9c27b0',
      'DELAYED': '#9c27b0'
    };
    return colors[state] || '#666';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return dateString;
    }
  };

  return (
    <div className="jobs-list">
      <div className="jobs-table">
        <div className="jobs-header">
          <div className="job-col-id">Job ID</div>
          <div className="job-col-command">Command</div>
          <div className="job-col-state">State</div>
          <div className="job-col-attempts">Attempts</div>
          <div className="job-col-created">Created</div>
        </div>
        <div className="jobs-body">
          {jobs.map((job, index) => (
            <div key={job.id || index} className="job-row">
              <div className="job-col-id" title={job.id}>
                {job.id ? job.id.substring(0, 8) + '...' : 'N/A'}
              </div>
              <div className="job-col-command" title={job.command}>
                {job.command || 'N/A'}
              </div>
              <div className="job-col-state">
                <span 
                  className="state-badge"
                  style={{ backgroundColor: getStateColor(job.state) }}
                >
                  {job.state || 'N/A'}
                </span>
              </div>
              <div className="job-col-attempts">
                {job.attempts || 0} / {job.max_retries || 'N/A'}
              </div>
              <div className="job-col-created">
                {formatDate(job.created_at)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default JobsList;

