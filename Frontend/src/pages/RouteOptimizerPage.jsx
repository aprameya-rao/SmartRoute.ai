import React, { useState } from 'react';
import RouteForm from '../components/RouteForm.jsx';
import MapDisplay from '../components/MapDisplay.jsx';
import RouteSummary from '../components/RouteSummary.jsx';
import { optimizeEvRoute } from '../services/evApi.js';
import './RouteOptimizerPage.css';

function RouteOptimizerPage() {
  const [routeResult, setRouteResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleOptimizeRoute = async (formData) => {
    setLoading(true);
    setError(null);
    setRouteResult(null);

    try {
      const backendResult = await optimizeEvRoute(formData);

      // Transform backendResult to match RouteSummary's expected props
      const formattedForSummary = {
        totalDistance: backendResult.summary.total_distance_km ? `${backendResult.summary.total_distance_km.toFixed(1)} km` : 'N/A',
        estimatedTime: backendResult.summary.total_duration_minutes ? 
                       `${Math.floor(backendResult.summary.total_duration_minutes / 60)}h ${Math.round(backendResult.summary.total_duration_minutes % 60)}m` : 'N/A',
        // Provide separate driving and charging times as requested
        totalDrivingTime: backendResult.summary.total_driving_minutes ? 
                          `${Math.floor(backendResult.summary.total_driving_minutes / 60)}h ${Math.round(backendResult.summary.total_driving_minutes % 60)}m` : 'N/A',
        totalChargingTime: backendResult.summary.total_charging_minutes ? 
                           `${Math.floor(backendResult.summary.total_charging_minutes / 60)}h ${Math.round(backendResult.summary.total_charging_minutes % 60)}m` : 'N/A',
        chargingStops: backendResult.charging_locations.map(stop => ({
          name: stop.name,
          type: stop.connection_types ? stop.connection_types.join(', ') : 'Unknown',
          power: stop.power_kw ? `${stop.power_kw} kW` : 'N/A',
          location: stop.address || 'Unknown Address',
          chargeTime: stop.recommended_charge_minutes ? `${stop.recommended_charge_minutes} mins` : 'N/A',
          cost: stop.usage_cost || (stop.is_free ? 'Free' : 'Not Specified')
        })),
        routeGeometry: backendResult.route_geometry // Pass geometry for map
      };

      setRouteResult(formattedForSummary);

    } catch (err) {
      console.error("Error optimizing route:", err);
      setError(err.message || "Failed to optimize route. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="route-optimizer-page">
      <h1>SmartRoute.ai </h1>
      <div className="optimizer-layout">
        <aside className="sidebar">
          <RouteForm onSubmit={handleOptimizeRoute} loading={loading} />
          {loading && <p>Optimizing route...</p>}
          {error && <p className="error-message">{error}</p>}
          {routeResult && <RouteSummary data={routeResult} />}
        </aside>
        <section className="map-section">
          <MapDisplay routeData={routeResult} />
        </section>
      </div>
    </div>
  );
}

export default RouteOptimizerPage;