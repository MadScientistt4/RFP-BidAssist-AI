import UploadPanel from "../components/UploadPanel";
import StatusBar from "../components/StatusBar";
import TechnicalSummary from "../components/TechnicalSummary";
import ScopeOfSupply from "../components/ScopeOfSupply";
import SpecMatchTable from "../components/SpecMatchTable";
import OEMRecommendations from "../components/OEMRecommendations";

export default function Dashboard() {
  return (
    <div className="container">
      <h1>RFP BidAssist AI – Dashboard</h1>
      <StatusBar />
      <UploadPanel />
      <TechnicalSummary />
      <ScopeOfSupply />
      <SpecMatchTable />
      <OEMRecommendations />
    </div>
  );
}
