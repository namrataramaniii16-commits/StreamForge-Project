function TruckTable({ search }) {
  const trucks = [
    {
      id: "TRK001",
      driver: "Rahul",
      fuel: "82%",
      temp: "26°C",
      speed: "62 km/h",
      status: "Moving",
    },
    {
      id: "TRK002",
      driver: "Amit",
      fuel: "74%",
      temp: "31°C",
      speed: "54 km/h",
      status: "Moving",
    },
    {
      id: "TRK003",
      driver: "Priya",
      fuel: "18%",
      temp: "42°C",
      speed: "0 km/h",
      status: "Idle",
    },
    {
      id: "TRK004",
      driver: "Karan",
      fuel: "91%",
      temp: "25°C",
      speed: "68 km/h",
      status: "Moving",
    },
  ];

  const filteredTrucks = trucks.filter(
    (truck) =>
      truck.id.toLowerCase().includes(search.toLowerCase()) ||
      truck.driver.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="table-container">
      <h2>🚚 Live Truck Status</h2>

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
          {filteredTrucks.map((truck) => (
            <tr key={truck.id}>
              <td>{truck.id}</td>

              <td>{truck.driver}</td>

              <td>
                <div className="fuel-bar">
                  <div
                    className="fuel-fill"
                    style={{
                      width: truck.fuel,
                      background:
                        parseInt(truck.fuel) < 25
                          ? "#ff5252"
                          : parseInt(truck.fuel) < 60
                          ? "#ffca28"
                          : "#00c853",
                    }}
                  ></div>
                </div>

                <span>{truck.fuel}</span>
              </td>

              <td
                style={{
                  color:
                    parseInt(truck.temp) > 35
                      ? "#ff5252"
                      : "#00e676",
                  fontWeight: "bold",
                }}
              >
                {truck.temp}
              </td>

              <td>{truck.speed}</td>

              <td>
                <span
                  className={
                    truck.status === "Moving"
                      ? "status-moving"
                      : "status-idle"
                  }
                >
                  {truck.status === "Moving"
                    ? "🟢 Moving"
                    : "🔴 Idle"}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TruckTable;