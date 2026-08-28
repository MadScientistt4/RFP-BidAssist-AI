import Badge from "./Badge";

const CONFIG = {
  idle: { tone: "neutral", label: "No active RFP" },
  loading: { tone: "accent", label: "Processing..." },
  done: { tone: "success", label: "Pipeline complete" },
  error: { tone: "danger", label: "Pipeline failed" },
};

export default function StatusBadge({ status }) {
  const { tone, label } = CONFIG[status] ?? CONFIG.idle;
  return (
    <Badge tone={tone}>
      {status === "loading" && (
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-indigo-600" />
      )}
      {label}
    </Badge>
  );
}
