import React, { useEffect, useRef, useState } from 'react';
import './MapDisplay.css'; // Ensure this CSS defines a height for .map-container

function MapDisplay({ routeData }) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const polylineRef = useRef(null);
  const startMarkerRef = useRef(null);
  const endMarkerRef = useRef(null);
  const chargingMarkersRef = useRef([]); // Ref to store an array of Google Maps Marker objects for charging stations

  // State to track if Google Maps API is available
  const [isGoogleMapsApiReady, setIsGoogleMapsApiReady] = useState(false);
  // State to track if map instance has been successfully created
  const [hasMapBeenCreated, setHasMapBeenCreated] = useState(false);
  // State for the message shown BEFORE the map is created or when no route data is present
  const [initialMapMessage, setInitialMapMessage] = useState("Loading map...");

  // Effect to check if Google Maps API is loaded (runs once on mount)
  useEffect(() => {
    if (window.google && window.google.maps) {
      setIsGoogleMapsApiReady(true);
      return;
    }

    // Polling until the Google Maps script is available
    const checkApiInterval = setInterval(() => {
      if (window.google && window.google.maps) {
        setIsGoogleMapsApiReady(true);
        clearInterval(checkApiInterval);
      } else {
        setInitialMapMessage("Loading map API..."); // Keep updating message if not ready
      }
    }, 100);

    return () => clearInterval(checkApiInterval); // Cleanup interval on unmount
  }, []); // Empty dependency array means this runs only once on mount

  // Main effect for map initialization and route rendering
  useEffect(() => {
    // 1. Initial checks: ensure API is ready and container exists
    if (!isGoogleMapsApiReady || !mapContainerRef.current) {
        return; // Exit early if prerequisites are not met
    }

    // 2. Initialize map only once
    let map = mapInstanceRef.current;
    if (!map) {
      map = new window.google.maps.Map(mapContainerRef.current, {
        center: { lat: 20.5937, lng: 78.9629 }, // Default center: India
        zoom: 5, // Default low zoom
        fullscreenControl: false,
        mapTypeControl: false,
        streetViewControl: false,
      });
      mapInstanceRef.current = map;
      setHasMapBeenCreated(true); // Indicate map is now initialized
      console.log("Map instance created.");
    }

    // 3. Handle route data or lack thereof
    if (!routeData || !routeData.success || !routeData.route_details || !routeData.route_details.route_geometry || routeData.route_details.route_geometry.length < 2) {
      // Clear existing overlays (polyline, markers) if route data is invalid or not available
      if (polylineRef.current) { polylineRef.current.setMap(null); polylineRef.current = null; }
      if (startMarkerRef.current) { startMarkerRef.current.setMap(null); startMarkerRef.current = null; }
      if (endMarkerRef.current) { endMarkerRef.current.setMap(null); endMarkerRef.current = null; }

      // Clear any existing charging station markers
      if (chargingMarkersRef.current) {
          chargingMarkersRef.current.forEach(marker => marker.setMap(null));
          chargingMarkersRef.current = []; // Clear the array
      }

      // Update map center/zoom to a default view if no route
      if (map) {
          map.setCenter({ lat: 20.5937, lng: 78.9629 }); // Center of India
          map.setZoom(5);
      }
      return; // Exit if no valid route data
    }

    // At this point, we have a map instance and valid routeData
    const { route_details } = routeData;
    const { route_geometry } = route_details;
    // Assuming route_details also contains charging_locations_coords from backend
    const { charging_locations_coords } = route_details;

    const path = route_geometry.map(coord => ({ lat: coord.lat, lng: coord.lon }));

    // 4. Update or create polyline
    if (polylineRef.current) {
      polylineRef.current.setPath(path);
      polylineRef.current.setMap(map); // Ensure it's attached to the correct map instance
    } else {
      polylineRef.current = new window.google.maps.Polyline({
        path: path,
        geodesic: true,
        strokeColor: "#FF0000",
        strokeOpacity: 0.8,
        strokeWeight: 4,
        map: map,
      });
    }

    // 5. Update or create start marker
    const startCoords = path[0];
    if (startMarkerRef.current) {
      startMarkerRef.current.setPosition(startCoords);
      startMarkerRef.current.setMap(map);
    } else {
      startMarkerRef.current = new window.google.maps.Marker({
        position: startCoords,
        map: map,
        title: "Start Location",
        label: "A",
      });
    }

    // 6. Update or create end marker
    const endCoords = path[path.length - 1];
    if (endMarkerRef.current) {
      endMarkerRef.current.setPosition(endCoords);
      endMarkerRef.current.setMap(map);
    } else {
      endMarkerRef.current = new window.google.maps.Marker({
        position: endCoords,
        map: map,
        title: "End Location",
        label: "B",
        icon: {
            path: window.google.maps.SymbolPath.CIRCLE,
            fillColor: 'blue',
            fillOpacity: 1,
            scale: 6,
            strokeColor: 'white',
            strokeWeight: 2
        }
      });
    }

    // 7. Display Charging Station Markers
    // First, clear any old charging markers before drawing new ones
    if (chargingMarkersRef.current) {
        chargingMarkersRef.current.forEach(marker => marker.setMap(null));
        chargingMarkersRef.current = []; // Reset the array
    }

    if (charging_locations_coords && charging_locations_coords.length > 0) {
        charging_locations_coords.forEach((charge_coord, index) => {
            const marker = new window.google.maps.Marker({
                position: { lat: charge_coord.lat, lng: charge_coord.lon },
                map: map,
                title: `Charging Stop ${index + 1}`,
                label: {
                    text: `⚡️${index + 1}`, // Unicode lightning bolt + number
                    color: "white",
                    fontWeight: "bold",
                    fontSize: "12px",
                },
                icon: {
                    path: window.google.maps.SymbolPath.CIRCLE, // Can replace with a custom SVG path for lightning bolt
                    fillColor: '#FFD700', // Gold color for chargers
                    fillOpacity: 1,
                    strokeColor: '#B8860B', // Darker gold outline
                    strokeWeight: 1,
                    scale: 10,
                },
            });
            chargingMarkersRef.current.push(marker); // Add to the ref array
        });
        console.log(`DEBUG: Displayed ${charging_locations_coords.length} charging markers.`);
    } else {
        console.log("DEBUG: No charging locations to display.");
    }

    // 8. Fit map to bounds of the polyline (and optionally markers)
    const bounds = new window.google.maps.LatLngBounds();
    for (let i = 0; i < path.length; i++) {
        bounds.extend(path[i]);
    }
    // Also extend bounds to include charging markers if they exist
    charging_locations_coords?.forEach(coord => {
        bounds.extend({ lat: coord.lat, lng: coord.lon });
    });
    map.fitBounds(bounds);

    // Cleanup function: runs when component unmounts or before this effect re-runs
    return () => {
        if (polylineRef.current) polylineRef.current.setMap(null);
        if (startMarkerRef.current) startMarkerRef.current.setMap(null);
        if (endMarkerRef.current) endMarkerRef.current.setMap(null);
        // Ensure all charging markers are also removed during cleanup
        if (chargingMarkersRef.current) {
            chargingMarkersRef.current.forEach(marker => marker.setMap(null));
            chargingMarkersRef.current = [];
        }
    };

  }, [routeData, isGoogleMapsApiReady, hasMapBeenCreated]); // Dependencies for this effect

  return (
    <> {/* Use a React Fragment to return multiple top-level elements */}
      {/* Conditionally render placeholder ONLY if map has NOT been created yet.
          It's now OUTSIDE the map-container div to prevent DOM conflicts. */}
      {!hasMapBeenCreated && (
        <p className="map-placeholder-text">
          {initialMapMessage}
        </p>
      )}

      {/* The actual map container where Google Maps directly renders. */}
      <div className="map-container" ref={mapContainerRef}>
        {/* Google Map will render here. */}
      </div>
    </>
  );
}

export default MapDisplay;
