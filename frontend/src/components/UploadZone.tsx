"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ImagePlus, Loader2, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { extractItem, findComps, valuateItem, generateListing } from "@/lib/api";

type Stage = "idle" | "uploading" | "identifying" | "finding_comps" | "estimating_value" | "generating_listing" | "error";

const STAGE_LABEL: Record<"uploading" | "identifying" | "finding_comps" | "estimating_value" | "generating_listing", string> = {
  uploading: "Uploading image...",
  identifying: "Identifying item...",
  finding_comps: "Finding market comparables...",
  estimating_value: "Estimating value...",
  generating_listing: "Generating listing...",
};

const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"];
const MAX_SIZE_MB = 10;

export default function UploadZone() {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const previewUrlRef = useRef<string | null>(null);

  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [stage, setStage] = useState<Stage>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    return () => {
      if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
    };
  }, []);

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selected = e.target.files?.[0];
      if (!selected) return;

      if (!ALLOWED_TYPES.includes(selected.type)) {
        setErrorMessage("Please select a JPEG, PNG, or WebP image.");
        return;
      }
      if (selected.size > MAX_SIZE_MB * 1024 * 1024) {
        setErrorMessage(`Image must be under ${MAX_SIZE_MB}MB.`);
        return;
      }

      if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
      const url = URL.createObjectURL(selected);
      previewUrlRef.current = url;

      setFile(selected);
      setPreview(url);
      setErrorMessage(null);
      setStage("idle");
    },
    []
  );

  const handleSubmit = useCallback(async () => {
    if (!file) return;
    setErrorMessage(null);
    setStage("uploading");

    const stageTimer = setTimeout(() => setStage("identifying"), 1400);

    try {
      const result = await extractItem(file);
      clearTimeout(stageTimer);

      setStage("finding_comps");
      let compsFound = false;
      try {
        const compsResult = await findComps(result.item.id);
        compsFound = compsResult.comp_count > 0;
      } catch {
        // Non-fatal: comp failure still lets the user see the result
      }

      if (compsFound) {
        setStage("estimating_value");
        let valuationSucceeded = false;
        try {
          await valuateItem(result.item.id);
          valuationSucceeded = true;
        } catch {
          // Non-fatal: valuation failure still lets the user see extraction + comps
        }

        if (valuationSucceeded) {
          setStage("generating_listing");
          try {
            await generateListing(result.item.id);
          } catch {
            // Non-fatal: listing failure still lets the user see extraction + comps + valuation
          }
        }
      }

      router.push(`/item/${result.item.id}`);
    } catch (err: unknown) {
      clearTimeout(stageTimer);
      setStage("error");
      setErrorMessage(
        err instanceof Error ? err.message : "Something went wrong. Please try again."
      );
    }
  }, [file, router]);

  const isProcessing = stage === "uploading" || stage === "identifying" || stage === "finding_comps" || stage === "estimating_value" || stage === "generating_listing";

  return (
    <div className="flex flex-col gap-4">
      {/* Upload zone */}
      <button
        type="button"
        onClick={() => !isProcessing && inputRef.current?.click()}
        disabled={isProcessing}
        className={[
          "w-full rounded-2xl border-2 border-dashed transition-colors text-left",
          preview ? "border-zinc-200 p-2" : "border-zinc-300 p-8",
          isProcessing
            ? "cursor-default opacity-80"
            : "hover:border-zinc-400 cursor-pointer",
        ].join(" ")}
      >
        {preview ? (
          <img
            src={preview}
            alt="Selected item"
            className="w-full rounded-xl object-cover max-h-72"
          />
        ) : (
          <div className="flex flex-col items-center gap-3 text-zinc-400">
            <ImagePlus className="w-8 h-8" />
            <span className="text-sm font-medium text-zinc-500">
              Tap to select a photo
            </span>
            <span className="text-xs">JPEG · PNG · WebP</span>
          </div>
        )}
      </button>

      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={handleFileChange}
      />

      {/* Loading indicator */}
      {isProcessing && (
        <div className="flex items-center justify-center gap-2 text-zinc-500 text-sm py-1">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>{STAGE_LABEL[stage as "uploading" | "identifying" | "finding_comps" | "estimating_value" | "generating_listing"]}</span>
        </div>
      )}

      {/* Error message */}
      {stage === "error" && errorMessage && (
        <p className="text-sm text-red-500 text-center px-1">{errorMessage}</p>
      )}
      {stage === "idle" && errorMessage && (
        <p className="text-sm text-red-500 text-center px-1">{errorMessage}</p>
      )}

      {/* Action button */}
      {file && !isProcessing ? (
        <Button
          onClick={handleSubmit}
          className="w-full h-12 text-base font-medium rounded-xl"
        >
          Analyze Item
        </Button>
      ) : !file && !isProcessing ? (
        <Button
          onClick={() => inputRef.current?.click()}
          className="w-full h-12 text-base font-medium rounded-xl"
        >
          <Upload className="w-4 h-4" />
          Select a photo
        </Button>
      ) : null}
    </div>
  );
}
