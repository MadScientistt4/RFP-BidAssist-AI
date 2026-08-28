import { useState } from "react";
import { scanRfps } from "../api";
import useRfp from "../context/useRfp";
import Card from "../components/ui/Card";
import Badge from "../components/ui/Badge";
import DataTable from "../components/ui/DataTable";

export default function SalesPage() {
  const { status, runFromFile, runFromSelectedRfp } = useRfp();
  const pipelineRunning = status === "loading";

  const [scanning, setScanning] = useState(false);
  const [scanError, setScanError] = useState(null);
  const [scanResult, setScanResult] = useState(null);

  const [file, setFile] = useState(null);

  const handleScan = async () => {
    setScanning(true);
    setScanError(null);
    try {
      setScanResult(await scanRfps());
    } catch (err) {
      setScanError(err.response?.data?.detail ?? err.message);
    } finally {
      setScanning(false);
    }
  };

  const selected = scanResult?.selected_rfp;
  const selectedPdfPath = scanResult?.selected_rfp_pdf_path;

  const handleUpload = () => {
    if (!file) return;
    runFromFile(file);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Sales — RFP Identification</h1>
        <p className="mt-1 text-sm text-slate-500">
          Scan tender portals for RFPs due in the next 3 months, or upload one manually.
        </p>
      </div>

      <Card
        title="Sales Agent — Portal Scan"
        subtitle="Scans predefined tender-listing URLs; no model call, safe to run anytime."
        actions={
          <button
            onClick={handleScan}
            disabled={scanning}
            className="rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
          >
            {scanning ? "Scanning..." : "Scan for RFPs"}
          </button>
        }
      >
        {scanError && <p className="mb-3 text-sm text-red-600">{scanError}</p>}

        {!scanResult && !scanning && (
          <p className="text-sm text-slate-500">
            No scan run yet. Click "Scan for RFPs" to check the configured portals.
          </p>
        )}

        {scanResult && (
          <div className="space-y-4">
            <p className="text-sm text-slate-600">
              Found <strong>{scanResult.total_rfps_found}</strong> tender(s) across{" "}
              <strong>{scanResult.scanned_urls.length}</strong> portal(s) —{" "}
              <strong>{scanResult.rfps_due_in_window.length}</strong> due within 3 months.
            </p>

            <DataTable
              columns={[
                { key: "rfp_id", label: "RFP ID" },
                { key: "title", label: "Title" },
                { key: "deadline", label: "Deadline" },
                {
                  key: "days_remaining",
                  label: "Days Left",
                  render: (r) => (
                    <Badge tone={r.days_remaining <= 14 ? "warning" : "neutral"}>
                      {r.days_remaining}d
                    </Badge>
                  ),
                },
                {
                  key: "product_fit",
                  label: "In Scope",
                  render: (r) => (
                    <Badge tone={r.product_fit ? "success" : "neutral"}>
                      {r.product_fit ? "Yes" : "No"}
                    </Badge>
                  ),
                },
              ]}
              rows={scanResult.rfps_due_in_window}
              rowKey={(r) => r.rfp_id}
              emptyMessage="No RFPs found within the next 3 months."
            />

            {selected ? (
              <div className="rounded-lg border border-indigo-200 bg-indigo-50 p-4">
                <p className="text-sm font-medium text-indigo-900">
                  Selected for response: {selected.rfp_id}
                </p>
                <p className="mt-1 text-sm text-indigo-800">{selected.title}</p>
                <p className="mt-1 text-xs text-indigo-700">
                  Due in {selected.days_remaining} day(s), on {selected.deadline}
                </p>
                <button
                  onClick={() => runFromSelectedRfp(selectedPdfPath, `${selected.rfp_id}`)}
                  disabled={!selectedPdfPath || pipelineRunning}
                  className="mt-3 rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
                >
                  {pipelineRunning ? "Processing..." : "Run Technical + Pricing Pipeline"}
                </button>
                {!selectedPdfPath && (
                  <p className="mt-2 text-xs text-indigo-700">
                    No document is linked for this notice yet — in production this would
                    first download the RFP PDF from the portal link.
                  </p>
                )}
              </div>
            ) : (
              <p className="text-sm text-slate-500">
                No in-scope RFP found within the next 3 months.
              </p>
            )}
          </div>
        )}
      </Card>

      <Card
        title="Manual Upload"
        subtitle="Fallback path — upload an RFP PDF directly without the portal scan."
      >
        <div className="flex flex-wrap items-center gap-3">
          <input
            type="file"
            accept=".pdf"
            disabled={pipelineRunning}
            onChange={(e) => setFile(e.target.files[0])}
            className="text-sm text-slate-600 file:mr-3 file:rounded-lg file:border-0 file:bg-slate-100 file:px-3 file:py-2 file:text-sm file:font-medium file:text-slate-700 hover:file:bg-slate-200"
          />
          <button
            onClick={handleUpload}
            disabled={!file || pipelineRunning}
            className="rounded-lg bg-slate-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
          >
            {pipelineRunning ? "Processing..." : "Run Pipeline"}
          </button>
        </div>
      </Card>
    </div>
  );
}
