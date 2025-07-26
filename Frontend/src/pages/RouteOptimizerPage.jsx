import React, { useState } from 'react';
import RouteForm from '../components/RouteForm.jsx';
import MapDisplay from '../components/MapDisplay.jsx';
import RouteSummary from '../components/RouteSummary.jsx';
import './RouteOptimizerPage.css';

function RouteOptimizerPage() {
  const [routeResult, setRouteResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_BASE_URL = 'http://localhost:8000'; // Your FastAPI base URL

  const handleOptimizeRoute = async (formData) => {
    setLoading(true);
    setError(null);
    setRouteResult(null); // Clear previous result on new submission

    try {
      const dataToSend = formData;

      const response = await fetch(`${API_BASE_URL}/api/v1/optimize-route`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json', 
        },
        body: JSON.stringify(dataToSend),
      });

      if (!response.ok) {
        let errorDetail = "Failed to optimize route. Please try again.";
        try {
          const errorData = await response.json();
          if (response.status === 422 && Array.isArray(errorData.detail)) {
              errorDetail = errorData.detail.map(err => `${err.loc.join('.')} - ${err.msg}`).join('; ');
          } else {
              errorDetail = errorData.detail || JSON.stringify(errorData) || errorDetail;
          }
        } catch (jsonError) {
          errorDetail = `HTTP error! status: ${response.status}`;
        }
        throw new Error(errorDetail);
      }

      const formattedResultFromBackend = await response.json();
      setRouteResult(formattedResultFromBackend);

    } catch (err) {
      console.error("Error optimizing route:", err);
      if (err instanceof TypeError && err.message.includes('fetch')) {
        setError('Unable to connect to the backend server. Please ensure the server is running and accessible.');
      } else {
        setError(err.message || "Failed to optimize route. Please check your inputs.");
      }
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
          {/* --- IMPORTANT CHANGE: Add a key to MapDisplay --- */}
          {/* This key forces React to re-mount MapDisplay when routeResult changes between null and a value,
              or when a new route (with a different total distance) is received.
              This can help synchronize React's DOM management with Google Maps' direct DOM manipulation. */}
          <MapDisplay
            routeData={routeResult}
            key={routeResult ? `map-with-route-${routeResult.route_summary?.total_distance_km}` : 'map-no-route'}
          />
        </section>
      </div>
    </div>
  );
}

export default RouteOptimizerPage;
