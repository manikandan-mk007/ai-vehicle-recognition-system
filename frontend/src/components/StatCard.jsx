function StatCard({ title, value, subtitle }) {
  return (
    <div className="vrs-stat">
      <p className="vrs-stat__label">{title}</p>
      <h2 className="vrs-stat__value">{value ?? 0}</h2>
      {subtitle && (
        <p style={{ fontSize: "12px", color: "#6b7280", marginTop: "6px" }}>
          {subtitle}
        </p>
      )}
    </div>
  );
}

export default StatCard;