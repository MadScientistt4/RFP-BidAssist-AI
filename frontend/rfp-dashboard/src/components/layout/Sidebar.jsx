import { NavLink } from "react-router-dom";
import { SalesIcon, TechnicalIcon, PricingIcon, ResponseIcon } from "./icons";

const NAV_ITEMS = [
  { to: "/", label: "Sales", icon: SalesIcon, end: true },
  { to: "/technical", label: "Technical", icon: TechnicalIcon },
  { to: "/pricing", label: "Pricing", icon: PricingIcon },
  { to: "/response", label: "Response", icon: ResponseIcon },
];

export default function Sidebar() {
  return (
    <aside className="print:hidden-force flex w-56 shrink-0 flex-col border-r border-slate-200 bg-white">
      <div className="flex items-center gap-2 px-5 py-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-sm font-bold text-white">
          R
        </div>
        <div>
          <p className="text-sm font-semibold leading-tight text-slate-900">RFP BidAssist</p>
          <p className="text-xs leading-tight text-slate-400">AI</p>
        </div>
      </div>

      <nav className="flex flex-1 flex-col gap-1 px-3">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                }`
              }
            >
              <Icon />
              {item.label}
            </NavLink>
          );
        })}
      </nav>

      <div className="px-5 py-4 text-xs text-slate-400">
        Sales → Technical → Pricing → Response
      </div>
    </aside>
  );
}
