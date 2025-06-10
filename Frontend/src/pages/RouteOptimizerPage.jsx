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
      const result = await optimizeEvRoute(formData);
      setRouteResult(result);
    } catch (err) {
      console.error("Error optimizing route:", err);
      setError("Failed to optimize route. Please try again.");
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