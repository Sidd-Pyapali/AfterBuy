import { WearAssessment } from "@/lib/api";

const WEAR_STYLES: Record<string, { label: string; badgeClass: string; dotClass: string }> = {
  none: {
    label: "No visible wear",
    badgeClass: "text-emerald-700 bg-emerald-50",
    dotClass: "bg-emerald-400",
  },
  light: {
    label: "Light wear",
    badgeClass: "text-amber-700 bg-amber-50",
    dotClass: "bg-amber-400",
  },
  moderate: {
    label: "Moderate wear",
    badgeClass: "text-orange-700 bg-orange-50",
    dotClass: "bg-orange-400",
  },
  heavy: {
    label: "Heavy wear",
    badgeClass: "text-rose-700 bg-rose-50",
    dotClass: "bg-rose-400",
  },
  unknown: {
    label: "Wear not assessed",
    badgeClass: "text-zinc-500 bg-zinc-100",
    dotClass: "bg-zinc-300",
  },
};

function pct(factor: number): string {
  const reduction = Math.round((1 - factor) * 100);
  return `${reduction}%`;
}

export default function WearAssessmentCard({ wear }: { wear: WearAssessment }) {
  const style = WEAR_STYLES[wear.wear_level] ?? WEAR_STYLES.unknown;
  const isUnknown = wear.wear_level === "unknown";
  const hasAdjustment = wear.pricing_adjustment_factor < 0.99 && !isUnknown;
  const visibleSignals = (wear.wear_signals ?? []).filter((s) => s.confidence >= 0.40);

  return (
    <div className="mt-10">
      <p className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest mb-3">
        Visible Wear
      </p>

      <div className="rounded-2xl border border-zinc-200 overflow-hidden">
        {/* Wear level header */}
        <div className="px-5 py-4 bg-white border-b border-zinc-100 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <span className={`w-2 h-2 rounded-full shrink-0 ${style.dotClass}`} />
            <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${style.badgeClass}`}>
              {style.label}
            </span>
          </div>
          {wear.wear_confidence > 0 && (
            <span className="text-[10px] text-zinc-400">
              {Math.round(wear.wear_confidence * 100)}% confidence
            </span>
          )}
        </div>

        {/* Wear summary */}
        {!isUnknown && wear.wear_summary && (
          <div className="px-5 py-4 bg-zinc-50/60 border-b border-zinc-100">
            <p className="text-sm text-zinc-600 leading-relaxed">{wear.wear_summary}</p>
          </div>
        )}

        {/* Wear signals */}
        {visibleSignals.length > 0 && (
          <div className="px-5 py-4 bg-white border-b border-zinc-100">
            <p className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest mb-3">
              Wear Zones
            </p>
            <ul className="flex flex-col gap-2">
              {visibleSignals.map((s, i) => (
                <li key={i} className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="shrink-0 w-1.5 h-1.5 rounded-full bg-zinc-300" />
                    <span className="text-sm text-zinc-700 capitalize truncate">
                      {s.zone} — {s.signal}
                    </span>
                  </div>
                  <span className={`shrink-0 text-[10px] font-medium px-2 py-0.5 rounded-full capitalize ${
                    s.severity === "heavy"
                      ? "text-rose-600 bg-rose-50"
                      : s.severity === "moderate"
                      ? "text-orange-600 bg-orange-50"
                      : "text-amber-600 bg-amber-50"
                  }`}>
                    {s.severity}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Pricing adjustment note */}
        {hasAdjustment && (
          <div className="px-5 py-3.5 bg-zinc-50/60">
            <p className="text-xs text-zinc-500 leading-snug">
              Resale price adjusted{" "}
              <span className="font-medium text-zinc-700">{pct(wear.pricing_adjustment_factor)} lower</span>{" "}
              to reflect visible wear shown in provided photos.
            </p>
          </div>
        )}

        {/* Unknown wear state */}
        {isUnknown && (
          <div className="px-5 py-4 bg-zinc-50/60">
            <p className="text-xs text-zinc-400 leading-snug">
              Wear could not be assessed from the provided photo. No pricing adjustment was applied.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
