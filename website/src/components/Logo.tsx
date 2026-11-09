import Link from "next/link";
import { siteConfig } from "@/config/site";

export function Logo({ light = false }: { light?: boolean }) {
  return (
    <Link href="/" className="group flex items-center gap-2.5" aria-label={`${siteConfig.name} – Home`}>
      <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-gradient-to-br from-brand-yellow to-brand-orange shadow-md shadow-orange-500/30">
        <svg viewBox="0 0 24 24" className="h-6 w-6 text-navy-950" fill="currentColor" aria-hidden="true">
          <path d="M13.5 2 4 13.5h6.2L9 22l10-12.2h-6.3L13.5 2Z" />
        </svg>
      </span>
      <span className="leading-tight">
        <span className={`block font-display text-[15px] font-extrabold sm:text-base ${light ? "text-white" : "text-navy-950"}`}>
          {siteConfig.shortName}
        </span>
        <span className={`block text-[11px] font-medium ${light ? "text-navy-200" : "text-slate-500"}`}>
          Sales · Installation · Service
        </span>
      </span>
    </Link>
  );
}
