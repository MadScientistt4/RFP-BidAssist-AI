import { humanizeKey, formatValue } from "../../lib/format";

export default function DataView({ data, depth = 0 }) {
  if (data === null || data === undefined) {
    return <span className="text-slate-400">—</span>;
  }

  if (Array.isArray(data)) {
    if (data.length === 0) return <span className="text-slate-400">—</span>;

    const allPrimitive = data.every((v) => typeof v !== "object" || v === null);
    if (allPrimitive) {
      return (
        <ul className="list-disc space-y-0.5 pl-4 text-sm text-slate-700">
          {data.map((v, i) => (
            <li key={i}>{String(v)}</li>
          ))}
        </ul>
      );
    }

    return (
      <div className="space-y-3">
        {data.map((item, i) => (
          <div key={i} className="rounded-lg border border-slate-200 p-3">
            <DataView data={item} depth={depth + 1} />
          </div>
        ))}
      </div>
    );
  }

  if (typeof data === "object") {
    const simple = formatValue(data);
    if (simple !== null) return <span className="text-sm text-slate-700">{simple}</span>;

    const entries = Object.entries(data).filter(
      ([, v]) => v !== null && v !== "" && !(Array.isArray(v) && v.length === 0)
    );
    if (entries.length === 0) return <span className="text-slate-400">—</span>;

    return (
      <dl className={depth === 0 ? "grid grid-cols-1 gap-4 sm:grid-cols-2" : "space-y-2"}>
        {entries.map(([key, value]) => (
          <div key={key} className={typeof value === "object" ? "sm:col-span-2" : ""}>
            <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              {humanizeKey(key)}
            </dt>
            <dd className="mt-0.5">
              <DataView data={value} depth={depth + 1} />
            </dd>
          </div>
        ))}
      </dl>
    );
  }

  return <span className="text-sm text-slate-700">{String(data)}</span>;
}
