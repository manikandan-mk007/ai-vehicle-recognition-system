import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from "recharts";

import API from "../api/axiosInstance";
import StatCard from "../components/StatCard";
import ChartBox from "../components/ChartBox";

const CHART_TOOLTIP_STYLE = {
  backgroundColor: "#0a0000",
  border: "1px solid #3D0000",
  borderRadius: "8px",
  color: "#e5e7eb",
  fontFamily: "'Rajdhani', sans-serif",
  fontSize: "13px",
};

const PIE_COLORS = ["#FF0000", "#950101", "#3D0000", "#CC0000", "#7a0000"];

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [charts, setCharts] = useState(null);
  const [recent, setRecent] = useState([]);

  const fetchDashboardData = async () => {
    const summaryRes = await API.get("/analytics/summary");
    const chartRes   = await API.get("/analytics/charts");
    const recentRes  = await API.get("/analytics/recent");

    setSummary(summaryRes.data.data);
    setCharts(chartRes.data.data);
    setRecent(recentRes.data.data);
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (!summary || !charts) {
    return (
      <div style={{ padding: "3rem 2rem", display: "flex", alignItems: "center", gap: "12px" }}>
        <span className="vrs-spinner" />
        <span style={{ color: "#6b7280", letterSpacing: "0.08em", textTransform: "uppercase", fontSize: "13px" }}>
          Loading dashboard...
        </span>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem", display: "flex", flexDirection: "column", gap: "2rem" }}>
      {/* Header */}
      <div>
        <h1 className="vrs-page-title">Dashboard</h1>
        <p className="vrs-page-sub">Overview of vehicle, person and number plate detections</p>
      </div>

      {/* Stat cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "1rem" }}>
        <StatCard title="Sessions"       value={summary.total_sessions} />
        <StatCard title="Vehicles"       value={summary.total_vehicles} />
        <StatCard title="Persons"        value={summary.total_persons} />
        <StatCard title="Number Plates"  value={summary.total_plates} />
        <StatCard title="Readable Plates"value={summary.readable_plates} />
      </div>

      {/* Charts row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1.25rem" }}>
        <ChartBox title="Vehicle Type Counts">
          <div style={{ height: "280px" }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.vehicle_type_counts}>
                <XAxis dataKey="label" stroke="#4b0000" tick={{ fill: "#6b7280", fontSize: 12 }} />
                <YAxis stroke="#4b0000" tick={{ fill: "#6b7280", fontSize: 12 }} />
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} cursor={{ fill: "rgba(149,1,1,0.1)" }} />
                <Bar dataKey="count" fill="#950101" radius={[6, 6, 0, 0]}
                  activeBar={{ fill: "#FF0000" }} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartBox>

        <ChartBox title="Person Type Counts">
          <div style={{ height: "280px" }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={charts.person_type_counts}
                  dataKey="count"
                  nameKey="type"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  innerRadius={40}
                  label={(entry) => `${entry.type}: ${entry.count}`}
                  labelLine={{ stroke: "#3D0000" }}
                >
                  {charts.person_type_counts.map((_, index) => (
                    <Cell key={index} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </ChartBox>
      </div>

      {/* Top vehicle models */}
      <ChartBox title="Top Vehicle Models">
        <div style={{ height: "280px" }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={charts.vehicle_model_counts}>
              <XAxis dataKey="model" stroke="#4b0000" tick={{ fill: "#6b7280", fontSize: 12 }} />
              <YAxis stroke="#4b0000" tick={{ fill: "#6b7280", fontSize: 12 }} />
              <Tooltip contentStyle={CHART_TOOLTIP_STYLE} cursor={{ fill: "rgba(149,1,1,0.1)" }} />
              <Bar dataKey="count" fill="#3D0000" radius={[6, 6, 0, 0]}
                activeBar={{ fill: "#FF0000" }} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </ChartBox>

      {/* Recent detections table */}
      <div className="vrs-card">
        <h3 className="vrs-heading">Recent Detections</h3>
        <div style={{ overflowX: "auto" }}>
          <table className="vrs-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Vehicles</th>
                <th>Persons</th>
                <th>Plates</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {recent.map((item) => (
                <tr key={item.id}>
                  <td className="id-cell">#{item.id}</td>
                  <td>
                    <span className="vrs-badge vrs-badge--gray" style={{ textTransform: "capitalize" }}>
                      {item.input_type}
                    </span>
                  </td>
                  <td style={{ fontFamily: "'JetBrains Mono', monospace" }}>{item.total_vehicles}</td>
                  <td style={{ fontFamily: "'JetBrains Mono', monospace" }}>{item.total_persons}</td>
                  <td style={{ fontFamily: "'JetBrains Mono', monospace" }}>{item.total_number_plates}</td>
                  <td style={{ color: "#6b7280", fontSize: "13px" }}>
                    {new Date(item.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;