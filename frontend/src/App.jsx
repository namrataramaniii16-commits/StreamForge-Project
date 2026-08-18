import React, { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bell,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  CircleGauge,
  Database,
  Gauge,
  Network,
  Search,
  Server,
  Settings,
  Truck,
  Users,
  XCircle,
  Zap,
  Thermometer,
  Clock3,
  Wifi,
  WifiOff,
  AlertCircle,
  Info,
  Check,
} from "lucide-react";

import Topology from "./components/Topology";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

/* =====================================================
   APP
===================================================== */

function App() {
  const [collapsed, setCollapsed] = useState(false);
  const [activePage, setActivePage] = useState("Dashboard");

  const [health, setHealth] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [workers, setWorkers] = useState([]);
  const [logs, setLogs] = useState([]);

  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  /* =====================================================
     BACKEND DATA
  ===================================================== */

  const fetchData = async () => {
    try {
      const [healthRes, metricsRes, workersRes, logsRes] =
        await Promise.all([
          fetch(`${API_BASE}/api/health`),
          fetch(`${API_BASE}/api/metrics`),
          fetch(`${API_BASE}/api/workers`),
          fetch(`${API_BASE}/api/logs`),
        ]);

      if (!healthRes.ok || !metricsRes.ok) {
        throw new Error("Backend unavailable");
      }

      const healthData = await healthRes.json();
      const metricsData = await metricsRes.json();

      const workersData = workersRes.ok
        ? await workersRes.json()
        : [];

      const logsData = logsRes.ok
        ? await logsRes.json()
        : [];

      setHealth(healthData);
      setMetrics(metricsData);

      setWorkers(
        Array.isArray(workersData)
          ? workersData
          : workersData?.workers || []
      );

      setLogs(
        Array.isArray(logsData)
          ? logsData
          : logsData?.logs || []
      );

      setLastUpdated(new Date());
    } catch (error) {
      console.error("Backend connection error:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();

    const interval = setInterval(fetchData, 3000);

    return () => clearInterval(interval);
  }, []);

  /* =====================================================
     CALCULATIONS
  ===================================================== */

  const activeWorkers =
    metrics?.active_workers ??
    health?.workers?.healthy ??
    workers.filter(
      (worker) =>
        worker.status === "Running" ||
        worker.status === "Healthy"
    ).length;

  const totalWorkers =
    health?.workers?.total ??
    (workers.length > 0 ? workers.length : 20);

  const healthyWorkers =
    workers.filter(
      (worker) =>
        worker.status === "Running" ||
        worker.status === "Healthy"
    ).length || activeWorkers;

  const filteredWorkers = workers.filter((worker) =>
    `${worker.worker_id} ${worker.partition}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  const kafkaConnected =
    health?.kafka_connected === true;

  /* =====================================================
     ALERTS
  ===================================================== */

  const alerts = useMemo(() => {
    const result = [];

    if (!kafkaConnected) {
      result.push({
        id: "kafka",
        severity: "critical",
        title: "Kafka connection lost",
        description:
          "Kafka broker is currently disconnected from StreamForge.",
        source: "Kafka",
        time: "Current",
      });
    } else {
      result.push({
        id: "kafka",
        severity: "resolved",
        title: "Kafka connection healthy",
        description:
          "Kafka broker is connected and responding normally.",
        source: "Kafka",
        time: "Current",
      });
    }

    if (healthyWorkers < totalWorkers) {
      result.push({
        id: "workers",
        severity: "critical",
        title: "Worker health issue detected",
        description: `${totalWorkers - healthyWorkers} worker(s) are not healthy.`,
        source: "Workers",
        time: "Current",
      });
    } else {
      result.push({
        id: "workers",
        severity: "resolved",
        title: "All workers are healthy",
        description: `${healthyWorkers}/${totalWorkers} distributed workers are running.`,
        source: "Workers",
        time: "Current",
      });
    }

    const lag =
      Number(metrics?.processing_lag_seconds) || 0;

    if (lag > 5) {
      result.push({
        id: "lag",
        severity: "warning",
        title: "High processing lag",
        description: `Current processing lag is ${lag} seconds.`,
        source: "Processing",
        time: "Current",
      });
    } else {
      result.push({
        id: "lag",
        severity: "resolved",
        title: "Processing lag normal",
        description: `Current processing lag is ${lag} seconds.`,
        source: "Processing",
        time: "Current",
      });
    }

    const processed =
      Number(metrics?.events_processed) || 0;

    if (processed === 0) {
      result.push({
        id: "events",
        severity: "warning",
        title: "No events processed",
        description:
          "The processor has not processed any events yet.",
        source: "Event Processor",
        time: "Current",
      });
    } else {
      result.push({
        id: "events",
        severity: "resolved",
        title: "Event processing active",
        description: `${processed.toLocaleString()} events processed successfully.`,
        source: "Event Processor",
        time: "Current",
      });
    }

    return result;
  }, [
    kafkaConnected,
    healthyWorkers,
    totalWorkers,
    metrics,
  ]);

  const activeAlerts = alerts.filter(
    (alert) =>
      alert.severity === "critical" ||
      alert.severity === "warning"
  ).length;

  /* =====================================================
     NAVIGATION
  ===================================================== */

  const handleNavigation = (page, event) => {
    if (event) {
      event.preventDefault();
    }

    setActivePage(page);
    setSearch("");
  };

  /* =====================================================
     PAGE RENDERER
  ===================================================== */

  const renderPage = () => {
    if (activePage === "Dashboard") {
      return (
        <DashboardContent
          metrics={metrics}
          activeWorkers={activeWorkers}
          totalWorkers={totalWorkers}
          healthyWorkers={healthyWorkers}
          kafkaConnected={kafkaConnected}
          lastUpdated={lastUpdated}
          filteredWorkers={filteredWorkers}
          logs={logs}
        />
      );
    }

    if (activePage === "Trucks") {
      return (
        <TrucksPage
          metrics={metrics}
          kafkaConnected={kafkaConnected}
          search={search}
        />
      );
    }

    if (activePage === "Workers") {
      return (
        <WorkersPage
          workers={workers}
          activeWorkers={activeWorkers}
          totalWorkers={totalWorkers}
          search={search}
        />
      );
    }

    if (activePage === "Topology") {
      return <TopologyPage />;
    }

    if (activePage === "Alerts") {
      return (
        <AlertsPage
          alerts={alerts}
          activeAlerts={activeAlerts}
        />
      );
    }

    if (activePage === "Reports") {
      return (
        <ReportsPage
          metrics={metrics}
          activeWorkers={activeWorkers}
        />
      );
    }

    if (activePage === "State Storage") {
      return (
        <StateStoragePage
          activeWorkers={activeWorkers}
        />
      );
    }

    if (activePage === "Settings") {
      return (
        <SettingsPage
          kafkaConnected={kafkaConnected}
        />
      );
    }

    return null;
  };

  /* =====================================================
     APP UI
  ===================================================== */

  return (
    <div className="app-shell">

      {/* =================================================
          SIDEBAR
      ================================================= */}

      <aside
        className={`sidebar ${
          collapsed ? "collapsed" : ""
        }`}
      >
        <div className="brand">
          <div className="brand-icon">
            <Truck size={23} />
          </div>

          {!collapsed && (
            <div>
              <div className="brand-name">
                StreamForge
              </div>

              <div className="brand-subtitle">
                Distributed Event Processor
              </div>
            </div>
          )}
        </div>

        <nav className="nav-menu">

          <div className="nav-section">
            MONITORING
          </div>

          {/* DASHBOARD */}

          <a
            href="#"
            className={`nav-item ${
              activePage === "Dashboard"
                ? "active"
                : ""
            }`}
            onClick={(e) =>
              handleNavigation("Dashboard", e)
            }
          >
            <CircleGauge size={19} />

            {!collapsed && (
              <span>Dashboard</span>
            )}
          </a>

          {/* TRUCKS */}

          <a
            href="#"
            className={`nav-item ${
              activePage === "Trucks"
                ? "active"
                : ""
            }`}
            onClick={(e) =>
              handleNavigation("Trucks", e)
            }
          >
            <Truck size={19} />

            {!collapsed && (
              <span>Trucks</span>
            )}
          </a>

          {/* WORKERS */}

          <a
            href="#"
            className={`nav-item ${
              activePage === "Workers"
                ? "active"
                : ""
            }`}
            onClick={(e) =>
              handleNavigation("Workers", e)
            }
          >
            <Users size={19} />

            {!collapsed && (
              <span>Workers</span>
            )}
          </a>

          {/* TOPOLOGY */}

          <a
            href="#"
            className={`nav-item ${
              activePage === "Topology"
                ? "active"
                : ""
            }`}
            onClick={(e) =>
              handleNavigation("Topology", e)
            }
          >
            <Network size={19} />

            {!collapsed && (
              <span>Topology</span>
            )}
          </a>

          {/* ALERTS */}

          <a
            href="#"
            className={`nav-item ${
              activePage === "Alerts"
                ? "active"
                : ""
            }`}
            onClick={(e) =>
              handleNavigation("Alerts", e)
            }
          >
            <AlertTriangle size={19} />

            {!collapsed && (
              <span>Alerts</span>
            )}

            {!collapsed && activeAlerts > 0 && (
              <span className="nav-badge">
                {activeAlerts}
              </span>
            )}
          </a>

          {/* REPORTS */}

          <a
            href="#"
            className={`nav-item ${
              activePage === "Reports"
                ? "active"
                : ""
            }`}
            onClick={(e) =>
              handleNavigation("Reports", e)
            }
          >
            <BarChart3 size={19} />

            {!collapsed && (
              <span>Reports</span>
            )}
          </a>

          <div className="nav-section second">
            SYSTEM
          </div>

          {/* STATE STORAGE */}

          <a
            href="#"
            className={`nav-item ${
              activePage === "State Storage"
                ? "active"
                : ""
            }`}
            onClick={(e) =>
              handleNavigation(
                "State Storage",
                e
              )
            }
          >
            <Database size={19} />

            {!collapsed && (
              <span>
                State Storage
              </span>
            )}
          </a>

          {/* SETTINGS */}

          <a
            href="#"
            className={`nav-item ${
              activePage === "Settings"
                ? "active"
                : ""
            }`}
            onClick={(e) =>
              handleNavigation("Settings", e)
            }
          >
            <Settings size={19} />

            {!collapsed && (
              <span>Settings</span>
            )}
          </a>
        </nav>

        {/* SIDEBAR BOTTOM */}

        <div className="sidebar-bottom">

          <div className="system-status">

            <span
              className={`status-dot ${
                kafkaConnected
                  ? "online"
                  : "offline"
              }`}
            />

            {!collapsed && (
              <div>
                <strong>
                  {kafkaConnected
                    ? "System Operational"
                    : "System Degraded"}
                </strong>

                <small>
                  {kafkaConnected
                    ? "Kafka connected"
                    : "Kafka disconnected"}
                </small>
              </div>
            )}
          </div>

          <button
            className="collapse-btn"
            onClick={() =>
              setCollapsed(!collapsed)
            }
          >
            {collapsed ? (
              <ChevronRight size={18} />
            ) : (
              <ChevronLeft size={18} />
            )}
          </button>

        </div>
      </aside>

      {/* =================================================
          MAIN
      ================================================= */}

      <main className="main-content">

        {/* HEADER */}

        <header className="top-header">

          <div>

            <div className="breadcrumb">
              Monitoring /{" "}
              <span>
                {activePage}
              </span>
            </div>

            <h1>
              {activePage === "Dashboard"
                ? "Stream Processing Dashboard"
                : activePage}
            </h1>

            <p>
              {activePage === "Dashboard"
                ? "Real-time distributed event processing overview"
                : getPageDescription(
                    activePage
                  )}
            </p>

          </div>

          <div className="header-actions">

            <div className="search-box">

              <Search size={18} />

              <input
                placeholder={
                  activePage === "Trucks"
                    ? "Search truck ID..."
                    : "Search worker or partition..."
                }
                value={search}
                onChange={(e) =>
                  setSearch(e.target.value)
                }
              />

              {search && (
                <button
                  onClick={() =>
                    setSearch("")
                  }
                >
                  <XCircle size={16} />
                </button>
              )}

            </div>

            <button className="icon-button">
              <Bell size={19} />

              {activeAlerts > 0 && (
                <span className="notification-dot" />
              )}
            </button>

            <div className="profile">

              <div className="avatar">
                P
              </div>

              <div>
                <strong>
                  Admin
                </strong>

                <small>
                  Operator
                </small>
              </div>

            </div>

          </div>

        </header>

        {/* ACTIVE PAGE */}

        {renderPage()}

        {/* FOOTER */}

        <footer>
          <span>
            StreamForge v2.0.0
          </span>

          <span>
            FastAPI + Kafka + React + RocksDB
          </span>
        </footer>

      </main>
    </div>
  );
}

/* =====================================================
   DASHBOARD
===================================================== */

function DashboardContent({
  metrics,
  activeWorkers,
  totalWorkers,
  healthyWorkers,
  kafkaConnected,
  lastUpdated,
  filteredWorkers,
  logs,
}) {
  return (
    <>
      {/* STATUS */}

      <section className="status-banner">

        <div className="status-left">

          <div
            className={`large-status-icon ${
              kafkaConnected
                ? "success"
                : "warning"
            }`}
          >
            {kafkaConnected ? (
              <CheckCircle2 size={21} />
            ) : (
              <AlertTriangle size={21} />
            )}
          </div>

          <div>

            <strong>
              {kafkaConnected
                ? "All systems operational"
                : "System running in simulation/degraded mode"}
            </strong>

            <span>
              Last updated{" "}
              {lastUpdated.toLocaleTimeString()}
            </span>

          </div>

        </div>

        <div className="status-right">

          <span
            className={`live-pill ${
              kafkaConnected
                ? "live"
                : "warning"
            }`}
          >
            <span />

            {kafkaConnected
              ? "LIVE"
              : "DEGRADED"}
          </span>

        </div>

      </section>

      {/* KPI */}

      <section className="kpi-grid">

        <KpiCard
          title="Events / sec"
          value={
            metrics?.events_per_second ?? 0
          }
          icon={<Zap size={21} />}
          trend="Real-time throughput"
          className="purple"
        />

        <KpiCard
          title="Events Processed"
          value={
            metrics?.events_processed ?? 0
          }
          icon={<Activity size={21} />}
          trend="Total processed events"
          className="blue"
        />

        <KpiCard
          title="Active Workers"
          value={`${activeWorkers}/${totalWorkers}`}
          icon={<Server size={21} />}
          trend={`${healthyWorkers} healthy workers`}
          className="green"
        />

        <KpiCard
          title="Processing Lag"
          value={`${
            metrics?.processing_lag_seconds ?? 0
          }s`}
          icon={<Gauge size={21} />}
          trend="Current processing latency"
          className="orange"
        />

      </section>

      {/* TOPOLOGY + WORKERS */}

      <section className="content-grid">

        <div className="panel topology-panel">

          <div className="panel-header">

            <div>
              <h2>
                Stream Processing Topology
              </h2>

              <p>
                Kafka → Workers → Aggregator → RocksDB
              </p>
            </div>

            <div className="panel-live">
              <span />
              Live topology
            </div>

          </div>

          <div className="topology-container">
            <Topology />
          </div>

        </div>

        <div className="panel worker-panel">

          <div className="panel-header">

            <div>
              <h2>
                Worker Health
              </h2>

              <p>
                20 distributed processing workers
              </p>
            </div>

            <span className="view-all">
              {healthyWorkers}/{totalWorkers}
            </span>

          </div>

          <div className="worker-list">

            {filteredWorkers.length > 0 ? (
              filteredWorkers
                .slice(0, 10)
                .map((worker) => (
                  <WorkerRow
                    key={worker.worker_id}
                    worker={worker}
                  />
                ))
            ) : (
              Array.from({ length: 6 }).map(
                (_, index) => (
                  <div
                    className="worker-row"
                    key={index}
                  >

                    <div className="worker-info">

                      <div className="worker-icon">
                        <Server size={16} />
                      </div>

                      <div>
                        <strong>
                          Worker-{index + 1}
                        </strong>

                        <small>
                          Partition {index}
                        </small>
                      </div>

                    </div>

                    <div className="worker-stats">

                      <span>
                        0 eps
                      </span>

                      <span className="worker-status running">
                        <span />
                        Running
                      </span>

                    </div>

                  </div>
                )
              )
            )}

          </div>

        </div>

      </section>

      {/* BOTTOM */}

      <section className="bottom-grid">

        <div className="panel metric-panel">

          <div className="panel-header">

            <div>
              <h2>
                Processing Metrics
              </h2>

              <p>
                Current event pipeline statistics
              </p>
            </div>

          </div>

          <div className="metric-list">

            <MetricRow
              label="Events Consumed"
              value={
                metrics?.events_consumed ?? 0
              }
              icon={<Activity size={17} />}
            />

            <MetricRow
              label="Events Processed"
              value={
                metrics?.events_processed ?? 0
              }
              icon={
                <CheckCircle2 size={17} />
              }
            />

            <MetricRow
              label="Events Filtered"
              value={
                metrics?.events_filtered ?? 0
              }
              icon={<XCircle size={17} />}
            />

            <MetricRow
              label="Active Workers"
              value={
                metrics?.active_workers ?? 20
              }
              icon={<Users size={17} />}
            />

          </div>

        </div>

        <div className="panel logs-panel">

          <div className="panel-header">

            <div>
              <h2>
                Recent Activity
              </h2>

              <p>
                Latest system events
              </p>
            </div>

            <Activity size={18} />

          </div>

          <div className="logs">

            {logs.length > 0 ? (
              logs
                .slice(-6)
                .reverse()
                .map((log, index) => (
                  <div
                    className="log-row"
                    key={index}
                  >
                    <span className="log-dot" />

                    <span>
                      {typeof log === "string"
                        ? log
                        : log.message ||
                          "System event"}
                    </span>
                  </div>
                ))
            ) : (
              <div className="empty-logs">

                <Activity size={25} />

                <span>
                  No recent events
                </span>

                <small>
                  System activity will appear here
                </small>

              </div>
            )}

          </div>

        </div>

      </section>
    </>
  );
}

/* =====================================================
   TRUCK DATA
===================================================== */

/*
  StreamForge requirement:
  50,000 trucks
  Telemetry every 10 seconds
*/

const TRUCK_COUNT = 50000;

function getTruckStatus(index) {
  if (index % 317 === 0) return "Offline";
  if (index % 127 === 0) return "Warning";
  return "Online";
}

function getTruckTemperature(index) {
  return (
    68 +
    ((index * 17) % 25) +
    (index % 10) / 10
  ).toFixed(1);
}

function getTruckEvents(index) {
  return (4.5 + ((index * 13) % 30) / 10).toFixed(2);
}

/* =====================================================
   TRUCKS PAGE
===================================================== */

function TrucksPage({
  metrics,
  kafkaConnected,
  search,
}) {
  const [truckPage, setTruckPage] = useState(1);
  const [truckData, setTruckData] = useState([]);

  const trucksPerPage = 50;
    useEffect(() => {
    let cancelled = false;

    const loadTrucks = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/api/trucks"
        );

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        if (!cancelled) {
          setTruckData(
            Array.isArray(data) ? data : []
          );
        }
      } catch (error) {
        console.error(
          "Failed to load truck telemetry:",
          error
        );
      }
    };

    loadTrucks();

    const interval = setInterval(
      loadTrucks,
      5000
    );

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  const filteredTrucks = useMemo(() => {
    const term = search.trim().toLowerCase();

    if (!term) {
      return null;
    }

    const results = [];

    for (let i = 1; i <= TRUCK_COUNT; i++) {
      const truckId = `TRUCK-${String(i).padStart(
        5,
        "0"
      )}`;

      if (
        truckId.toLowerCase().includes(term)
      ) {
        results.push(i);
      }

      if (results.length >= 500) {
        break;
      }
    }

    return results;
  }, [search]);

  const totalPages = Math.ceil(
    TRUCK_COUNT / trucksPerPage
  );

  const currentIndexes = filteredTrucks
    ? filteredTrucks.slice(
        (truckPage - 1) * trucksPerPage,
        truckPage * trucksPerPage
      )
    : Array.from(
        {
          length: trucksPerPage,
        },
        (_, index) =>
          (truckPage - 1) *
            trucksPerPage +
          index +
          1
      ).filter(
        (index) => index <= TRUCK_COUNT
      );

  useEffect(() => {
    setTruckPage(1);
  }, [search]);

  return (
    <section className="panel page-panel">

      {/* HEADER */}

      <div className="panel-header">

        <div>
          <h2>
            Connected Trucks
          </h2>

          <p>
            Monitor 50,000 connected trucks and
            real-time telemetry data
          </p>
        </div>

        <Truck size={25} />

      </div>

      {/* TRUCK KPI */}

      <div className="kpi-grid">

        <KpiCard
          title="Total Trucks"
          value="50,000"
          icon={<Truck size={21} />}
          trend="Configured fleet"
          className="purple"
        />

        <KpiCard
          title="Online Trucks"
          value={
            kafkaConnected
              ? "49,842"
              : "0"
          }
          icon={
            <CheckCircle2 size={21} />
          }
          trend="Currently connected"
          className="green"
        />

        <KpiCard
          title="Telemetry Interval"
          value="10s"
          icon={
            <Activity size={21} />
          }
          trend="Data reporting frequency"
          className="blue"
        />

        <KpiCard
          title="Events / sec"
          value={
            metrics?.events_per_second ?? 0
          }
          icon={<Zap size={21} />}
          trend="Incoming telemetry"
          className="orange"
        />

      </div>

      {/* FLEET SUMMARY */}

      <div className="metric-list">

        <MetricRow
          label="Fleet Status"
          value={
            kafkaConnected
              ? "Operational"
              : "Degraded"
          }
          icon={<Truck size={17} />}
        />

        <MetricRow
          label="Telemetry Source"
          value="Kafka"
          icon={<Network size={17} />}
        />

        <MetricRow
          label="Processing Window"
          value="5 minutes"
          icon={<Gauge size={17} />}
        />

      </div>

      {/* TRUCK LIST */}

      <div
        style={{
          marginTop: "24px",
          borderTop:
            "1px solid rgba(255,255,255,0.08)",
        }}
      >

        <div
          style={{
            padding: "20px 16px 14px",
            display: "flex",
            justifyContent:
              "space-between",
            alignItems: "center",
          }}
        >

          <div>
            <h3
              style={{
                margin: 0,
                fontSize: "18px",
              }}
            >
              Truck Fleet
            </h3>

            <p
              style={{
                margin: "5px 0 0",
                fontSize: "13px",
                opacity: 0.65,
              }}
            >
              {search
                ? `Search results for "${search}"`
                : "All registered trucks"}
            </p>
          </div>

          <span className="view-all">
            {search
              ? `${filteredTrucks?.length || 0} found`
              : "50,000 trucks"}
          </span>

        </div>

        {/* TABLE HEADER */}

        <div
          className="truck-table-header"
          style={{
            display: "grid",
            gridTemplateColumns:
              "1.4fr 1fr 1fr 1fr 1fr 1fr",
            padding:
              "12px 20px",
            fontSize: "12px",
            opacity: 0.55,
            borderTop:
              "1px solid rgba(255,255,255,0.06)",
            borderBottom:
              "1px solid rgba(255,255,255,0.06)",
          }}
        >
          <span>TRUCK ID</span>
          <span>STATUS</span>
          <span>TEMPERATURE</span>
          <span>TELEMETRY</span>
          <span>EVENTS / SEC</span>
          <span>LAST SEEN</span>
        </div>

        {/* ROWS */}

        <div
          className="truck-list"
          style={{
            maxHeight: "620px",
            overflowY: "auto",
          }}
        >

          {currentIndexes.map((index) => {
  const truckId = `TRUCK_${String(index).padStart(5, "0")}`;

  const truck = truckData.find(
    (item) => item.truck_id === truckId
  );

  return (
    <TruckRow
      key={truckId}
      index={index}
      truck={truck}
    />
  );
})}

        </div>

        {/* PAGINATION */}

        <div
          style={{
            display: "flex",
            justifyContent:
              "space-between",
            alignItems: "center",
            padding: "16px 20px",
            borderTop:
              "1px solid rgba(255,255,255,0.08)",
          }}
        >

          <span
            style={{
              fontSize: "13px",
              opacity: 0.65,
            }}
          >
            Page {truckPage} of{" "}
            {filteredTrucks
              ? Math.max(
                  1,
                  Math.ceil(
                    filteredTrucks.length /
                      trucksPerPage
                  )
                )
              : totalPages}
          </span>

          <div
            style={{
              display: "flex",
              gap: "8px",
            }}
          >

            <button
              className="collapse-btn"
              disabled={truckPage <= 1}
              onClick={() =>
                setTruckPage((p) =>
                  Math.max(1, p - 1)
                )
              }
            >
              <ChevronLeft size={18} />
            </button>

            <button
              className="collapse-btn"
              disabled={
                truckPage >=
                (filteredTrucks
                  ? Math.max(
                      1,
                      Math.ceil(
                        filteredTrucks.length /
                          trucksPerPage
                      )
                    )
                  : totalPages)
              }
              onClick={() =>
                setTruckPage((p) =>
                  Math.min(
                    filteredTrucks
                      ? Math.max(
                          1,
                          Math.ceil(
                            filteredTrucks.length /
                              trucksPerPage
                          )
                        )
                      : totalPages,
                    p + 1
                  )
                )
              }
            >
              <ChevronRight size={18} />
            </button>

          </div>

        </div>

      </div>

    </section>
  );
}

/* =====================================================
   TRUCK ROW
===================================================== */

function TruckRow({ index, truck }) {
  const status =
    truck?.status === "Healthy"
      ? "Online"
      : "Offline";

  const temperature =
    truck?.temperature != null
      ? Number(truck.temperature).toFixed(1)
      : "--";

  const events =
    truck?.count ?? 0;

  const lastSeen =
    truck?.last_event
      ? new Date(
          truck.last_event
        ).toLocaleTimeString()
      : "--";

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns:
          "1.4fr 1fr 1fr 1fr 1fr 1fr",
        alignItems: "center",
        padding:
          "13px 20px",
        borderBottom:
          "1px solid rgba(255,255,255,0.055)",
        minHeight: "58px",
      }}
    >

      {/* TRUCK ID */}

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "11px",
        }}
      >

        <div
          className="worker-icon"
          style={{
            width: "34px",
            height: "34px",
          }}
        >
          <Truck size={17} />
        </div>

        <div>
          <strong
            style={{
              display: "block",
              fontSize: "14px",
            }}
          >
            TRUCK-
            {String(index).padStart(
              5,
              "0"
            )}
          </strong>

          <small
            style={{
              opacity: 0.55,
              fontSize: "11px",
            }}
          >
            Fleet vehicle
          </small>
        </div>

      </div>

      {/* STATUS */}

      <div>
        <span
          className={`worker-status ${
            status === "Online"
              ? "running"
              : "stopped"
          }`}
        >
          <span />
          {status}
        </span>
      </div>

      {/* TEMPERATURE */}

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "7px",
        }}
      >
        <Thermometer size={15} />
        <span>
          {temperature} °C
        </span>
      </div>

      {/* TELEMETRY */}

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "7px",
        }}
      >
        <Activity size={15} />
        <span>10 sec</span>
      </div>

      {/* EPS */}

      <div>
        {events} eps
      </div>

      {/* LAST SEEN */}

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "7px",
          opacity: 0.7,
        }}
      >
        <Clock3 size={14} />
         <span>
            {lastSeen}
          </span>
      </div>

    </div>
  );
}

/* =====================================================
   WORKERS PAGE
===================================================== */

function WorkersPage({
  workers,
  activeWorkers,
  totalWorkers,
  search,
}) {
  const filtered = workers.filter(
    (worker) =>
      `${worker.worker_id} ${worker.partition}`
        .toLowerCase()
        .includes(search.toLowerCase())
  );

  return (
    <section className="panel page-panel">

      <div className="panel-header">

        <div>
          <h2>
            Workers
          </h2>

          <p>
            Distributed processing workers
          </p>
        </div>

        <span className="view-all">
          {activeWorkers}/
          {totalWorkers} Healthy
        </span>

      </div>

      <div className="worker-list">

        {filtered.length > 0 ? (
          filtered.map((worker) => (
            <WorkerRow
              key={worker.worker_id}
              worker={worker}
            />
          ))
        ) : (
          <div className="empty-logs">

            <Server size={25} />

            <span>
              No worker data available
            </span>

            <small>
              Waiting for backend worker information
            </small>

          </div>
        )}

      </div>

    </section>
  );
}

/* =====================================================
   WORKER ROW
===================================================== */

function WorkerRow({ worker }) {
  const isRunning =
    worker.status === "Running" ||
    worker.status === "Healthy";

  return (
    <div className="worker-row">

      <div className="worker-info">

        <div className="worker-icon">
          <Server size={16} />
        </div>

        <div>

          <strong>
            {worker.worker_id}
          </strong>

          <small>
            Partition{" "}
            {worker.partition}
          </small>

        </div>

      </div>

      <div className="worker-stats">

        <span>
          {worker.events_per_sec ?? 0} eps
        </span>

        <span
          className={`worker-status ${
            isRunning
              ? "running"
              : "stopped"
          }`}
        >
          <span />
          {worker.status ||
            "Unknown"}
        </span>

      </div>

    </div>
  );
}

/* =====================================================
   TOPOLOGY PAGE
===================================================== */

function TopologyPage() {
  return (
    <section className="panel topology-panel page-panel">

      <div className="panel-header">

        <div>
          <h2>
            Stream Processing Topology
          </h2>

          <p>
            Kafka → Workers → Aggregator → RocksDB
          </p>
        </div>

        <div className="panel-live">
          <span />
          Live topology
        </div>

      </div>

      <div className="topology-container">
        <Topology />
      </div>

    </section>
  );
}

/* =====================================================
   ALERTS PAGE
===================================================== */

function AlertsPage({
  alerts,
  activeAlerts,
}) {
  return (
    <section className="panel page-panel">

      {/* HEADER */}

      <div className="panel-header">

        <div>
          <h2>
            System Alerts
          </h2>

          <p>
            Monitor system warnings, worker failures
            and processing alerts
          </p>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >

          <span
            className={`view-all ${
              activeAlerts > 0
                ? "alert-count"
                : ""
            }`}
          >
            {activeAlerts} Active
          </span>

          <AlertTriangle size={24} />

        </div>

      </div>

      {/* ALERT SUMMARY */}

      <div className="kpi-grid">

        <KpiCard
          title="Active Alerts"
          value={activeAlerts}
          icon={
            <AlertTriangle size={21} />
          }
          trend="Requires attention"
          className="orange"
        />

        <KpiCard
          title="Critical"
          value={
            alerts.filter(
              (a) =>
                a.severity ===
                "critical"
            ).length
          }
          icon={
            <XCircle size={21} />
          }
          trend="Critical system issues"
          className="purple"
        />

        <KpiCard
          title="Warnings"
          value={
            alerts.filter(
              (a) =>
                a.severity ===
                "warning"
            ).length
          }
          icon={
            <AlertCircle size={21} />
          }
          trend="Warnings detected"
          className="orange"
        />

        <KpiCard
          title="Resolved"
          value={
            alerts.filter(
              (a) =>
                a.severity ===
                "resolved"
            ).length
          }
          icon={
            <CheckCircle2 size={21} />
          }
          trend="Healthy checks"
          className="green"
        />

      </div>

      {/* ALERT LIST */}

      <div
        style={{
          marginTop: "25px",
        }}
      >

        <div
          style={{
            padding:
              "15px 20px",
            borderBottom:
              "1px solid rgba(255,255,255,0.07)",
            fontSize: "13px",
            opacity: 0.6,
          }}
        >
          SYSTEM MONITORING EVENTS
        </div>

        {alerts.map((alert) => (
          <AlertRow
            key={alert.id}
            alert={alert}
          />
        ))}

      </div>

    </section>
  );
}

/* =====================================================
   ALERT ROW
===================================================== */

function AlertRow({ alert }) {
  const isCritical =
    alert.severity === "critical";

  const isWarning =
    alert.severity === "warning";

  const isResolved =
    alert.severity === "resolved";

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent:
          "space-between",
        gap: "20px",
        padding:
          "20px",
        borderBottom:
          "1px solid rgba(255,255,255,0.06)",
      }}
    >

      <div
        style={{
          display: "flex",
          alignItems:
            "flex-start",
          gap: "15px",
        }}
      >

        <div
          style={{
            width: "40px",
            height: "40px",
            borderRadius: "10px",
            display: "flex",
            alignItems: "center",
            justifyContent:
              "center",
            background:
              isCritical
                ? "rgba(239,68,68,0.12)"
                : isWarning
                ? "rgba(245,158,11,0.12)"
                : "rgba(34,197,94,0.12)",
          }}
        >
          {isCritical ? (
            <XCircle size={20} />
          ) : isWarning ? (
            <AlertTriangle
              size={20}
            />
          ) : (
            <Check size={20} />
          )}
        </div>

        <div>

          <div
            style={{
              display: "flex",
              alignItems:
                "center",
              gap: "10px",
              marginBottom:
                "5px",
            }}
          >

            <strong>
              {alert.title}
            </strong>

            <span
              className={`alert-severity ${
                isCritical
                  ? "critical"
                  : isWarning
                  ? "warning"
                  : "resolved"
              }`}
            >
              {alert.severity ===
              "resolved"
                ? "RESOLVED"
                : alert.severity.toUpperCase()}
            </span>

          </div>

          <p
            style={{
              margin:
                "0 0 6px",
              fontSize: "13px",
              opacity: 0.65,
            }}
          >
            {alert.description}
          </p>

          <small
            style={{
              opacity: 0.45,
            }}
          >
            Source: {alert.source}
          </small>

        </div>

      </div>

      <div
        style={{
          display: "flex",
          alignItems:
            "center",
          gap: "7px",
          opacity: 0.55,
          fontSize: "12px",
          whiteSpace:
            "nowrap",
        }}
      >
        <Clock3 size={14} />
        {alert.time}
      </div>

    </div>
  );
}

/* =====================================================
   REPORTS PAGE
===================================================== */

function ReportsPage({
  metrics,
  activeWorkers,
}) {
  return (
    <section className="panel page-panel">

      <div className="panel-header">

        <div>
          <h2>
            Reports
          </h2>

          <p>
            Processing statistics and system performance
          </p>
        </div>

        <BarChart3 size={24} />

      </div>

      <div className="kpi-grid">

        <KpiCard
          title="Events Consumed"
          value={
            metrics?.events_consumed ?? 0
          }
          icon={
            <Activity size={21} />
          }
          trend="Total consumed"
          className="purple"
        />

        <KpiCard
          title="Events Processed"
          value={
            metrics?.events_processed ?? 0
          }
          icon={
            <CheckCircle2 size={21} />
          }
          trend="Successfully processed"
          className="green"
        />

        <KpiCard
          title="Events Filtered"
          value={
            metrics?.events_filtered ?? 0
          }
          icon={
            <XCircle size={21} />
          }
          trend="Filtered events"
          className="orange"
        />

        <KpiCard
          title="Active Workers"
          value={activeWorkers}
          icon={
            <Users size={21} />
          }
          trend="Currently active"
          className="blue"
        />

      </div>

      <div className="metric-list">

        <MetricRow
          label="Events / Second"
          value={
            metrics?.events_per_second ?? 0
          }
          icon={<Zap size={17} />}
        />

        <MetricRow
          label="Processing Lag"
          value={`${
            metrics?.processing_lag_seconds ?? 0
          }s`}
          icon={<Gauge size={17} />}
        />

      </div>

    </section>
  );
}

/* =====================================================
   STATE STORAGE
===================================================== */

function StateStoragePage({
  activeWorkers,
}) {
  return (
    <section className="panel page-panel">

      <div className="panel-header">

        <div>
          <h2>
            State Storage
          </h2>

          <p>
            RocksDB state storage and persistence
          </p>
        </div>

        <Database size={24} />

      </div>

      <div className="metric-list">

        <MetricRow
          label="Storage Engine"
          value="RocksDB"
          icon={
            <Database size={17} />
          }
        />

        <MetricRow
          label="State Management"
          value="Active"
          icon={
            <CheckCircle2 size={17} />
          }
        />

        <MetricRow
          label="Active Workers"
          value={activeWorkers}
          icon={
            <Users size={17} />
          }
        />

        <MetricRow
          label="Persistence"
          value="Enabled"
          icon={
            <Database size={17} />
          }
        />

      </div>

    </section>
  );
}

/* =====================================================
   SETTINGS
===================================================== */

function SettingsPage({
  kafkaConnected,
}) {
  return (
    <section className="panel page-panel">

      <div className="panel-header">

        <div>
          <h2>
            Settings
          </h2>

          <p>
            StreamForge system configuration
          </p>
        </div>

        <Settings size={24} />

      </div>

      <div className="metric-list">

        <MetricRow
          label="Backend"
          value="FastAPI"
          icon={
            <Server size={17} />
          }
        />

        <MetricRow
          label="Message Broker"
          value="Kafka"
          icon={
            <Network size={17} />
          }
        />

        <MetricRow
          label="State Storage"
          value="RocksDB"
          icon={
            <Database size={17} />
          }
        />

        <MetricRow
          label="Frontend"
          value="React + Vite"
          icon={
            <Activity size={17} />
          }
        />

        <MetricRow
          label="Kafka Status"
          value={
            kafkaConnected
              ? "Connected"
              : "Disconnected"
          }
          icon={
            kafkaConnected ? (
              <Wifi size={17} />
            ) : (
              <WifiOff size={17} />
            )
          }
        />

      </div>

    </section>
  );
}

/* =====================================================
   PAGE DESCRIPTION
===================================================== */

function getPageDescription(page) {
  const descriptions = {
    Trucks:
      "Monitor and manage connected trucks and telemetry data.",

    Workers:
      "Monitor distributed processing workers.",

    Topology:
      "Live Kafka → Workers → Aggregator → RocksDB processing topology.",

    Alerts:
      "Monitor system warnings, worker failures and processing alerts.",

    Reports:
      "View processing statistics and system performance reports.",

    "State Storage":
      "Monitor RocksDB state storage and persisted stream processing state.",

    Settings:
      "Configure StreamForge system and processing settings.",
  };

  return (
    descriptions[page] ||
    "StreamForge distributed event processing"
  );
}

/* =====================================================
   KPI CARD
===================================================== */

function KpiCard({
  title,
  value,
  icon,
  trend,
  className,
}) {
  return (
    <div className="kpi-card">

      <div
        className={`kpi-icon ${className}`}
      >
        {icon}
      </div>

      <div className="kpi-content">

        <span>
          {title}
        </span>

        <strong>
          {value}
        </strong>

        <small>
          {trend}
        </small>

      </div>

      <div className="kpi-decoration" />

    </div>
  );
}

/* =====================================================
   METRIC ROW
===================================================== */

function MetricRow({
  label,
  value,
  icon,
}) {
  return (
    <div className="metric-row">

      <div className="metric-label">

        <span className="metric-icon">
          {icon}
        </span>

        {label}

      </div>

      <strong>
        {value}
      </strong>

    </div>
  );
}

/* =====================================================
   EXPORT
===================================================== */

export default App;