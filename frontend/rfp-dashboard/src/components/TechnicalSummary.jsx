import { useEffect, useState } from "react";
import { fetchTechnicalSummary } from "../api";

export default function TechnicalSummary() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchTechnicalSummary().then(setData);
  }, []);

  return (
    <div className="card">
      <h2>Technical Summary</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
