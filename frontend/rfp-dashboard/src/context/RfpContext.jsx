import { useState } from "react";
import { runRfp, runSelectedRfp } from "../api";
import RfpContext from "./rfpContextInstance";

export function RfpProvider({ children }) {
  const [status, setStatus] = useState("idle"); // idle | loading | done | error
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [source, setSource] = useState(null); // { type: "upload" | "sales-agent", label }

  const execute = async (call, sourceMeta) => {
    setStatus("loading");
    setError(null);
    setSource(sourceMeta);
    try {
      const data = await call();
      setResult(data);
      setStatus("done");
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message ?? "Something went wrong");
      setStatus("error");
    }
  };

  const runFromFile = (file) =>
    execute(() => runRfp(file), { type: "upload", label: file.name });

  const runFromSelectedRfp = (pdfPath, label) =>
    execute(() => runSelectedRfp(pdfPath), { type: "sales-agent", label });

  const reset = () => {
    setStatus("idle");
    setError(null);
    setResult(null);
    setSource(null);
  };

  const value = { status, error, result, source, runFromFile, runFromSelectedRfp, reset };

  return <RfpContext.Provider value={value}>{children}</RfpContext.Provider>;
}
