import { useEffect, useState } from "react";

function TopBar({ search, setSearch }) {
  const [dateTime, setDateTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setDateTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="topbar">
      <div>
        <h2>Fleet Monitoring Dashboard</h2>

        <p>
          {dateTime.toLocaleDateString()} |{" "}
          {dateTime.toLocaleTimeString()}
        </p>
      </div>

      <div className="topbar-right">
        <input
          type="text"
          placeholder="🔍 Search Truck or Driver..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <button>🔔</button>

        <button>👤 Namrata</button>
      </div>
    </div>
  );
}

export default TopBar;