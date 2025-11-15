import React from 'react';
import './StatsCards.css';

function StatsCards({ summary, workerCount }) {
  const stats = [
    {
      label: 'Pending',
      value: summary.pending || summary.PENDING || 0,
      color: '#ff9800',
      icon: '⏳'
    },
    {
      label: 'Processing',
      value: summary.processing || summary.PROCESSING || 0,
      color: '#2196f3',
      icon: '⚙️'
    },
    {
      label: 'Completed',
      value: summary.completed || summary.COMPLETED || 0,
      color: '#4caf50',
      icon: '✅'
    },
    {
      label: 'Dead',
      value: summary.dead || summary.DEAD || 0,
      color: '#f44336',
      icon: '💀'
    },
    {
      label: 'Active Workers',
      value: workerCount,
      color: '#9c27b0',
      icon: '👷'
    }
  ];

  return (
    <div className="stats-cards">
      {stats.map((stat, index) => (
        <div key={index} className="stat-card" style={{ borderTopColor: stat.color }}>
          <div className="stat-icon">{stat.icon}</div>
          <div className="stat-content">
            <div className="stat-value">{stat.value}</div>
            <div className="stat-label">{stat.label}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default StatsCards;

