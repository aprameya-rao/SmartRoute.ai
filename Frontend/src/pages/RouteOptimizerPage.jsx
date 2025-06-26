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
    setRouteResult(null);

    try {
      // --- IMPORTANT: Prepare data types for backend ---
      const dataToSend = {
        ...formData,
        current_charge_percent: parseInt(formData.current_charge_percent, 10), // Convert to integer
        range_full_charge: parseFloat(formData.range_full_charge),           // Convert to float
      };

      // --- IMPORTANT: Correct the API endpoint URL ---
      const response = await fetch(`${API_BASE_URL}/api/v1/optimize-route`, { // ADDED `/api/v1`
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataToSend), // Use the prepared dataToSend
      });

      if (!response.ok) {
        let errorDetail = "Failed to optimize route. Please try again.";
        try {
          const errorData = await response.json();
          // Backend 422 errors usually have a 'detail' array
          if (response.status === 422 && Array.isArray(errorData.detail)) {
              errorDetail = errorData.detail.map(err => `${err.loc.join('.')} - ${err.msg}`).join('; ');
          } else {
              errorDetail = errorData.detail || JSON.stringify(errorData) || errorDetail;
          }
        } catch (jsonError) {
          // If response is not JSON, use generic message
          // The issue is likely here. Ensure the backticks are standard.
          errorDetail = `HTTP error! status: ${response.status}`; // THIS LINE IS THE FIX TARGET
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
          <MapDisplay routeData={routeResult} />
        </section>
      </div>
    </div>
  );
}

export default RouteOptimizerPage;