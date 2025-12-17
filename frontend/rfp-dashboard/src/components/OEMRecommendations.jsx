import { useEffect, useState } from "react";
import { fetchOEMRecommendations } from "../api";

export default function OEMRecommendations() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetchOEMRecommendations().then(setData);
  }, []);

  return (
    <div className="card">
      <h2>OEM Recommendations</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
