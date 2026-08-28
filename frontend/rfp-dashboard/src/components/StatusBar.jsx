const LABELS = {
  idle: "Backend Connected • Waiting for an RFP",
  loading: "Running Sales -> Technical -> Pricing pipeline...",
  done: "Pipeline complete",
  error: "Pipeline failed",
};

export default function StatusBar({ status = "idle", error }) {
  return (
    <div className="card">
      <strong>Status:</strong> {LABELS[status] ?? status}
      {status === "error" && error ? ` — ${error}` : ""}
    </div>
  );
}
