function ChartBox({ title, children }) {
  return (
    <div className="vrs-card">
      <h3 className="vrs-heading">{title}</h3>
      {children}
    </div>
  );
}

export default ChartBox;