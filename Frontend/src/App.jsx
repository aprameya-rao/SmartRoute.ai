import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header.jsx'; 
import Footer from './components/Footer.jsx'; 
import RouteOptimizerPage from './pages/RouteOptimizerPage.jsx'; 
import BatteryDisposalPage from './pages/BatteryDisposalPage.jsx'; 
import './App.css'; 
import HomePage from './pages/HomePage.jsx';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Header />

        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/route-optimizer" element={<RouteOptimizerPage />} />
            <Route path="/battery-disposal" element={<BatteryDisposalPage />} />
          </Routes>
        </main>

        <Footer />
      </div>
    </Router>
  );
}

export default App;