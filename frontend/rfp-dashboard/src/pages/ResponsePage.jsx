import useRfp from "../context/useRfp";
import { formatCurrency, matchTone } from "../lib/format";
import Card from "../components/ui/Card";
import Badge from "../components/ui/Badge";
import DataTable from "../components/ui/DataTable";
import EmptyState from "../components/ui/EmptyState";

export default function ResponsePage() {
  const { result } = useRfp();

  if (!result) {
    return (
      <EmptyState
        title="No RFP loaded"
        description="Run the Sales Agent scan or upload an RFP to build a consolidated response."
        ctaLabel="Go to Sales"
        ctaTo="/"
      />
    );
  }

  const meta = result.extracted_rfp?.rfp_metadata ?? {};
  const recommendationTable = result.technical_agent_output?.final_recommendation_table ?? [];
  const priced = result.final_priced_output ?? {};
  const currency = priced.currency ?? "INR";

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">Response — Consolidated Summary</h1>
          <p className="mt-1 text-sm text-slate-500">
            Main Agent's consolidation of technical and pricing inputs, ready for submission.
          </p>
        </div>
        <button
          onClick={() => window.print()}
          className="print:hidden-force shrink-0 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Print / Export
        </button>
      </div>

      <Card title="RFP Details">
        <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">Title</dt>
            <dd className="mt-0.5 text-sm text-slate-800">{meta.rfp_title || "—"}</dd>
          </div>
          <div>
            <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">RFP Number</dt>
            <dd className="mt-0.5 text-sm text-slate-800">{meta.rfp_number || "—"}</dd>
          </div>
          <div>
            <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">Issuing Authority</dt>
            <dd className="mt-0.5 text-sm text-slate-800">{meta.issuing_authority || "—"}</dd>
          </div>
          <div>
            <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">Submission Deadline</dt>
            <dd className="mt-0.5 text-sm text-slate-800">{meta.submission_deadline || "—"}</dd>
          </div>
        </dl>
      </Card>

      <Card title="Recommended Products" subtitle="From the Technical Agent's SKU matching">
        <DataTable
          columns={[
            { key: "rfp_product_name", label: "RFP Product" },
            { key: "quantity", label: "Qty" },
            { key: "recommended_oem_sku", label: "Recommended SKU" },
            {
              key: "spec_match_pct",
              label: "Spec Match",
              render: (r) => <Badge tone={matchTone(r.spec_match_pct)}>{r.spec_match_pct}%</Badge>,
            },
          ]}
          rows={recommendationTable}
          rowKey={(r, i) => `${r.rfp_product_code}-${i}`}
        />
      </Card>

      <Card title="Pricing" subtitle="From the Pricing Agent's synthetic price tables">
        <DataTable
          columns={[
            { key: "item_name", label: "Item" },
            { key: "sku", label: "SKU" },
            { key: "total_item_cost", label: "Total Cost", render: (r) => formatCurrency(r.total_item_cost, currency) },
          ]}
          rows={priced.priced_items}
          rowKey={(r) => r.item_id}
        />
        <div className="mt-4 flex justify-end border-t border-slate-100 pt-4">
          <div className="text-right">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Grand Total</p>
            <p className="text-2xl font-semibold text-slate-900">
              {formatCurrency(priced.grand_total, currency)}
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
