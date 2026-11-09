import { ChevronDown } from "lucide-react";
import type { Faq } from "@/data/faqs";
import { faqJsonLd } from "@/lib/seo";
import { JsonLd } from "./JsonLd";

export function FaqList({ items }: { items: Faq[] }) {
  return (
    <div className="divide-y divide-slate-200 rounded-2xl border border-slate-200 bg-white">
      {items.map((f, i) => (
        <details key={f.q} className="group p-5 sm:p-6" open={i === 0}>
          <summary className="flex cursor-pointer list-none items-start justify-between gap-4 font-display text-base font-bold text-navy-950 sm:text-lg [&::-webkit-details-marker]:hidden">
            {f.q}
            <ChevronDown className="mt-1 h-5 w-5 shrink-0 text-brand-orange transition group-open:rotate-180" aria-hidden="true" />
          </summary>
          <p className="mt-3 text-sm leading-relaxed text-slate-600 sm:text-base">{f.a}</p>
        </details>
      ))}
      <JsonLd data={faqJsonLd(items)} />
    </div>
  );
}
