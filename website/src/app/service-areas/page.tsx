import Link from "next/link";
import { MapPin, Phone } from "lucide-react";
import { areas, otherAreasNote } from "@/data/areas";
import { services } from "@/data/services";
import { siteConfig } from "@/config/site";
import { pageMetadata } from "@/lib/seo";
import { telLink, whatsappLink } from "@/lib/whatsapp";
import { PageHero } from "@/components/PageHero";
import { WhatsAppIcon } from "@/components/WhatsAppIcon";
import { MapEmbed } from "@/components/MapEmbed";
import { CtaBanner } from "@/components/CtaBanner";

export const metadata = pageMetadata({
  title: "Electrical Services Near Me in Chennai – Velachery, OMR, Tambaram & More",
  description:
    "Phase changeover switch installation, EB switch sales and electrical panel services in Velachery, Madipakkam, Medavakkam, Pallikaranai, Tambaram, Perungudi, Thoraipakkam, Adyar, Guindy, Taramani, Sholinganallur and OMR, Chennai.",
  path: "/service-areas",
});

const popular = services.slice(0, 6);

export default function ServiceAreasPage() {
  return (
    <>
      <PageHero
        eyebrow="Service Areas"
        title="EB Switch & Phase Changeover Services Across Chennai"
        lead="Looking for electrical services near you in Chennai? We cover South Chennai and the OMR corridor for changeover switch sales, installation, repair and electrical panel work."
        crumbs={[{ name: "Service Areas", path: "/service-areas" }]}
      />

      <section className="section">
        <div className="container-x">
          <ul className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {areas.map((a) => (
              <li key={a.slug} id={a.slug} className="card flex flex-col p-6">
                <h2 className="flex items-center gap-2 text-xl font-extrabold">
                  <MapPin className="h-5 w-5 text-brand-orange" aria-hidden="true" />
                  Electrical Services in {a.name}
                </h2>
                <p className="mt-3 flex-1 text-sm text-slate-600">{a.note}</p>
                <a
                  href={whatsappLink(`Hello, I need EB switch / phase changeover service in ${a.name}, Chennai. Please share the details.`)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-whatsapp-dark hover:underline"
                >
                  <WhatsAppIcon className="h-4 w-4" /> Enquire for {a.name}
                </a>
              </li>
            ))}
          </ul>
          <div className="mt-8 rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center">
            <p className="font-semibold text-navy-950">Other Chennai locations</p>
            <p className="mt-1 text-sm text-slate-600">{otherAreasNote}</p>
            <div className="mt-4 flex flex-wrap justify-center gap-3">
              <a href={telLink} className="btn-primary !py-2.5 !text-sm">
                <Phone className="h-4 w-4" aria-hidden="true" /> {siteConfig.phoneDisplay}
              </a>
              <a href={whatsappLink()} target="_blank" rel="noopener noreferrer" className="btn-whatsapp !py-2.5 !text-sm">
                <WhatsAppIcon className="h-4 w-4" /> Check availability
              </a>
            </div>
          </div>
        </div>
      </section>

      <section className="section bg-slate-50">
        <div className="container-x grid gap-10 lg:grid-cols-2">
          <div>
            <h2 className="text-2xl font-extrabold sm:text-3xl">Services available in all our areas</h2>
            <ul className="mt-6 space-y-3">
              {popular.map((s) => (
                <li key={s.slug}>
                  <Link href={`/services#${s.slug}`} className="card block p-4 font-semibold text-navy-900 hover:border-brand-orange hover:text-brand-orange">
                    {s.name}
                  </Link>
                </li>
              ))}
            </ul>
            <Link href="/services" className="btn-outline mt-6">All services</Link>
          </div>
          <MapEmbed className="h-full min-h-96" />
        </div>
      </section>

      <CtaBanner />
    </>
  );
}
