import UploadZone from "@/components/UploadZone";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-white flex flex-col">
      <div className="flex-1 flex flex-col items-center justify-center px-5 py-12">
        <div className="w-full max-w-md">
          {/* Wordmark */}
          <div className="mb-10 text-center">
            <p className="text-xs font-semibold tracking-widest text-zinc-400 uppercase mb-1">
              AfterBuy
            </p>
            <h1 className="text-3xl font-semibold tracking-tight text-zinc-900 leading-tight">
              Find out what your<br />item is worth
            </h1>
            <p className="mt-3 text-sm text-zinc-500 leading-relaxed max-w-xs mx-auto">
              Upload a photo. We&apos;ll identify it, find comparable listings, and build a
              marketplace-ready listing.
            </p>
          </div>

          <UploadZone />
        </div>
      </div>
    </main>
  );
}
