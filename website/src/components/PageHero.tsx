import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { JsonLd } from "./JsonLd";
import { breadcrumbJsonLd } from "@/lib/seo";

type Crumb = { name: string; path: string };

export function PageHero({
  eyebrow,
  title,
  lead,
  crumbs,
  children,
}: {
  eyebrow?: string;
  title: string;
  lead?: string;
  crumbs: Crumb[];
  children?: React.ReactNode;
}) {
  const all = [{ name: "Home", path: "/" }, ...crumbs];
  return (
    <section className="relative overflow-hidden bg-navy-950 text-white">
      <div className="bg-grid absolute inset-0" aria-hidden="true" />
      <div className="absolute -top-24 -right-24 h-72 w-72 rounded-full bg-brand-orange/20 blur-3xl" aria-hidden="true" />
      <div className="container-x relative py-14 sm:py-20">
        <nav aria-label="Breadcrumb">
          <ol className="flex flex-wrap items-center gap-1 text-xs text-navy-200 sm:text-sm">
            {all.map((c, i) => (
              <li key={c.path} className="flex items-center gap-1">
                {i > 0 && <ChevronRight className="h-3.5 w-3.5 text-navy-400" aria-hidden="true" />}
                {i < all.length - 1 ? (
                  <Link href={c.path} className="hover:text-brand-yellow">{c.name}</Link>
                ) : (
                  <span aria-current="page" className="text-white">{c.name}</span>
                )}
              </li>
            ))}
          </ol>
        </nav>
        {eyebrow && <p className="eyebrow mt-6 text-brand-yellow">{eyebrow}</p>}
        <h1 className="mt-3 max-w-4xl text-3xl font-extrabold text-white sm:text-4xl lg:text-5xl">{title}</h1>
        {lead && <p className="mt-4 max-w-3xl text-base text-navy-100 sm:text-lg">{lead}</p>}
        {children && <div className="mt-8">{children}</div>}
      </div>
      <JsonLd data={breadcrumbJsonLd(all)} />
    </section>
  );
}
