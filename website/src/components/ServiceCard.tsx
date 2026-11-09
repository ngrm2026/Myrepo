import Link from "next/link";
import { ArrowRight } from "lucide-react";
import type { Service } from "@/data/services";
import { ServiceIcon } from "./ServiceIcon";

export function ServiceCard({ service }: { service: Service }) {
  return (
    <article className="card group relative flex flex-col p-6 transition hover:border-brand-orange/40 hover:shadow-lg hover:shadow-navy-900/5">
      <span className="grid h-12 w-12 place-items-center rounded-xl bg-navy-950 text-brand-yellow transition group-hover:bg-brand-orange group-hover:text-white">
        <ServiceIcon name={service.icon} />
      </span>
      <h3 className="mt-5 text-lg font-bold">{service.name}</h3>
      <p className="mt-2 flex-1 text-sm leading-relaxed text-slate-600">{service.summary}</p>
      <Link
        href={`/services#${service.slug}`}
        className="mt-4 inline-flex items-center gap-1 text-sm font-semibold text-navy-700 after:absolute after:inset-0 hover:text-brand-orange"
      >
        Learn more <ArrowRight className="h-4 w-4" aria-hidden="true" />
      </Link>
    </article>
  );
}
