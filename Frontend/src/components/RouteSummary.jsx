import React from 'react';

const RouteSummary = ({ data }) => {
    if (!data || !data.route_summary) {
        return (
            <div className="route-summary bg-white p-4 rounded-lg shadow-md mt-4">
                <h2 className="text-xl font-semibold mb-2">Route Summary</h2>
                <p>No route data available yet. Please plan a route.</p>
            </div>
        );
    }

    const {
        totalDistanceKm,
        totalDurationMinutes,
        totalDrivingMinutes,
        totalChargingMinutes,
        estimatedChargingStops,
        totalEnergyConsumptionKwh,
        finalChargePercent
    } = data.route_summary;

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
        <div className="route-summary bg-white p-4 rounded-lg shadow-md mt-4">
            <h2 className="text-xl font-semibold mb-2">Route Summary</h2>
            <div className="space-y-1 text-gray-700">
                <p><strong>Total Distance:</strong> {totalDistanceKm !== undefined ? totalDistanceKm.toFixed(2) : 'N/A'} km</p>
                <p>
                    <strong>Estimated Total Travel Time:</strong> {formatMinutes(totalDurationMinutes)}
                </p>
                {totalDrivingMinutes !== undefined && (
                    <p className="ml-4 text-sm text-gray-600">
                        (Driving: {formatMinutes(totalDrivingMinutes)})
                    </p>
                )}
                {totalChargingMinutes !== undefined && totalChargingMinutes > 0 && (
                    <p className="ml-4 text-sm text-gray-600">
                        (Charging: {formatMinutes(totalChargingMinutes)})
                    </p>
                )}
                {/* --- Robust display for Estimated Charging Stops --- */}
                <p>
                    <strong>Estimated Charging Stops:</strong>
                    {/* Check if it's a number, if so, display it. Otherwise, N/A.
                        Adding ' stops' for better readability if the value is 0. */}
                    {typeof estimatedChargingStops === 'number'
                        ? `${estimatedChargingStops} stops`
                        : 'N/A'}
                </p>
                <p><strong>Total Energy Consumption:</strong> {totalEnergyConsumptionKwh !== undefined ? totalEnergyConsumptionKwh.toFixed(2) : 'N/A'} kWh</p>
                <p><strong>Final Charge at Destination:</strong> {finalChargePercent !== undefined ? `${finalChargePercent.toFixed(2)}%` : 'N/A'}</p>
            </div>
        </div>
    );
};

export default RouteSummary;
