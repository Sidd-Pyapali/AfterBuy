import { notFound } from "next/navigation";
import Link from "next/link";
import { ChevronLeft, ImagePlus } from "lucide-react";
import ExtractionResult from "@/components/ExtractionResult";
import CompsSection from "@/components/CompsSection";
import ValuationCard from "@/components/ValuationCard";
import ListingCard from "@/components/ListingCard";
import RetryListingButton from "@/components/RetryListingButton";
import { AssembledItem } from "@/lib/api";

async function fetchItem(itemId: string): Promise<AssembledItem | null> {
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";
  try {
    const res = await fetch(`${backendUrl}/item/${itemId}`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function ItemPage({
  params,
}: {
  params: Promise<{ itemId: string }>;
}) {
  const { itemId } = await params;
  const data = await fetchItem(itemId);

  if (!data?.item) {
    notFound();
  }

  return (
    <main className="min-h-screen bg-white">
      <div className="mx-auto w-full max-w-md px-5 py-6 pb-16">
        {/* Header */}
        <div className="flex items-center mb-6">
          <Link
            href="/"
            className="flex items-center gap-1 text-sm text-zinc-400 hover:text-zinc-600 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            New item
          </Link>
          <span className="ml-auto text-xs font-semibold tracking-widest text-zinc-400 uppercase">
            AfterBuy
          </span>
        </div>

        {/* Extraction result */}
        <ExtractionResult item={data.item} />

        {/* Market comparables */}
        <CompsSection comps={data.comps} confidenceScore={data.item.confidence_score} />

        {/* Valuation */}
        {data.valuation && <ValuationCard valuation={data.valuation} />}

        {/* Generated listing — show card if ready, retry button if valuation exists but listing failed */}
        {data.listing ? (
          <ListingCard listing={data.listing} />
        ) : data.valuation ? (
          <RetryListingButton itemId={data.item.id} />
        ) : null}

        {/* Bottom CTA */}
        <div className="mt-12 text-center">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-sm font-medium text-zinc-400 hover:text-zinc-700 transition-colors"
          >
            <ImagePlus className="w-4 h-4" />
            Analyze another item
          </Link>
        </div>
      </div>
    </main>
  );
}
