import Link from "next/link";
import { LayoutList } from "lucide-react";
import UploadZone from "@/components/UploadZone";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-white flex flex-col">
      <div className="flex-1 flex flex-col items-center justify-center px-5 py-12">
        <div className="w-full max-w-md">
          {/* Wordmark + nav */}
          <div className="flex items-center justify-between mb-10">
            <span className="text-xs font-semibold tracking-widest text-zinc-400 uppercase">
              AfterBuy
            </span>
            <Link
              href="/inventory"
              className="flex items-center gap-1.5 text-xs font-medium text-zinc-400 hover:text-zinc-700 transition-colors"
            >
              <LayoutList className="w-3.5 h-3.5" />
              My items
            </Link>
          </div>

          {/* Hero */}
          <div className="mb-10 text-center">
            <h1 className="text-3xl font-semibold tracking-tight text-zinc-900 leading-tight">
              Find out what your<br />item is worth
            </h1>
            <p className="mt-3 text-sm text-zinc-500 leading-relaxed max-w-xs mx-auto">
              Upload or photograph an item you own. We&apos;ll identify it, find
              comparable listings, and build a marketplace-ready resale listing.
            </p>
          </div>

          <UploadZone />
        </div>
      </div>
    </main>
  );
}
