import { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8000/api";

function TruckTable({ search }) {
  const [trucks, setTrucks] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchTrucks = async () => {
    try {
      const response = await fetch(`${API_BASE}/trucks`);

      if (!response.ok) {
        throw new Error("Failed to fetch trucks");
      }

      const data = await response.json();

      setTrucks(Array.isArray(data) ? data : []);
      setLoading(false);
    } catch (error) {
      console.error("Truck API error:", error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrucks();

    const interval = setInterval(fetchTrucks, 3000);

    return () => clearInterval(interval);
  }, []);

  const filteredTrucks = trucks.filter((truck) =>
    String(truck.truck_id || "")
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  return (
    <div className="table-container">
      <h2>🚚 Live Truck Status</h2>

      {loading ? (
        <p>Loading live truck data...</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Truck ID</th>
              <th>Driver</th>
              <th>Fuel</th>
              <th>Temperature</th>
              <th>Speed</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            {filteredTrucks.map((truck) => {
              const temperature = Number(truck.temperature || 0);

              return (
                <tr key={truck.truck_id}>
                  <td>{truck.truck_id}</td>

                  <td>—</td>

                  <td>
                    <div className="fuel-bar">
                      <div
                        className="fuel-fill"
                        style={{
                          width: "—",
                          background: "#00c853",
                        }}
                      ></div>
                    </div>

                    <span>—</span>
                  </td>

                  <td
                    style={{
                      color:
                        temperature > 35
                          ? "#ff5252"
                          : "#00e676",
                      fontWeight: "bold",
                    }}
                  >
                    {temperature.toFixed(2)}°C
                  </td>

                  <td>—</td>

                  <td>
                    <span
                      className={
                        truck.status === "Healthy"
                          ? "status-moving"
                          : "status-idle"
                      }
                    >
                      {truck.status === "Healthy"
                        ? "🟢 Online"
                        : "🔴 Offline"}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}

      {!loading && filteredTrucks.length === 0 && (
        <p>No truck data available.</p>
      )}
    </div>
  );
}

export default TruckTable;