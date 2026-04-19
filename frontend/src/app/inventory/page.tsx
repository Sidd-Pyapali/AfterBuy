import Link from "next/link";
import { ChevronLeft, ImagePlus } from "lucide-react";
import InventoryCard from "@/components/InventoryCard";
import { getItems } from "@/lib/api";

export const dynamic = "force-dynamic";

async function fetchItems() {
  const backendUrl =
    process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";
  try {
    const res = await fetch(`${backendUrl}/items?limit=50`, {
      cache: "no-store",
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.items ?? [];
  } catch {
    return [];
  }
}

export default async function InventoryPage() {
  const items = await fetchItems();

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
            Home
          </Link>
          <span className="ml-auto text-xs font-semibold tracking-widest text-zinc-400 uppercase">
            AfterBuy
          </span>
        </div>

        {/* Page title */}
        <div className="mb-6">
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">
            Your items
          </h1>
          <p className="text-sm text-zinc-400 mt-1">
            Everything you&apos;ve analyzed and prepared for resale.
          </p>
        </div>

        {/* Item list */}
        {items.length === 0 ? (
          <div className="rounded-2xl border border-zinc-100 bg-zinc-50 px-5 py-10 text-center">
            <p className="text-sm font-medium text-zinc-500 mb-1">
              No items yet
            </p>
            <p className="text-xs text-zinc-400 mb-5">
              Upload a photo to identify and value your first item.
            </p>
            <Link
              href="/"
              className="inline-flex items-center gap-2 text-sm font-medium text-zinc-900 bg-zinc-100 hover:bg-zinc-200 transition-colors px-4 py-2 rounded-xl"
            >
              <ImagePlus className="w-4 h-4" />
              Add your first item
            </Link>
          </div>
        ) : (
          <div className="rounded-2xl border border-zinc-200 overflow-hidden px-5">
            {items.map((item: Parameters<typeof InventoryCard>[0]["item"]) => (
              <InventoryCard key={item.id} item={item} />
            ))}
          </div>
        )}

        {/* Bottom CTA */}
        {items.length > 0 && (
          <div className="mt-10 text-center">
            <Link
              href="/"
              className="inline-flex items-center gap-2 text-sm font-medium text-zinc-400 hover:text-zinc-700 transition-colors"
            >
              <ImagePlus className="w-4 h-4" />
              Analyze another item
            </Link>
          </div>
        )}
      </div>
    </main>
  );
}
