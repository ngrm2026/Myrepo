import Image from "next/image";
import Link from "next/link";
import {
  ArrowRight, Building, Building2, CalendarCheck, CheckCircle2, ClipboardCheck, Factory, HardHat, House,
  MapPin, PhoneCall, Phone, Store, Wrench,
} from "lucide-react";
import { siteConfig } from "@/config/site";
import { products } from "@/data/products";
import { services } from "@/data/services";
import { areas, otherAreasNote } from "@/data/areas";
import { faqs } from "@/data/faqs";
import { telLink, whatsappLink } from "@/lib/whatsapp";
import { pageMetadata } from "@/lib/seo";
import { WhatsAppIcon } from "@/components/WhatsAppIcon";
import { ProductCard } from "@/components/ProductCard";
import { ServiceCard } from "@/components/ServiceCard";
import { SectionHeading } from "@/components/SectionHeading";
import { WhyChooseUs } from "@/components/WhyChooseUs";
import { Testimonials } from "@/components/Testimonials";
import { FaqList } from "@/components/FaqList";
import { CtaBanner } from "@/components/CtaBanner";

export const metadata = pageMetadata({
  title: `EB Switch & Phase Changeover Switch Sales, Installation & Repair in Chennai`,
  description:
    "Reliable EB switch and phase changeover solutions in Chennai — manual & automatic phase changeover switches, EB to generator changeover, electrical panels, MCB/MCCB sales, installation, repair and maintenance.",
  path: "/",
});

const audiences = [
  { icon: House, label: "Homeowners" },
  { icon: Building2, label: "Apartments" },
  { icon: Building, label: "Residential Associations" },
  { icon: Store, label: "Shops & Showrooms" },
  { icon: Building2, label: "Offices & Commercial" },
  { icon: Factory, label: "Industries" },
  { icon: HardHat, label: "Builders" },
];

const steps = [
  { icon: PhoneCall, title: "Call or WhatsApp", text: "Tell us your requirement or send a photo of your EB board." },
  { icon: ClipboardCheck, title: "Assessment", text: "We check your supply, load and existing setup — on call or on site." },
  { icon: CheckCircle2, title: "Clear Quotation", text: "You get the right product options and a clear price before work starts." },
  { icon: Wrench, title: "Install & Test", text: "Neat installation, full testing and a quick demo of how to use it." },
];

