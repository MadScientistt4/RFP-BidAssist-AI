export default function PricingSummary({ data }) {
  return (
    <div className="card">
      <h2>Pricing Summary</h2>
      {!data ? (
        <p>Upload an RFP to see the consolidated price and test costs.</p>
      ) : (
        <>
          <table border="1" width="100%">
            <thead>
              <tr>
                <th>Item</th>
                <th>SKU</th>
                <th>Qty</th>
                <th>Unit Price</th>
                <th>Material Cost</th>
                <th>Test Cost</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {data.priced_items.map((item) => (
                <tr key={item.item_id}>
                  <td>{item.item_name}</td>
                  <td>{item.sku}</td>
                  <td>{item.quantity} {item.unit}</td>
                  <td>{item.unit_price}</td>
                  <td>{item.base_material_cost}</td>
                  <td>{item.total_test_cost}</td>
                  <td>{item.total_item_cost}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p>
            <strong>Grand Total ({data.currency}):</strong> {data.grand_total}
          </p>
        </>
      )}
    </div>
  );
}
