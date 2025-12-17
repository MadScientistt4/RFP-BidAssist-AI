import axios from "axios";

const API_BASE = "http://localhost:8000";

export const uploadRFP = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await axios.post(`${API_BASE}/upload-rfp`, formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });

  return res.data;
};

export const fetchTechnicalSummary = async () => {
  const res = await axios.get(`${API_BASE}/technical-summary`);
  return res.data;
};

export const fetchScopeOfSupply = async () => {
  const res = await axios.get(`${API_BASE}/scope-of-supply`);
  return res.data;
};

export const fetchSpecMatch = async () => {
  const res = await axios.get(`${API_BASE}/spec-match`);
  return res.data;
};

export const fetchOEMRecommendations = async () => {
  const res = await axios.get(`${API_BASE}/oem-recommendations`);
  return res.data;
};
