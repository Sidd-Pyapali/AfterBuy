import Link from "next/link";
import { InventoryItem } from "@/lib/api";

const PLATFORM_LABELS: Record<string, string> = {
  ebay: "eBay",
  poshmark: "Poshmark",
  depop: "Depop",
  facebook_marketplace: "Facebook",
};

const STATUS_CONFIG: Record<
  InventoryItem["listing_status"],
  { label: string; className: string }
> = {
  distributed: { label: "Distributed", className: "bg-green-50 text-green-700" },
  listed: { label: "Listing ready", className: "bg-blue-50 text-blue-700" },
  valued: { label: "Valued", className: "bg-amber-50 text-amber-700" },
  identified: { label: "Identified", className: "bg-zinc-100 text-zinc-500" },
};

function fmt(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

export default function InventoryCard({ item }: { item: InventoryItem }) {
  const status = STATUS_CONFIG[item.listing_status] ?? STATUS_CONFIG.identified;
  const displayTitle =
    item.listing_title ?? item.title_guess ?? item.item_type ?? "Unknown item";
  const subtitle = [item.brand, item.category].filter(Boolean).join(" · ");

  return (
    <Link href={`/item/${item.id}`} className="block group">
      <div className="flex gap-3 items-start py-4 border-b border-zinc-100 last:border-0">
        {/* Thumbnail */}
        <div className="shrink-0 w-16 h-16 rounded-xl overflow-hidden bg-zinc-100">
          {item.image_url ? (
            <img
              src={item.image_url}
              alt={displayTitle}
              className="w-full h-full object-cover group-hover:opacity-90 transition-opacity"
            />
          ) : (
            <div className="w-full h-full bg-zinc-200" />
          )}
        </div>

        {/* Details */}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-zinc-900 leading-snug truncate">
            {displayTitle}
          </p>
          {subtitle && (
            <p className="text-xs text-zinc-400 mt-0.5 truncate">{subtitle}</p>
          )}

          <div className="mt-2 flex items-center gap-2 flex-wrap">
            <span
              className={`text-xs font-medium px-2 py-0.5 rounded-full ${status.className}`}
            >
              {status.label}
            </span>
            {item.platforms.length > 0 && (
              <span className="text-xs text-zinc-400">
                {item.platforms
                  .map((p) => PLATFORM_LABELS[p] ?? p)
                  .join(", ")}
              </span>
            )}
          </div>
        </div>

        {/* Price */}
        <div className="shrink-0 text-right">
          {item.valuation_mid != null ? (
            <p className="text-sm font-semibold text-zinc-900">
              {fmt(item.valuation_mid)}
            </p>
          ) : (
            <p className="text-xs text-zinc-300">—</p>
          )}
        </div>
      </div>
    </Link>
  );
}
