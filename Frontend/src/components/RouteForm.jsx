import React, { useState } from 'react';
import './RouteForm.css';

function RouteForm({ onSubmit, loading }) {
  const [makeModel, setMakeModel] = useState('');
  const [range, setRange] = useState('');
  const [currentCharge, setCurrentCharge] = useState('');
  const [startLocation, setStartLocation] = useState('');
  const [destination, setDestination] = useState('');
  const [preferredCharger, setPreferredCharger] = useState('any');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      makeModel,
      range: parseFloat(range),
      currentCharge: parseFloat(currentCharge),
      startLocation,
      destination,
      preferredCharger,
    });
  };

  return (
    <form className="route-form" onSubmit={handleSubmit}>
      <h2>Plan Your Journey</h2>
      <div className="form-group">
        <label htmlFor="makeModel">Vehicle Make & Model:</label>
        <input
          type="text"
          id="makeModel"
          value={makeModel}
          onChange={(e) => setMakeModel(e.target.value)}
          placeholder="e.g., Tata Nexon EV Max"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="range">Full Charge Range (km):</label>
        <input
          type="number"
          id="range"
          value={range}
          onChange={(e) => setRange(e.target.value)}
          placeholder="e.g., 453"
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
          <option value="any">Any</option>
          <option value="level2">Level 2 AC</option>
          <option value="dc_fast">DC Fast Charge</option>
        </select>
      </div>
      <button type="submit" disabled={loading}>
        {loading ? 'Optimizing...' : 'Optimize Route'}
      </button>
    </form>
  );
}

export default RouteForm;