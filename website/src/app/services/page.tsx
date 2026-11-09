import Link from "next/link";
import { CalendarCheck, CheckCircle2 } from "lucide-react";
import { services } from "@/data/services";
import { pageMetadata } from "@/lib/seo";
import { serviceWhatsappMessage, whatsappLink } from "@/lib/whatsapp";
import { PageHero } from "@/components/PageHero";
import { ServiceIcon } from "@/components/ServiceIcon";
import { WhatsAppIcon } from "@/components/WhatsAppIcon";
import { WhyChooseUs } from "@/components/WhyChooseUs";
import { CtaBanner } from "@/components/CtaBanner";
import { JsonLd } from "@/components/JsonLd";
import { absoluteUrl } from "@/lib/seo";

export const metadata = pageMetadata({
  title: "EB Phase Changeover Installation, Repair & Electrical Panel Installation in Chennai",
  description:
    "Electrical services in Chennai: EB phase changeover switch installation, EB to generator changeover, automatic changeover, electrical panel installation, changeover switch repair, wiring, load assessment and maintenance.",
  path: "/services",
});

export default function ServicesPage() {
  return (
    <>
      <PageHero
        eyebrow="Our Services"
        title="Electrical Installation, Repair & Maintenance Services in Chennai"
        lead="Phase changeover installation, generator changeover, electrical panels, troubleshooting and preventive maintenance — for homes, apartments, commercial buildings and industries."
        crumbs={[{ name: "Services", path: "/services" }]}
      >
        <div className="flex flex-wrap gap-3">
          <Link href="/contact#enquiry" className="btn-primary">
            <CalendarCheck className="h-5 w-5" aria-hidden="true" /> Book a Service
          </Link>
          <a href={whatsappLink()} target="_blank" rel="noopener noreferrer" className="btn-whatsapp">
            <WhatsAppIcon /> WhatsApp Us
          </a>
        </div>
      </PageHero>

      <section className="section">
        <div className="container-x">
          <nav aria-label="Services on this page" className="card mb-12 p-5">
            <p className="text-sm font-bold text-navy-950">Jump to a service</p>
            <ul className="mt-3 flex flex-wrap gap-2">
              {services.map((s) => (
                <li key={s.slug}>
                  <a href={`#${s.slug}`} className="inline-block rounded-full bg-navy-50 px-3 py-1.5 text-xs font-semibold text-navy-800 hover:bg-brand-orange hover:text-white sm:text-sm">
                    {s.name}
                  </a>
                </li>
              ))}
            </ul>
          </nav>

          <div className="grid gap-6 lg:grid-cols-2">
            {services.map((s, i) => (
              <article key={s.slug} id={s.slug} className="card flex flex-col p-6 sm:p-8">
                <div className="flex items-start gap-4">
                  <span className="grid h-14 w-14 shrink-0 place-items-center rounded-2xl bg-navy-950 text-brand-yellow">
                    <ServiceIcon name={s.icon} className="h-7 w-7" />
                  </span>
                  <div>
                    <p className="text-xs font-bold text-brand-orange">SERVICE {String(i + 1).padStart(2, "0")}</p>
                    <h2 className="mt-1 text-xl font-extrabold sm:text-2xl">{s.name}</h2>
                  </div>
                </div>
                <p className="mt-4 text-slate-600">{s.summary}</p>
                <ul className="mt-4 flex-1 space-y-2">
                  {s.details.map((d) => (
                    <li key={d} className="flex items-start gap-2 text-sm text-slate-700">
                      <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-green-600" aria-hidden="true" /> {d}
                    </li>
                  ))}
                </ul>
                <div className="mt-6 flex flex-wrap gap-3">
                  <a href={whatsappLink(serviceWhatsappMessage(s.name))} target="_blank" rel="noopener noreferrer" className="btn-whatsapp !py-2.5 !text-sm">
                    <WhatsAppIcon className="h-4 w-4" /> Book on WhatsApp
                  </a>
                  <Link href={`/contact?service=${s.slug}#enquiry`} className="btn-outline !py-2.5 !text-sm">
                    Request a visit
                  </Link>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <WhyChooseUs />
      <CtaBanner />

      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "ItemList",
          itemListElement: services.map((s, i) => ({
            "@type": "ListItem",
            position: i + 1,
            item: {
              "@type": "Service",
              name: s.name,
              description: s.summary,
              url: absoluteUrl(`/services#${s.slug}`),
              areaServed: { "@type": "City", name: "Chennai" },
              provider: { "@id": absoluteUrl("/#business") },
            },
          })),
        }}
      />
    </>
  );
}
