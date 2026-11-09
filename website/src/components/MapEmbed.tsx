import { siteConfig } from "@/config/site";

export function MapEmbed({ className = "" }: { className?: string }) {
  const src = `https://www.google.com/maps?q=${encodeURIComponent(siteConfig.mapQuery)}&output=embed`;
  return (
    <div className={`overflow-hidden rounded-2xl border border-slate-200 bg-slate-100 ${className}`}>
      <iframe
        title={`Map showing ${siteConfig.name} location in Chennai`}
        src={src}
        className="h-full min-h-80 w-full"
        loading="lazy"
        referrerPolicy="no-referrer-when-downgrade"
        allowFullScreen
      />
    </div>
  );
}
