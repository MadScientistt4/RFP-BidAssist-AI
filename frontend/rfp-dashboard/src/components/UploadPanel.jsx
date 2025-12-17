import { uploadRFP } from "../api";
import { useState } from "react";

export default function UploadPanel() {
  const [file, setFile] = useState(null);

  const handleUpload = async () => {
    if (!file) return alert("Select a PDF");
    await uploadRFP(file);
    alert("RFP Uploaded & Processed");
  };

  return (
    <div className="card">
      <h2>Upload RFP PDF</h2>
      <input type="file" accept=".pdf" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload}>Upload</button>
    </div>
  );
}
