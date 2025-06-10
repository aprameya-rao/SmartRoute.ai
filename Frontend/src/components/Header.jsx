import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

function Header() {
  return (
    <header className="header">
      <div className="logo">
        <Link to="/">SmartRoute.ai </Link>
      </div>
      <nav className="nav-links">
        <ul>
          <li><Link to="/">Route Optimizer</Link></li>
          <li><Link to="/battery-disposal">Battery Disposal</Link></li>
        </ul>
      </nav>
    </header>
  );
}

export default Header;