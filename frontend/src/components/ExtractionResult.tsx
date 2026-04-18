import { Item } from "@/lib/api";

function confidenceLabel(score: number | null): { text: string; className: string } {
  const n = score ?? 0;
  if (n >= 0.75) return { text: "High confidence", className: "text-green-700 bg-green-50" };
  if (n >= 0.5) return { text: "Medium confidence", className: "text-amber-700 bg-amber-50" };
  return { text: "Low confidence", className: "text-red-700 bg-red-50" };
}

export default function ExtractionResult({ item }: { item: Item }) {
  const conf = confidenceLabel(item.confidence_score);

  const attributes = [
    { label: "Brand", value: item.brand },
    { label: "Category", value: item.category },
    { label: "Type", value: item.item_type },
    { label: "Color", value: item.color },
    { label: "Condition", value: item.condition },
  ].filter((a): a is { label: string; value: string } => typeof a.value === "string" && a.value.length > 0);

  const notableDetails = item.extracted_metadata?.notable_details ?? [];

  return (
    <div className="flex flex-col gap-6">
      {/* Item image */}
      <img
        src={item.image_url}
        alt={item.title_guess ?? "Your item"}
        className="w-full rounded-2xl object-cover max-h-80"
      />

      {/* Title and confidence */}
      <div className="flex items-start justify-between gap-3">
        <h2 className="text-xl font-semibold text-zinc-900 leading-snug">
          {item.title_guess ?? "Item identified"}
        </h2>
        <span
          className={`shrink-0 text-xs font-medium px-2.5 py-1 rounded-full ${conf.className}`}
        >
          {conf.text}
        </span>
      </div>

      {/* Attribute grid */}
      {attributes.length > 0 && (
        <div className="grid grid-cols-2 gap-3">
          {attributes.map((attr) => (
            <div key={attr.label} className="bg-zinc-50 rounded-xl px-4 py-3">
              <p className="text-xs font-medium text-zinc-400 uppercase tracking-wide mb-1">
                {attr.label}
              </p>
              <p className="text-sm font-medium text-zinc-900 capitalize">{attr.value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Notable details */}
      {notableDetails.length > 0 && (
        <div>
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wide mb-2">
            Details
          </p>
          <ul className="flex flex-wrap gap-2">
            {notableDetails.map((detail, i) => (
              <li
                key={i}
                className="text-sm text-zinc-600 bg-zinc-100 rounded-lg px-3 py-1.5"
              >
                {detail}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
