export default function OEMRecommendations({ data = [] }) {
  return (
    <div className="card">
      <h2>Top OEM Recommendations</h2>
      {data.length === 0 ? (
        <p>Upload an RFP to see ranked OEM SKU recommendations.</p>
      ) : (
        <table border="1" width="100%">
          <thead>
            <tr>
              <th>Rank</th>
              <th>OEM SKU</th>
              <th>Spec Match %</th>
            </tr>
          </thead>
          <tbody>
            {data.map((oem, i) => (
              <tr key={oem.product_sku}>
                <td>#{i + 1}</td>
                <td>{oem.product_sku}</td>
                <td>{oem.spec_match_pct}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
