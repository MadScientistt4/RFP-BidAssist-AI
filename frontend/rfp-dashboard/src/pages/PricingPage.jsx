import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import useRfp from "../context/useRfp";
import { formatCurrency } from "../lib/format";
import Card from "../components/ui/Card";
import DataTable from "../components/ui/DataTable";
import DataView from "../components/ui/DataView";
import EmptyState from "../components/ui/EmptyState";

export default function PricingPage() {
  const { result } = useRfp();

  if (!result) {
    return (
      <EmptyState
        title="No RFP loaded"
        description="Run the Sales Agent scan or upload an RFP to see the priced response here."
        ctaLabel="Go to Sales"
        ctaTo="/"
      />
    );
  }

  const priced = result.final_priced_output ?? {};
  const items = priced.priced_items ?? [];
  const currency = priced.currency ?? "INR";

  const chartData = items.map((item) => ({
    name: item.item_name?.length > 20 ? `${item.item_name.slice(0, 20)}…` : item.item_name,
    Material: Math.round(item.base_material_cost ?? 0),
    Tests: Math.round(item.total_test_cost ?? 0),
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Pricing — Cost Consolidation</h1>
        <p className="mt-1 text-sm text-slate-500">
          Pricing Team's view: material and test costs from the synthetic price tables.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Card title="Grand Total">
          <p className="text-2xl font-semibold text-slate-900">
            {formatCurrency(priced.grand_total, currency)}
          </p>
        </Card>
        <Card title="Line Items">
          <p className="text-2xl font-semibold text-slate-900">{items.length}</p>
        </Card>
        <Card title="Inspection Cost">
          <p className="text-2xl font-semibold text-slate-900">
            {formatCurrency(priced.inspection_cost, currency)}
          </p>
        </Card>
      </div>

      {chartData.length > 0 && (
        <Card title="Cost Breakdown by Item" subtitle="Material cost vs. test/service cost">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} stroke="#94a3b8" />
              <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" />
              <Tooltip
                formatter={(value) => formatCurrency(value, currency)}
                contentStyle={{ fontSize: 12, borderRadius: 8, borderColor: "#e2e8f0" }}
              />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="Material" stackId="cost" fill="#4f46e5" radius={[0, 0, 0, 0]} />
              <Bar dataKey="Tests" stackId="cost" fill="#a5b4fc" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      )}

      <Card title="Priced Line Items">
        <DataTable
          columns={[
            { key: "item_name", label: "Item" },
            { key: "sku", label: "SKU" },
            { key: "quantity", label: "Qty", render: (r) => `${r.quantity} ${r.unit ?? ""}` },
            { key: "unit_price", label: "Unit Price", render: (r) => formatCurrency(r.unit_price, currency) },
            { key: "base_material_cost", label: "Material Cost", render: (r) => formatCurrency(r.base_material_cost, currency) },
            { key: "total_test_cost", label: "Test Cost", render: (r) => formatCurrency(r.total_test_cost, currency) },
            { key: "total_item_cost", label: "Total", render: (r) => formatCurrency(r.total_item_cost, currency) },
          ]}
          rows={items}
          rowKey={(r) => r.item_id}
        />
      </Card>

      <details className="rounded-xl border border-slate-200 bg-white shadow-sm">
        <summary className="cursor-pointer select-none px-5 py-4 text-sm font-semibold text-slate-900">
          Pricing Inputs (Main Agent → Pricing Agent briefing)
        </summary>
        <div className="border-t border-slate-100 px-5 py-4">
          <DataView data={result.pricing_summary} />
        </div>
      </details>
    </div>
  );
}
