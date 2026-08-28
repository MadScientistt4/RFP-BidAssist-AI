import { BrowserRouter, Routes, Route } from "react-router-dom";
import { RfpProvider } from "./context/RfpContext";
import Layout from "./components/layout/Layout";
import SalesPage from "./pages/SalesPage";
import TechnicalPage from "./pages/TechnicalPage";
import PricingPage from "./pages/PricingPage";
import ResponsePage from "./pages/ResponsePage";

function App() {
  return (
    <RfpProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<SalesPage />} />
            <Route path="technical" element={<TechnicalPage />} />
            <Route path="pricing" element={<PricingPage />} />
            <Route path="response" element={<ResponsePage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </RfpProvider>
  );
}

export default App;
