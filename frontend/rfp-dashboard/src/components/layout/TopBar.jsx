import useRfp from "../../context/useRfp";
import StatusBadge from "../ui/StatusBadge";

export default function TopBar() {
  const { status, error, result, source } = useRfp();

  const title =
    result?.extracted_rfp?.rfp_metadata?.rfp_title ||
    source?.label ||
    "No active RFP";

  return (
    <header className="print:hidden-force flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
      <div>
        <p className="text-sm font-semibold text-slate-900">{title}</p>
        {error && status === "error" && (
          <p className="mt-0.5 text-xs text-red-600">{error}</p>
        )}
      </div>
      <StatusBadge status={status} />
    </header>
  );
}
