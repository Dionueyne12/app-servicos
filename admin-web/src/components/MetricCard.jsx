export default function MetricCard({ title, value, hint, tone = "blue" }) {
  return (
    <article className={`metric-card ${tone}`}>
      <span className="metric-title">{title}</span>
      <strong>{value}</strong>
      {hint ? <small>{hint}</small> : null}
    </article>
  );
}
