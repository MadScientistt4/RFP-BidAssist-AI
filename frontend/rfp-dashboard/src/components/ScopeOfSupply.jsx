import { useEffect, useState } from "react";
import { fetchScopeOfSupply } from "../api";

export default function ScopeOfSupply() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchScopeOfSupply().then(setData);
  }, []);

  return (
    <div className="card">
      <h2>Scope of Supply</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
