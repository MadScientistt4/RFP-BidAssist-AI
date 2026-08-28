import { useContext } from "react";
import RfpContext from "./rfpContextInstance";

export default function useRfp() {
  const ctx = useContext(RfpContext);
  if (!ctx) throw new Error("useRfp must be used within RfpProvider");
  return ctx;
}
