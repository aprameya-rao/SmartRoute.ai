import React, { useState } from 'react';
import './RouteForm.css';

function RouteForm({ onSubmit, loading }) {
  const [evType, setEvType] = useState('');
  const [currentCharge, setCurrentCharge] = useState('');
  const [startLocation, setStartLocation] = useState('');
  const [destination, setDestination] = useState('');
  const [preferredCharger, setPreferredCharger] = useState('any');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ev_type: evType,
      current_charge_percent: parseFloat(currentCharge),
      start_location: startLocation,
      end_location: destination,
      charging_preference: preferredCharger === 'fast' ? 'fast' : 'standard', 
    });
  };

  return (
    <form className="route-form" onSubmit={handleSubmit}>
      <h2>Plan Your Journey</h2>
      <div className="form-group">
        <label htmlFor="evType">Vehicle Make & Model:</label>
        <input
          type="text"
          id="evType"
          value={evType}
          onChange={(e) => setEvType(e.target.value)}
          placeholder="e.g., Tata Nexon EV Max"
          required
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="currentCharge">Current Battery (%):</label>
        <input
          type="number"
          id="currentCharge"
          value={currentCharge}
          onChange={(e) => setCurrentCharge(e.target.value)}
          min="0"
          max="100"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="startLocation">Start Location:</label>
        <input
          type="text"
          id="startLocation"
          value={startLocation}
          onChange={(e) => setStartLocation(e.target.value)}
          placeholder="e.g., Bengaluru"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="destination">Destination:</label>
        <input
          type="text"
          id="destination"
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          placeholder="e.g., Chennai"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="chargerType">Preferred Charger Type:</label>
        <select
          id="chargerType"
          value={preferredCharger}
          onChange={(e) => setPreferredCharger(e.target.value)}
        >
          <option value="standard">Standard (Any Charger)</option>
          <option value="fast">Fast Charge</option>
        </select>
      </div>
      <button type="submit" disabled={loading}>
        {loading ? 'Optimizing...' : 'Optimize Route'}
      </button>
    </form>
  );
}

export default RouteForm;