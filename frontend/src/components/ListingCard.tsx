"use client";

import { useState } from "react";
import { Copy, Check } from "lucide-react";
import { GeneratedListing } from "@/lib/api";

function fmt(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API unavailable in some environments
    }
  };

  return (
    <button
      onClick={handleCopy}
      className="shrink-0 p-1.5 rounded-lg text-zinc-400 hover:text-zinc-600 hover:bg-zinc-100 transition-colors"
      title={copied ? "Copied!" : "Copy to clipboard"}
    >
      {copied ? (
        <Check className="w-4 h-4 text-green-500" />
      ) : (
        <Copy className="w-4 h-4" />
      )}
    </button>
  );
}

export default function ListingCard({ listing }: { listing: GeneratedListing }) {
  const specificsEntries = listing.item_specifics
    ? Object.entries(listing.item_specifics)
    : [];

  return (
    <div className="mt-10">
      <p className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest mb-3">
        Generated Listing
      </p>

      <div className="rounded-2xl border border-zinc-200 overflow-hidden">
        {/* Title row */}
        <div className="px-5 py-4 bg-white border-b border-zinc-100 flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest mb-1.5">Title</p>
            <p className="text-sm font-semibold text-zinc-900 leading-snug">
              {listing.title}
            </p>
          </div>
          <CopyButton text={listing.title} />
        </div>

        {/* Description row */}
        <div className="px-5 py-4 bg-white border-b border-zinc-100 flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest mb-1.5">Description</p>
            <p className="text-sm text-zinc-600 leading-relaxed whitespace-pre-line">
              {listing.description}
            </p>
          </div>
          <CopyButton text={listing.description} />
        </div>

        {/* Condition + Price row */}
        <div
          className={`grid divide-x divide-zinc-100 bg-zinc-50/60 border-b border-zinc-100 ${
            listing.suggested_price != null ? "grid-cols-2" : "grid-cols-1"
          }`}
        >
          <div className="px-5 py-4">
            <p className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest mb-1.5">Condition</p>
            <p className="text-sm text-zinc-700 leading-snug">
              {listing.condition_note}
            </p>
          </div>
          {listing.suggested_price != null && (
            <div className="px-5 py-4 text-center">
              <p className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest mb-1.5">Price</p>
              <p className="text-sm font-semibold text-primary">
                {fmt(listing.suggested_price)}
              </p>
            </div>
          )}
        </div>

        {/* Item specifics */}
        {specificsEntries.length > 0 && (
          <div className="px-5 py-4 bg-white border-b border-zinc-100">
            <p className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest mb-3">
              Item Specifics
            </p>
            <div className="grid grid-cols-2 gap-2">
              {specificsEntries.map(([key, value]) => (
                <div key={key} className="bg-zinc-50/60 rounded-lg px-3 py-2">
                  <p className="text-[10px] text-zinc-400 mb-0.5">{key}</p>
                  <p className="text-sm font-medium text-zinc-800">{value}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Photo checklist */}
        {listing.photo_checklist && listing.photo_checklist.length > 0 && (
          <div className="px-5 py-4 bg-white">
            <p className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest mb-3">
              Recommended Photos
            </p>
            <ul className="flex flex-col gap-1.5">
              {listing.photo_checklist.map((shot, i) => (
                <li key={i} className="flex items-center gap-2.5 text-sm text-zinc-600">
                  <span className="shrink-0 w-4 h-4 rounded-full border border-zinc-200 flex items-center justify-center text-[9px] text-zinc-400 font-medium">
                    {i + 1}
                  </span>
                  {shot}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
