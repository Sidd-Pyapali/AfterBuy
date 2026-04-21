import Link from "next/link";
import { LayoutList } from "lucide-react";
import UploadZone from "@/components/UploadZone";

export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col">
      <div className="flex-1 flex flex-col items-center justify-center px-5 py-12">
        <div className="w-full max-w-md">
          {/* Wordmark + nav */}
          <div className="flex items-center justify-between mb-12">
            <span className="font-display text-xl text-primary tracking-wide">
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
            <h1 className="font-display text-4xl text-zinc-900 leading-tight">
              Turn your closet into<br />resale-ready listings
            </h1>
            <p className="mt-4 text-[15px] text-zinc-500 leading-relaxed max-w-xs mx-auto">
              Photograph something from your wardrobe. AfterBuy identifies it,
              estimates wear, prices it against real comps, and lists it across
              marketplaces — all in one flow.
            </p>
          </div>

          <UploadZone />
        </div>
      </div>
    </main>
  );
}