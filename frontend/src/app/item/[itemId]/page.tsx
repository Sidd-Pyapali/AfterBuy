import { notFound } from "next/navigation";
import Link from "next/link";
import { ChevronLeft } from "lucide-react";
import ExtractionResult from "@/components/ExtractionResult";
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
      <div className="mx-auto w-full max-w-md px-5 py-6">
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

        {/* Placeholder — comps and valuation added in Phase 3 & 4 */}
        <div className="mt-8 rounded-2xl border border-dashed border-zinc-200 p-6 text-center">
          <p className="text-sm text-zinc-400">
            Market comparables and valuation coming next
          </p>
        </div>
      </div>
    </main>
  );
}
