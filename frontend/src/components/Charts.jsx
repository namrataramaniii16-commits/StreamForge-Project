import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const data = [
  { day: "Mon", trips: 40 },
  { day: "Tue", trips: 52 },
  { day: "Wed", trips: 48 },
  { day: "Thu", trips: 61 },
  { day: "Fri", trips: 57 },
  { day: "Sat", trips: 39 },
];

function Charts() {
  return (
    <div className="chart-container">
      <h2>Trips This Week</h2>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <XAxis dataKey="day" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="trips" fill="#00c8ff" radius={[8,8,0,0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default Charts;