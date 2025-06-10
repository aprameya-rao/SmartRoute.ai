import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header.jsx'; 
import Footer from './components/Footer.jsx'; 
import RouteOptimizerPage from './pages/RouteOptimizerPage.jsx'; 
import BatteryDisposalPage from './pages/BatteryDisposalPage.jsx'; 
import './App.css'; 

function App() {
  return (
    <Router>
      <div className="app-container">
        <Header />

        <main className="main-content">
          <Routes>
            <Route path="/" element={<RouteOptimizerPage />} />
            <Route path="/battery-disposal" element={<BatteryDisposalPage />} />
          </Routes>
        </main>

        <Footer />
      </div>
    </Router>
  );
}

export default App;