"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Pencil, X, Check, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  GeneratedListing,
  Publication,
  updateListing,
  publishToMarketplaces,
} from "@/lib/api";

const MARKETPLACES = [
  { id: "ebay", label: "eBay" },
  { id: "poshmark", label: "Poshmark" },
  { id: "depop", label: "Depop" },
  { id: "facebook_marketplace", label: "Facebook" },
];

export default function ListingEditPanel({
  listing,
  itemId,
  publications,
}: {
  listing: GeneratedListing;
  itemId: string;
  publications: Publication[];
}) {
  const router = useRouter();

  // ── Edit state ──────────────────────────────────────────────
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(listing.title);
  const [editDescription, setEditDescription] = useState(listing.description);
  const [editConditionNote, setEditConditionNote] = useState(listing.condition_note);
  const [editPrice, setEditPrice] = useState(
    listing.suggested_price != null ? String(listing.suggested_price) : ""
  );
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Re-sync form fields when the server refreshes listing data (not while editing)
  useEffect(() => {
    if (!isEditing) {
      setEditTitle(listing.title);
      setEditDescription(listing.description);
      setEditConditionNote(listing.condition_note);
      setEditPrice(listing.suggested_price != null ? String(listing.suggested_price) : "");
    }
  }, [listing, isEditing]);

  const handleSave = async () => {
    setIsSaving(true);
    setSaveError(null);
    try {
      const parsedPrice = editPrice ? parseFloat(editPrice) : undefined;
      await updateListing(listing.id, {
        title: editTitle,
        description: editDescription,
        condition_note: editConditionNote,
        ...(parsedPrice != null && !isNaN(parsedPrice) ? { suggested_price: parsedPrice } : {}),
      });
      setIsEditing(false);
      router.refresh();
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : "Save failed. Please try again.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setSaveError(null);
    setEditTitle(listing.title);
    setEditDescription(listing.description);
    setEditConditionNote(listing.condition_note);
    setEditPrice(listing.suggested_price != null ? String(listing.suggested_price) : "");
  };

  // ── Publish state ────────────────────────────────────────────
  const publishedIds = new Set(publications.map((p) => p.platform));
  const availablePlatforms = MARKETPLACES.filter((m) => !publishedIds.has(m.id));

  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [isPublishing, setIsPublishing] = useState(false);
  const [publishError, setPublishError] = useState<string | null>(null);

  const togglePlatform = (id: string) => {
    setSelectedPlatforms((prev) =>
      prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]
    );
  };

  const handlePublish = async () => {
    if (!selectedPlatforms.length) return;
    setIsPublishing(true);
    setPublishError(null);
    try {
      await publishToMarketplaces(itemId, selectedPlatforms);
      setSelectedPlatforms([]);
      router.refresh();
    } catch (err) {
      setPublishError(err instanceof Error ? err.message : "Publish failed. Please try again.");
    } finally {
      setIsPublishing(false);
    }
  };

  return (
    <div className="mt-8">
      <p className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest mb-3">
        Review &amp; Distribute
      </p>

      <div className="rounded-2xl border border-zinc-200 overflow-hidden">
        {/* Edit toggle row */}
        {!isEditing ? (
          <div className="px-5 py-4 bg-white border-b border-zinc-100 flex items-center justify-between gap-3">
            <p className="text-sm text-zinc-500">
              Looks good? Edit before publishing if needed.
            </p>
            <button
              onClick={() => setIsEditing(true)}
              className="shrink-0 flex items-center gap-1.5 text-xs font-medium text-zinc-500 hover:text-zinc-800 transition-colors"
            >
              <Pencil className="w-3.5 h-3.5" />
              Edit
            </button>
          </div>
        ) : (
          /* Edit form */
          <div className="px-5 py-4 bg-white border-b border-zinc-100">
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm font-medium text-zinc-800">Edit listing</p>
              <button
                onClick={handleCancelEdit}
                className="text-zinc-400 hover:text-zinc-700 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="flex flex-col gap-3">
              <div>
                <label className="block text-xs text-zinc-400 mb-1">Title</label>
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  className="w-full text-sm border border-zinc-200 rounded-xl px-3 py-2 text-zinc-900 focus:outline-none focus:ring-2 focus:ring-zinc-300"
                />
              </div>
              <div>
                <label className="block text-xs text-zinc-400 mb-1">Description</label>
                <textarea
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  rows={4}
                  className="w-full text-sm border border-zinc-200 rounded-xl px-3 py-2 text-zinc-900 focus:outline-none focus:ring-2 focus:ring-zinc-300 resize-none"
                />
              </div>
              <div>
                <label className="block text-xs text-zinc-400 mb-1">Condition note</label>
                <input
                  type="text"
                  value={editConditionNote}
                  onChange={(e) => setEditConditionNote(e.target.value)}
                  className="w-full text-sm border border-zinc-200 rounded-xl px-3 py-2 text-zinc-900 focus:outline-none focus:ring-2 focus:ring-zinc-300"
                />
              </div>
              <div>
                <label className="block text-xs text-zinc-400 mb-1">Suggested price ($)</label>
                <input
                  type="number"
                  value={editPrice}
                  onChange={(e) => setEditPrice(e.target.value)}
                  min={0}
                  step={1}
                  className="w-full text-sm border border-zinc-200 rounded-xl px-3 py-2 text-zinc-900 focus:outline-none focus:ring-2 focus:ring-zinc-300"
                />
              </div>
            </div>

            {saveError && (
              <p className="mt-3 text-sm text-red-500">{saveError}</p>
            )}

            <div className="mt-4 flex gap-2 justify-end">
              <Button
                variant="outline"
                size="sm"
                onClick={handleCancelEdit}
                disabled={isSaving}
              >
                Cancel
              </Button>
              <Button size="sm" onClick={handleSave} disabled={isSaving}>
                {isSaving ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    Saving…
                  </>
                ) : (
                  <>
                    <Check className="w-3.5 h-3.5" />
                    Save changes
                  </>
                )}
              </Button>
            </div>
          </div>
        )}

        {/* Already-published platforms */}
        {publications.length > 0 && (
          <div className="px-5 py-4 bg-white border-b border-zinc-100">
            <p className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest mb-2">Distributed to</p>
            <div className="flex flex-wrap gap-2">
              {publications.map((pub) => (
                <span
                  key={pub.id}
                  className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1 rounded-full bg-emerald-50 text-emerald-700"
                >
                  <Check className="w-3 h-3" />
                  {MARKETPLACES.find((m) => m.id === pub.platform)?.label ?? pub.platform}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Platform selector */}
        {availablePlatforms.length > 0 && (
          <div className="px-5 py-5 bg-white">
            <p className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest mb-3">
              {publications.length > 0 ? "Add more channels" : "Distribute to"}
            </p>

            <div className="grid grid-cols-2 gap-2 mb-4">
              {availablePlatforms.map((m) => {
                const selected = selectedPlatforms.includes(m.id);
                return (
                  <button
                    key={m.id}
                    onClick={() => togglePlatform(m.id)}
                    className={[
                      "px-3 py-2.5 rounded-xl border text-sm font-medium transition-colors",
                      selected
                        ? "border-primary bg-primary text-white"
                        : "border-zinc-200 bg-white text-zinc-700 hover:border-zinc-300",
                    ].join(" ")}
                  >
                    {m.label}
                  </button>
                );
              })}
            </div>

            {publishError && (
              <p className="mb-3 text-sm text-red-500">{publishError}</p>
            )}

            <Button
              onClick={handlePublish}
              disabled={isPublishing || selectedPlatforms.length === 0}
              className="w-full"
            >
              {isPublishing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Routing listing…
                </>
              ) : selectedPlatforms.length > 0 ? (
                `Distribute to ${selectedPlatforms.length} channel${selectedPlatforms.length > 1 ? "s" : ""}`
              ) : (
                "Select channels above"
              )}
            </Button>

            <p className="mt-3 text-xs text-zinc-400 text-center">
              Listing routing is simulated for selected channels
            </p>
          </div>
        )}

        {/* All platforms demo-published */}
        {availablePlatforms.length === 0 && publications.length > 0 && (
          <div className="px-5 py-4 bg-zinc-50 text-center">
            <p className="text-xs text-zinc-400">Ready across all selected channels ✓</p>
          </div>
        )}
      </div>
    </div>
  );
}
