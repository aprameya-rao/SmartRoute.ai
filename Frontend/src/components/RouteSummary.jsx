import React from 'react';
import './RouteSummary.css';

function RouteSummary({ data }) {
  if (!data) return null;

  return (
    <div className="route-summary">
      <h2>Optimized Route Details</h2>
      <p><strong>Total Distance:</strong> {data.totalDistance}</p>
      <p><strong>Estimated Travel Time:</strong> {data.estimatedTime}</p>

      <h3>Charging Stops:</h3>
      {data.chargingStops && data.chargingStops.length > 0 ? (
        <ul>
          {data.chargingStops.map((stop, index) => (
            <li key={index}>
              <strong>{stop.name}</strong> ({stop.type}, {stop.power})<br/>
              <em>Location:</em> {stop.location}<br/>
              <em>Estimated Charge Time:</em> {stop.chargeTime}<br/>
              <em>Estimated Cost:</em> {stop.cost}
            </li>
          ))}
        </ul>
      ) : (
        <p>No charging stops required for this route.</p>
      )}
    </div>
  );
}

export default RouteSummary;