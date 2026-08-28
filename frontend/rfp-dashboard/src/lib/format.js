export function humanizeKey(key) {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function formatValue(value) {
  if (value === null || value === undefined || value === "") return "—";

  if (Array.isArray(value)) {
    return value.length ? value.map(formatValue).join(", ") : "—";
  }

  if (typeof value === "object") {
    // Common RFP spec shape: { exact, min, max }
    const { exact, min, max } = value;
    if (exact !== undefined || min !== undefined || max !== undefined) {
      if (exact !== null && exact !== undefined) return `${exact}`;
      if (min !== null && min !== undefined && max !== null && max !== undefined) {
        return `${min} – ${max}`;
      }
      if (min !== null && min !== undefined) return `>= ${min}`;
      if (max !== null && max !== undefined) return `<= ${max}`;
      return "—";
    }
    return null; // signal "not a simple value" to callers
  }

  return String(value);
}

export function formatCurrency(amount, currency = "INR") {
  if (amount === null || amount === undefined || Number.isNaN(amount)) return "—";
  try {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency,
      maximumFractionDigits: 2,
    }).format(amount);
  } catch {
    return `${currency} ${amount}`;
  }
}

export function matchTone(pct) {
  if (pct === null || pct === undefined) return "neutral";
  if (pct >= 90) return "success";
  if (pct >= 70) return "warning";
  return "danger";
}
