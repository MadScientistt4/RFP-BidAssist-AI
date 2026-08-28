import { useState } from "react";
import { runRfp, runSelectedRfp } from "../api";
import SalesAgentPanel from "../components/SalesAgentPanel";
import UploadPanel from "../components/UploadPanel";
import StatusBar from "../components/StatusBar";
import TechnicalSummary from "../components/TechnicalSummary";
import ScopeOfSupply from "../components/ScopeOfSupply";
import SpecMatchTable from "../components/SpecMatchTable";
import OEMRecommendations from "../components/OEMRecommendations";
import PricingSummary from "../components/PricingSummary";

export default function Dashboard() {
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const runPipeline = async (pipelineCall) => {
    setStatus("loading");
    setError(null);

    try {
      const data = await pipelineCall();
      setResult(data);
      setStatus("done");
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message);
      setStatus("error");
    }
  };

  const handleUpload = (file) => runPipeline(() => runRfp(file));
  const handleRunSelected = (pdfPath) => runPipeline(() => runSelectedRfp(pdfPath));

  const technicalAgentOutput = result?.technical_agent_output;

  return (
    <div className="container">
      <h1>RFP BidAssist AI – Dashboard</h1>
      <StatusBar status={status} error={error} />
      <SalesAgentPanel
        onRunSelected={handleRunSelected}
        pipelineRunning={status === "loading"}
      />
      <UploadPanel onUpload={handleUpload} status={status} />
      <TechnicalSummary data={result?.technical_summary} />
      <ScopeOfSupply data={technicalAgentOutput?.scope_of_supply_summary} />
      <OEMRecommendations data={technicalAgentOutput?.top_3_oems} />
      <SpecMatchTable rows={technicalAgentOutput?.final_recommendation_table} />
      <PricingSummary data={result?.final_priced_output} />
    </div>
  );
}
