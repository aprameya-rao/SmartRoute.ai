import React, { useEffect, useRef } from 'react';
import './MapDisplay.css';

function MapDisplay({ routeData }) {
  const mapContainerRef = useRef(null);

  useEffect(() => {
    if (mapContainerRef.current) {
      mapContainerRef.current.innerHTML = ''; 
      if (routeData) {
        console.log("MapDisplay received routeData:", routeData);
        mapContainerRef.current.innerHTML = `
          <p>Map will render route:</p>
          <p>Distance: ${routeData.totalDistance}</p>
          <p>Time: ${routeData.estimatedTime}</p>
          <p>Charging Stops: ${routeData.chargingStops.length}</p>
          <p><em>(Actual map integration with markers and polylines would go here)</em></p>
        `;
      } else {
        mapContainerRef.current.innerHTML = '<p class="map-placeholder-text">Enter details and optimize your route to see the map.</p>';
      }
    }
  }, [routeData]);

  return (
    <div className="map-container" ref={mapContainerRef}>
      {!routeData && (
        <p className="map-placeholder-text">Enter details and optimize your route to see the map.</p>
      )}
    </div>
  );
}

export default MapDisplay;