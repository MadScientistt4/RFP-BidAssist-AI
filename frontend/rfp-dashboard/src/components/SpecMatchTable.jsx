import { useEffect, useState } from "react";
import { fetchSpecMatch } from "../api";

export default function SpecMatchTable() {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    fetchSpecMatch().then(setRows);
  }, []);

  return (
    <div className="card">
      <h2>Spec Match Table</h2>
      <table border="1" width="100%">
        <thead>
          <tr>
            <th>RFP Item</th>
            <th>OEM SKU</th>
            <th>Spec Match %</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              <td>{r.rfp_item}</td>
              <td>{r.oem_sku}</td>
              <td>{r.match_percent}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
