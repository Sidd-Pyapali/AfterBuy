"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { generateListing } from "@/lib/api";

export default function RetryListingButton({ itemId }: { itemId: string }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      await generateListing(itemId);
      router.refresh();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Generation failed. Please try again."
      );
      setLoading(false);
    }
  };

  return (
    <div className="mt-10">
      <p className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest mb-3">
        Generated Listing
      </p>
      <div className="rounded-2xl border border-zinc-200 p-6 flex flex-col items-center gap-3 text-center">
        {error ? (
          <>
            <p className="text-sm text-rose-500">{error}</p>
            <Button onClick={handleGenerate} disabled={loading} variant="outline" className="text-sm">
              Try again
            </Button>
          </>
        ) : (
          <>
            <p className="text-sm text-zinc-400 leading-relaxed">
              Your item is valued. Tap below to generate a<br />marketplace-ready listing.
            </p>
            <Button onClick={handleGenerate} disabled={loading} className="text-sm mt-1">
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating listing…
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Generate listing
                </>
              )}
            </Button>
          </>
        )}
      </div>
    </div>
  );
}
