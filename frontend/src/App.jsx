import { useEffect, useState } from "react";

import "./App.css";

import Sidebar from "./components/Sidebar";
import TopBar from "./components/TopBar";
import StatsCards from "./components/StatsCards";
import Charts from "./components/Charts";
import ActivityPanel from "./components/ActivityPanel";
import TruckTable from "./components/TruckTable";
import Footer from "./components/Footer";

function App() {
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1200);

    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="loading">
        🚚 Loading Fleet Dashboard...
      </div>
    );
  }

  return (
    <div className="app">
      <Sidebar />

      <div className="content">
        <TopBar
          search={search}
          setSearch={setSearch}
        />

        <StatsCards />

        <Charts />

        <ActivityPanel />

        <TruckTable search={search} />

        <Footer />
      </div>
    </div>
  );
}

export default App;