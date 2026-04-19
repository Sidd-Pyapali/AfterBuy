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
    <div className="mt-8">
      <p className="text-xs font-medium text-zinc-400 uppercase tracking-wide mb-3">
        Generated Listing
      </p>
      <div className="rounded-2xl border border-dashed border-zinc-200 p-6 flex flex-col items-center gap-3 text-center">
        {error ? (
          <>
            <p className="text-sm text-red-500">{error}</p>
            <Button onClick={handleGenerate} disabled={loading} variant="outline" className="text-sm">
              Try again
            </Button>
          </>
        ) : (
          <>
            <p className="text-sm text-zinc-400">
              Listing wasn&apos;t generated automatically. Generate it now.
            </p>
            <Button onClick={handleGenerate} disabled={loading} className="text-sm">
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating...
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
