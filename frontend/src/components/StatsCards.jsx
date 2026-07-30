function StatsCards() {
  const stats = [
    {
      title: "Total Trucks",
      value: "50",
      icon: "🚚",
    },
    {
      title: "Moving",
      value: "38",
      icon: "🟢",
    },
    {
      title: "Idle",
      value: "8",
      icon: "🅿️",
    },
    {
      title: "Alerts",
      value: "4",
      icon: "⚠️",
    },
  ];

  return (
    <div className="stats-container">
      {stats.map((item, index) => (
        <div className="card" key={index}>
          <div className="card-icon">{item.icon}</div>

          <h2>{item.value}</h2>

          <h3>{item.title}</h3>
        </div>
      ))}
    </div>
  );
}

export default StatsCards;