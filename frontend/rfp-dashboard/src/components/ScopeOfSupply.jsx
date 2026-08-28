export default function ScopeOfSupply({ data }) {
  return (
    <div className="card">
      <h2>Scope of Supply</h2>
      {data ? (
        <pre>{JSON.stringify(data, null, 2)}</pre>
      ) : (
        <p>Upload an RFP to see the scope of supply.</p>
      )}
    </div>
  );
}
