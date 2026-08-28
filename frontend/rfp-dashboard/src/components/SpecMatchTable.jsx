export default function SpecMatchTable({ rows = [] }) {
  return (
    <div className="card">
      <h2>Spec Match Table</h2>
      {rows.length === 0 ? (
        <p>Upload an RFP to see OEM spec-match results.</p>
      ) : (
        <table border="1" width="100%">
          <thead>
            <tr>
              <th>RFP Item</th>
              <th>Recommended OEM SKU</th>
              <th>Spec Match %</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i}>
                <td>{r.rfp_product_name}</td>
                <td>{r.recommended_oem_sku}</td>
                <td>{r.spec_match_pct}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
