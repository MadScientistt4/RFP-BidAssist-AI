import axios from "axios";

const API_BASE = "http://localhost:8000";

export const runRfp = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await axios.post(`${API_BASE}/run-rfp`, formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });

  return res.data;
};

export const scanRfps = async () => {
  const res = await axios.get(`${API_BASE}/scan-rfps`);
  return res.data;
};

export const runSelectedRfp = async (pdfPath) => {
  const res = await axios.post(`${API_BASE}/run-selected-rfp`, {
    pdf_path: pdfPath
  });
  return res.data;
};
