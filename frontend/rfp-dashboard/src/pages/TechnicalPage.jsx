import useRfp from "../context/useRfp";
import { formatValue, matchTone } from "../lib/format";
import Card from "../components/ui/Card";
import Badge from "../components/ui/Badge";
import DataTable from "../components/ui/DataTable";
import DataView from "../components/ui/DataView";
import EmptyState from "../components/ui/EmptyState";

function MatchBadge({ pct }) {
  return <Badge tone={matchTone(pct)}>{pct ?? "—"}%</Badge>;
}

function ComparisonTable({ rows }) {
  if (!rows || rows.length === 0) {
    return <p className="text-sm text-slate-500">No spec comparison available.</p>;
  }

  const oemKeys = Object.keys(rows[0]).filter((k) => k.startsWith("OEM_"));

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead>
          <tr>
            <th className="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Spec
            </th>
            <th className="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              RFP Requirement
            </th>
            {oemKeys.map((k, i) => (
              <th
                key={k}
                className="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-slate-500"
              >
                OEM #{i + 1}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {rows.map((row, i) => (
            <tr key={i} className="hover:bg-slate-50">
              <td className="whitespace-nowrap px-3 py-2.5 text-slate-700">
                {row.spec_key}
                {row.pair_count ? ` (${row.pair_count}p)` : ""}
              </td>
              <td className="px-3 py-2.5 text-slate-700">{formatValue(row.rfp_requirement)}</td>
              {oemKeys.map((k) => {
                const cell = row[k];
                if (cell === "N/A" || !cell) {
                  return (
                    <td key={k} className="px-3 py-2.5 text-slate-400">
                      N/A
                    </td>
                  );
                }
                return (
                  <td key={k} className="px-3 py-2.5">
                    <span className={cell.passed ? "text-emerald-700" : "text-red-700"}>
                      {cell.value}
                    </span>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function TechnicalPage() {
  const { result } = useRfp();

  if (!result) {
    return (
      <EmptyState
        title="No RFP loaded"
        description="Run the Sales Agent scan or upload an RFP to see scope of supply and OEM matching here."
        ctaLabel="Go to Sales"
        ctaTo="/"
      />
    );
  }

  const tech = result.technical_agent_output ?? {};

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Technical — Scope &amp; SKU Matching</h1>
        <p className="mt-1 text-sm text-slate-500">
          Product Technical Team's view: scope of supply and OEM spec-match results.
        </p>
      </div>

      <Card title="Top OEM Recommendations" subtitle="Ranked by overall spec-match score">
        <DataTable
          columns={[
            { key: "rank", label: "Rank", render: (_, i) => `#${i + 1}` },
            { key: "product_sku", label: "OEM SKU" },
            { key: "spec_match_pct", label: "Spec Match", render: (r) => <MatchBadge pct={r.spec_match_pct} /> },
          ]}
          rows={tech.top_3_oems}
          rowKey={(r) => r.product_sku}
        />
      </Card>

      <Card title="Final Recommendation Table" subtitle="Selected SKU per item in scope of supply">
        <DataTable
          columns={[
            { key: "product_line", label: "Product Line" },
            { key: "rfp_product_name", label: "RFP Product" },
            { key: "rfp_product_code", label: "Code" },
            { key: "quantity", label: "Qty" },
            { key: "recommended_oem_sku", label: "Recommended SKU" },
            { key: "spec_match_pct", label: "Match", render: (r) => <MatchBadge pct={r.spec_match_pct} /> },
          ]}
          rows={tech.final_recommendation_table}
          rowKey={(r, i) => `${r.rfp_product_code}-${i}`}
        />
      </Card>

      <Card
        title="Spec Comparison Table"
        subtitle="RFP requirement vs. each recommended OEM's actual spec value"
      >
        <ComparisonTable rows={tech.comparison_table} />
      </Card>

      <details className="rounded-xl border border-slate-200 bg-white shadow-sm">
        <summary className="cursor-pointer select-none px-5 py-4 text-sm font-semibold text-slate-900">
          Technical Context Summary (Main Agent → Technical Agent briefing)
        </summary>
        <div className="border-t border-slate-100 px-5 py-4">
          <DataView data={result.technical_summary} />
        </div>
      </details>

      <details className="rounded-xl border border-slate-200 bg-white shadow-sm">
        <summary className="cursor-pointer select-none px-5 py-4 text-sm font-semibold text-slate-900">
          Full Scope of Supply Summary
        </summary>
        <div className="border-t border-slate-100 px-5 py-4">
          <DataView data={tech.scope_of_supply_summary} />
        </div>
      </details>
    </div>
  );
}
