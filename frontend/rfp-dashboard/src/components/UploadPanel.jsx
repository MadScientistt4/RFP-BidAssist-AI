import { useState } from "react";

export default function UploadPanel({ onUpload, status }) {
  const [file, setFile] = useState(null);
  const loading = status === "loading";

  const handleUpload = () => {
    if (!file) return alert("Select a PDF");
    onUpload(file);
  };

  return (
    <div className="card">
      <h2>Upload RFP PDF</h2>
      <input
        type="file"
        accept=".pdf"
        disabled={loading}
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Processing..." : "Upload"}
      </button>
    </div>
  );
}
