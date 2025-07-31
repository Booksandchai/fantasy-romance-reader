import { PieChart, Pie, Tooltip, Legend } from "recharts";

export default function StatsChart({ data }) {
  if (data.length === 0) return <div>No stats yet.</div>;
  return (
    <PieChart width={250} height={220}>
      <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label />
      <Tooltip />
      <Legend verticalAlign="bottom" height={36} />
    </PieChart>
  );
}