export default function HomePage() {
  return (
    <>
      {/* HERO */}
      <section className="relative overflow-hidden bg-navy-950 text-white">
        <div className="bg-grid absolute inset-0" aria-hidden="true" />
        <div className="absolute top-1/3 -left-40 h-96 w-96 rounded-full bg-navy-600/40 blur-3xl" aria-hidden="true" />
        <div className="absolute -right-32 -bottom-32 h-[28rem] w-[28rem] rounded-full bg-brand-orange/25 blur-3xl" aria-hidden="true" />
        <div className="container-x relative grid items-center gap-12 py-14 sm:py-20 lg:grid-cols-[1.05fr_1fr] lg:py-24">
          <div>
            <p className="inline-flex items-center gap-2 rounded-full border border-brand-yellow/30 bg-brand-yellow/10 px-3 py-1 text-xs font-semibold text-brand-yellow sm:text-sm">
              <span className="h-2 w-2 rounded-full bg-brand-yellow" aria-hidden="true" />
              EB Switch &amp; Phase Changeover · Sales &amp; Services · Chennai
            </p>
            <h1 className="mt-5 text-4xl leading-[1.1] font-extrabold text-white sm:text-5xl lg:text-[3.4rem]">
              Reliable <span className="text-brand-yellow">EB Switch</span> &amp;{" "}
              <span className="bg-gradient-to-r from-brand-yellow to-brand-orange bg-clip-text text-transparent">
                Phase Changeover
              </span>{" "}
              Solutions in Chennai
            </h1>
            <p className="mt-5 max-w-xl text-lg text-navy-100">
              Your Trusted Partner for EB Switches, Phase Changeover Systems, Electrical Installation, Repair and
              Maintenance Services.
            </p>
            <div className="mt-8 grid grid-cols-2 gap-3 sm:flex sm:flex-wrap">
              <a href={telLink} className="btn-primary">
                <Phone className="h-5 w-5" aria-hidden="true" /> Call Now
              </a>
              <a href={whatsappLink()} target="_blank" rel="noopener noreferrer" className="btn-whatsapp">
                <WhatsAppIcon /> WhatsApp Us
              </a>
              <Link href="/products" className="btn-yellow">
                Explore Products <ArrowRight className="h-5 w-5" aria-hidden="true" />
              </Link>
              <Link href="/contact#enquiry" className="btn-outline-light">
                <CalendarCheck className="h-5 w-5" aria-hidden="true" /> Book a Service
              </Link>
            </div>
            <ul className="mt-8 grid gap-2 text-sm text-navy-100 sm:grid-cols-2">
              {[
                "Manual & automatic phase changeover",
                "EB to generator changeover",
                "Electrical panels, MCB & MCCB",
                "Installation, repair & maintenance",
              ].map((t) => (
                <li key={t} className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 shrink-0 text-brand-yellow" aria-hidden="true" /> {t}
                </li>
              ))}
            </ul>
          </div>
          <div className="relative">
            <div className="relative overflow-hidden rounded-3xl border border-white/10 shadow-2xl shadow-black/40">
              <Image
                src="/images/hero-changeover-panel.svg"
                alt="Phase changeover switch and electrical panel installation by Chennai electrical technicians"
                width={890}
                height={650}
                priority
                className="h-auto w-full"
              />
            </div>
            <div className="absolute -bottom-10 left-4 flex items-center gap-3 rounded-2xl bg-white px-4 py-3 text-navy-950 shadow-xl sm:left-8">
              <span className="grid h-10 w-10 place-items-center rounded-xl bg-brand-orange text-white">
                <MapPin className="h-5 w-5" aria-hidden="true" />
              </span>
              <span className="text-sm leading-tight">
                <span className="block font-bold">Serving across Chennai</span>
                <span className="text-slate-500">Velachery · OMR · Tambaram & more</span>
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* AUDIENCES */}
      <section aria-label="Who we serve" className="border-b border-slate-200 bg-white">
        <div className="container-x py-6">
          <ul className="flex flex-wrap items-center justify-center gap-x-6 gap-y-3 text-sm font-semibold text-navy-800">
            {audiences.map(({ icon: Icon, label }) => (
              <li key={label} className="flex items-center gap-2">
                <Icon className="h-4 w-4 text-brand-orange" aria-hidden="true" /> {label}
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* PRODUCTS */}
      <section className="section bg-slate-50">
        <div className="container-x">
          <div className="flex flex-col justify-between gap-6 md:flex-row md:items-end">
            <SectionHeading
              eyebrow="Products – Sales"
              title="EB switches, phase changeover switches & panels"
              lead="Quality changeover switches, distribution boards, MCB, MCCB, contactors, switchgear and custom panels — supplied with expert advice on the right rating for your load."
            />
            <Link href="/products" className="btn-outline shrink-0">
              View all products <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          </div>
          <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {products.slice(0, 6).map((p) => (
              <ProductCard key={p.slug} product={p} />
            ))}
          </div>
        </div>
      </section>

      {/* SERVICES */}
      <section className="section">
        <div className="container-x">
          <div className="flex flex-col justify-between gap-6 md:flex-row md:items-end">
            <SectionHeading
              eyebrow="Our Services"
              title="Installation, repair & maintenance services"
              lead="From EB phase changeover installation to complete electrical panel work — handled by experienced technicians across Chennai."
            />
            <Link href="/services" className="btn-outline shrink-0">
              All services <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          </div>
          <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {services.slice(0, 8).map((s) => (
              <ServiceCard key={s.slug} service={s} />
            ))}
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="section bg-navy-50/60">
        <div className="container-x">
          <SectionHeading center eyebrow="How It Works" title="Getting your changeover installed is simple" />
          <ol className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {steps.map(({ icon: Icon, title, text }, i) => (
              <li key={title} className="card relative p-6">
                <span className="absolute top-5 right-5 font-display text-4xl font-extrabold text-navy-100">0{i + 1}</span>
                <span className="grid h-12 w-12 place-items-center rounded-xl bg-brand-orange text-white">
                  <Icon className="h-6 w-6" aria-hidden="true" />
                </span>
                <h3 className="mt-5 text-lg font-bold">{title}</h3>
                <p className="mt-2 text-sm text-slate-600">{text}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <WhyChooseUs />

      {/* SERVICE AREAS */}
      <section className="section">
        <div className="container-x grid items-center gap-10 lg:grid-cols-2">
          <div>
            <SectionHeading
              eyebrow="Service Areas"
              title="Electrical services near you in Chennai"
              lead="We provide EB switch sales, phase changeover installation, repair and electrical panel services across South Chennai and the OMR corridor."
            />
            <p className="mt-4 text-sm text-slate-500">{otherAreasNote}</p>
            <Link href="/service-areas" className="btn-primary mt-6">
              View service areas <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          </div>
          <ul className="flex flex-wrap gap-2.5">
            {areas.map((a) => (
              <li key={a.slug}>
                <Link
                  href={`/service-areas#${a.slug}`}
                  className="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-navy-900 shadow-sm transition hover:border-brand-orange hover:text-brand-orange"
                >
                  <MapPin className="h-4 w-4 text-brand-orange" aria-hidden="true" /> {a.name}
                </Link>
              </li>
            ))}
            <li className="inline-flex items-center rounded-full border border-dashed border-slate-300 px-4 py-2 text-sm text-slate-500">
              + Other Chennai locations
            </li>
          </ul>
        </div>
      </section>

      <Testimonials />

      {/* FAQ */}
      <section className="section">
        <div className="container-x grid gap-10 lg:grid-cols-[1fr_1.6fr]">
          <div>
            <SectionHeading
              eyebrow="FAQ"
              title="Frequently asked questions"
              lead="Quick answers about phase changeover switches, generator changeover and our services."
            />
            <div className="mt-6 flex flex-wrap gap-3">
              <a href={whatsappLink()} target="_blank" rel="noopener noreferrer" className="btn-whatsapp">
                <WhatsAppIcon /> Ask on WhatsApp
              </a>
              <a href={telLink} className="btn-outline">
                <Phone className="h-4 w-4" aria-hidden="true" /> {siteConfig.phoneDisplay}
              </a>
            </div>
          </div>
          <FaqList items={faqs.slice(0, 6)} />
        </div>
      </section>

      <CtaBanner />
    </>
  );
}
