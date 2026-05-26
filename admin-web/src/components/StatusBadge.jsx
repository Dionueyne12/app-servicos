export default function StatusBadge({ value, tone }) {
  return <span className={`status ${tone || toneFromValue(value)}`}>{format(value)}</span>;
}

function toneFromValue(value) {
  const normalized = String(value || "").toLowerCase();
  if (normalized.includes("critico") || normalized.includes("recus") || normalized.includes("cancel")) return "danger";
  if (normalized.includes("pendente") || normalized.includes("analise") || normalized.includes("aguard")) return "warning";
  if (normalized.includes("aprov") || normalized.includes("conclu") || normalized.includes("ok")) return "success";
  return "neutral";
}

function format(value) {
  return value ? String(value).replaceAll("_", " ") : "sem status";
}
