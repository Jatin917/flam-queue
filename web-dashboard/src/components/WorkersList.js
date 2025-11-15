import React from 'react';
import './WorkersList.css';

function WorkersList({ workers }) {
  if (!workers || workers.length === 0) {
    return (
      <div className="workers-list">
        <h3>Workers</h3>
        <div className="empty-state">No active workers</div>
      </div>
    );
  }

  return (
    <div className="workers-list">
      <h3>Active Workers ({workers.length})</h3>
      <div className="workers-grid">
        {workers.map((worker, index) => (
          <div key={index} className="worker-card">
            <div className="worker-header">
              <span className="worker-id">Worker {worker.worker_id || 'N/A'}</span>
              <span className="worker-status">🟢 Active</span>
            </div>
            <div className="worker-details">
              <div className="worker-detail">
                <span className="detail-label">PID:</span>
                <span className="detail-value">{worker.pid || 'N/A'}</span>
              </div>
              <div className="worker-detail">
                <span className="detail-label">Started:</span>
                <span className="detail-value">
                  {worker.started_at 
                    ? new Date(worker.started_at).toLocaleString()
                    : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default WorkersList;

