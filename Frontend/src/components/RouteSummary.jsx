import React from 'react';

const RouteSummary = ({ data }) => {
    if (!data) {
        return (
            <div className="bg-white p-4 rounded-lg shadow-md mt-4">
                <h2 className="text-xl font-semibold mb-2">Route Summary</h2>
                <p>No route data available yet. Please plan a route.</p>
            </div>
        );
    }

    // Helper function to format minutes into hours and minutes
    const formatMinutes = (totalMinutes) => {
        if (totalMinutes === null || totalMinutes === undefined) {
            return "N/A";
        }
        const hours = Math.floor(totalMinutes / 60);
        const minutes = Math.round(totalMinutes % 60);
        if (hours > 0) {
            return `${hours}h ${minutes}m`;
        }
        return `${minutes}m`;
    };

    return (
        <div className="bg-white p-4 rounded-lg shadow-md mt-4">
            <h2 className="text-xl font-semibold mb-2">Route Summary</h2>
            <div className="space-y-1 text-gray-700">
                <p><strong>Total Distance:</strong> {data.totalDistanceKm ? data.totalDistanceKm.toFixed(2) : 'N/A'} km</p>
                <p>
                    <strong>Estimated Total Travel Time:</strong> {formatMinutes(data.totalDurationMinutes)}
                </p>
                {/* New lines for detailed time breakdown */}
                {data.totalDrivingMinutes !== undefined && (
                    <p className="ml-4 text-sm text-gray-600">
                        (Driving: {formatMinutes(data.totalDrivingMinutes)})
                    </p>
                )}
                {data.totalChargingMinutes !== undefined && data.totalChargingMinutes > 0 && (
                    <p className="ml-4 text-sm text-gray-600">
                        (Charging: {formatMinutes(data.totalChargingMinutes)})
                    </p>
                )}
                <p><strong>Estimated Charging Stops:</strong> {data.estimatedChargingStops !== undefined ? data.estimatedChargingStops : 'N/A'}</p>
                <p><strong>Total Energy Consumption:</strong> {data.totalEnergyConsumptionKwh ? data.totalEnergyConsumptionKwh.toFixed(2) : 'N/A'} kWh</p>
                <p><strong>Final Charge at Destination:</strong> {data.finalChargePercent !== undefined ? `${data.finalChargePercent}%` : 'N/A'}</p>
            </div>
        </div>
    );
};

export default RouteSummary;