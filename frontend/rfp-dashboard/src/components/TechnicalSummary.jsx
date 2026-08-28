export default function TechnicalSummary({ data }) {
  return (
    <div className="card">
      <h2>Technical Summary</h2>
      {data ? (
        <pre>{JSON.stringify(data, null, 2)}</pre>
      ) : (
        <p>Upload an RFP to see the technical context summary.</p>
      )}
    </div>
  );
}
