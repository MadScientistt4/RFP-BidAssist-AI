import { Link } from "react-router-dom";

export default function EmptyState({ title, description, ctaLabel, ctaTo }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 bg-white px-6 py-16 text-center">
      <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
      <p className="mt-1 max-w-sm text-sm text-slate-500">{description}</p>
      {ctaTo && (
        <Link
          to={ctaTo}
          className="mt-4 inline-flex items-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500"
        >
          {ctaLabel}
        </Link>
      )}
    </div>
  );
}
