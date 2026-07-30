function ActivityPanel() {
  const activities = [
    "🚚 TRK001 reached Pune",
    "⛽ TRK003 fuel dropped below 20%",
    "🟢 TRK002 started moving",
    "⚠️ High engine temperature detected",
    "📍 TRK004 entered Mumbai",
  ];

  return (
    <div className="activity-panel">
      <h2>Recent Activity</h2>

      {activities.map((activity, index) => (
        <div className="activity-item" key={index}>
          {activity}
        </div>
      ))}
    </div>
  );
}

export default ActivityPanel;