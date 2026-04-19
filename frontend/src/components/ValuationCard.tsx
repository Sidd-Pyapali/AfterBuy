import { Valuation } from "@/lib/api";

function fmt(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

const CONFIDENCE_STYLES: Record<
  "high" | "medium" | "low",
  { label: string; className: string }
> = {
  high: { label: "High confidence", className: "text-emerald-700 bg-emerald-50" },
  medium: { label: "Medium confidence", className: "text-amber-700 bg-amber-50" },
  low: { label: "Low confidence", className: "text-rose-700 bg-rose-50" },
};

export default function ValuationCard({ valuation }: { valuation: Valuation }) {
  const conf = CONFIDENCE_STYLES[valuation.confidence] ?? CONFIDENCE_STYLES.low;

  return (
    <div className="mt-10">
      <p className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest mb-3">
        Valuation
      </p>

      <div className="rounded-2xl border border-zinc-200 overflow-hidden">
        {/* Suggested price — hero row */}
        <div className="bg-primary px-5 py-6 text-center">
          <p className="text-[10px] font-semibold text-white/50 uppercase tracking-widest mb-2">
            Suggested listing price
          </p>
          <p className="font-display text-5xl text-white tracking-tight">
            {fmt(valuation.suggested_listing_price)}
          </p>
        </div>

        {/* Range row */}
        <div className="grid grid-cols-3 divide-x divide-zinc-100 bg-white">
          {[
            { label: "Low", value: valuation.estimated_low },
            { label: "Est. Value", value: valuation.estimated_mid },
            { label: "High", value: valuation.estimated_high },
          ].map(({ label, value }) => (
            <div key={label} className="px-3 py-4 text-center">
              <p className="text-[10px] text-zinc-400 uppercase tracking-wide mb-1">{label}</p>
              <p className="text-sm font-semibold text-zinc-900">{fmt(value)}</p>
            </div>
          ))}
        </div>

        {/* Confidence + reason */}
        <div className="px-5 py-4 bg-white border-t border-zinc-100 flex items-start gap-3">
          <span
            className={`shrink-0 mt-0.5 text-xs font-medium px-2.5 py-1 rounded-full ${conf.className}`}
          >
            {conf.label}
          </span>
          <p className="text-sm text-zinc-500 leading-snug">
            {valuation.valuation_reason}
          </p>
        </div>
      </div>
    </div>
  );
}
