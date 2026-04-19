import { ExternalLink } from "lucide-react";
import { Comp } from "@/lib/api";

function formatPrice(price: number, currency: string): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: currency || "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(price);
}

function CompCard({ comp }: { comp: Comp }) {
  return (
    <a
      href={comp.url || "#"}
      target="_blank"
      rel="noopener noreferrer"
      className="flex gap-3 p-3.5 rounded-xl bg-white border border-zinc-100 hover:border-zinc-200 transition-colors"
    >
      {/* Thumbnail */}
      <div className="shrink-0 w-16 h-16 rounded-lg overflow-hidden bg-zinc-100">
        {comp.image_url ? (
          <img
            src={comp.image_url}
            alt={comp.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-zinc-300 text-xs">
            —
          </div>
        )}
      </div>

      {/* Details */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-zinc-800 line-clamp-2 leading-snug">
          {comp.title}
        </p>
        <div className="mt-1.5 flex items-center gap-2">
          <span className="text-sm font-semibold text-primary">
            {formatPrice(comp.price, comp.currency)}
          </span>
          {comp.condition && (
            <span className="text-xs text-zinc-400">{comp.condition}</span>
          )}
        </div>
        <div className="mt-0.5 flex items-center gap-1 text-xs text-zinc-400">
          <span className="capitalize">{comp.source}</span>
          <ExternalLink className="w-3 h-3" />
        </div>
      </div>
    </a>
  );
}

const COMP_SEARCH_MIN_CONFIDENCE = 0.35;

export default function CompsSection({
  comps,
  confidenceScore,
}: {
  comps: Comp[];
  confidenceScore: number | null;
}) {
  if (comps.length === 0) {
    const tooWeak =
      confidenceScore !== null && confidenceScore < COMP_SEARCH_MIN_CONFIDENCE;

    return (
      <div className="mt-10">
        <p className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest mb-3">
          Market Comparables
        </p>
        <div className="rounded-2xl border border-dashed border-zinc-200 p-6 text-center">
          <p className="text-sm text-zinc-400">
            {tooWeak
              ? "This item couldn't be clearly identified — comparable search was skipped."
              : "No comparable listings found for this item."}
          </p>
        </div>
      </div>
    );
  }

  const displayComps = comps.slice(0, 6);

  return (
    <div className="mt-10">
      <p className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest mb-3">
        Market Comparables
        <span className="ml-2 normal-case font-normal text-zinc-300">
          {comps.length} found
        </span>
      </p>
      <div className="flex flex-col gap-2">
        {displayComps.map((comp) => (
          <CompCard key={comp.id} comp={comp} />
        ))}
      </div>
    </div>
  );
}
