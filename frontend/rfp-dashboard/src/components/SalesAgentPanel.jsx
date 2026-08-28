import { useState } from "react";
import { scanRfps } from "../api";

export default function SalesAgentPanel({ onRunSelected, pipelineRunning }) {
  const [scanning, setScanning] = useState(false);
  const [scanError, setScanError] = useState(null);
  const [scanResult, setScanResult] = useState(null);

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

  return (
    <div className="card">
      <h2>Sales Agent — RFP Identification</h2>
      <p>Scans predefined tender portals for RFPs due in the next 3 months.</p>

      <button onClick={handleScan} disabled={scanning}>
        {scanning ? "Scanning portals..." : "Scan for RFPs"}
      </button>

      {scanError && <p style={{ color: "red" }}>{scanError}</p>}

      {scanResult && (
        <>
          <p>
            Found {scanResult.total_rfps_found} tender(s) across{" "}
            {scanResult.scanned_urls.length} portal(s) —{" "}
            {scanResult.rfps_due_in_window.length} due within 3 months.
          </p>

          <table border="1" width="100%">
            <thead>
              <tr>
                <th>RFP ID</th>
                <th>Title</th>
                <th>Deadline</th>
                <th>Days Left</th>
                <th>In Scope</th>
              </tr>
            </thead>
            <tbody>
              {scanResult.rfps_due_in_window.map((r) => (
                <tr
                  key={r.rfp_id}
                  style={
                    selected && r.rfp_id === selected.rfp_id
                      ? { fontWeight: "bold" }
                      : undefined
                  }
                >
                  <td>{r.rfp_id}</td>
                  <td>{r.title}</td>
                  <td>{r.deadline}</td>
                  <td>{r.days_remaining}</td>
                  <td>{r.product_fit ? "Yes" : "No"}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {selected ? (
            <div style={{ marginTop: "1rem" }}>
              <p>
                <strong>Selected for response:</strong> {selected.rfp_id} —{" "}
                {selected.title} (due in {selected.days_remaining} days)
              </p>
              <button
                onClick={() => onRunSelected(selectedPdfPath)}
                disabled={!selectedPdfPath || pipelineRunning}
              >
                {pipelineRunning
                  ? "Processing..."
                  : "Run Technical + Pricing Pipeline on this RFP"}
              </button>
              {!selectedPdfPath && (
                <p>
                  No document is linked for this notice yet — in production
                  this would first download the RFP PDF from the portal link.
                </p>
              )}
            </div>
          ) : (
            <p>No RFP in scope was found within the next 3 months.</p>
          )}
        </>
      )}
    </div>
  );
}
