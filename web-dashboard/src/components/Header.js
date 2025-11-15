import React from 'react';
import './Header.css';

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <h1>QueueCTL Dashboard</h1>
        <span className="header-subtitle">Job Queue Monitoring</span>
      </div>
    </header>
  );
}

export default Header;

