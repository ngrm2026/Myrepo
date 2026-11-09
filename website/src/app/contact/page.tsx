import { Suspense } from "react";
import { Clock, Mail, MapPin, Navigation, Phone } from "lucide-react";
import { siteConfig } from "@/config/site";
import { faqs } from "@/data/faqs";
import { pageMetadata } from "@/lib/seo";
import { formatAddress, formatHours } from "@/lib/format";
import { mailLink, telLink, whatsappLink } from "@/lib/whatsapp";
import { PageHero } from "@/components/PageHero";
import { EnquiryForm, EnquiryFormWithParams } from "@/components/EnquiryForm";
import { MapEmbed } from "@/components/MapEmbed";
import { FaqList } from "@/components/FaqList";
import { WhatsAppIcon } from "@/components/WhatsAppIcon";
import { SectionHeading } from "@/components/SectionHeading";

export const metadata = pageMetadata({
  title: "Contact Us – Book EB Switch & Phase Changeover Service in Chennai",
  description: `Contact ${siteConfig.name} for EB switch sales, phase changeover installation and electrical repair in Chennai. Call, WhatsApp or send an enquiry online.`,
  path: "/contact",
});

export default function ContactPage() {
  const directions =
    siteConfig.googleBusinessUrl ||
    `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(siteConfig.mapQuery)}`;

  const items = [
    { icon: Phone, label: "Phone", value: siteConfig.phoneDisplay, href: telLink },
    { icon: WhatsAppIcon, label: "WhatsApp", value: siteConfig.whatsappDisplay, href: whatsappLink(), external: true },
    { icon: Mail, label: "Email", value: siteConfig.email, href: mailLink },
  ];

  return (
    <>
      <PageHero
        eyebrow="Contact Us"
        title="Get in Touch – Sales, Installation & Service Bookings"
        lead="Call, WhatsApp or send us your requirement. Share a photo of your EB board on WhatsApp for the quickest recommendation."
        crumbs={[{ name: "Contact Us", path: "/contact" }]}
      />

      <section className="section">
        <div className="container-x grid gap-10 lg:grid-cols-[1fr_1.5fr]">
          <div className="space-y-6">
            <div className="card p-6">
              <h2 className="text-xl font-extrabold">{siteConfig.name}</h2>
              <p className="mt-1 text-sm text-slate-500">{siteConfig.tagline}</p>
              <ul className="mt-6 space-y-4">
                {items.map(({ icon: Icon, label, value, href, external }) => (
                  <li key={label}>
                    <a
                      href={href}
                      {...(external ? { target: "_blank", rel: "noopener noreferrer" } : {})}
                      className="group flex items-center gap-4"
                    >
                      <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-navy-950 text-brand-yellow group-hover:bg-brand-orange group-hover:text-white">
                        <Icon className="h-5 w-5" />
                      </span>
                      <span>
                        <span className="block text-xs font-semibold tracking-wide text-slate-500 uppercase">{label}</span>
                        <span className="font-semibold break-all text-navy-950 group-hover:text-brand-orange">{value}</span>
                      </span>
                    </a>
                  </li>
                ))}
                <li className="flex items-start gap-4">
                  <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-navy-950 text-brand-yellow">
                    <MapPin className="h-5 w-5" aria-hidden="true" />
                  </span>
                  <span>
                    <span className="block text-xs font-semibold tracking-wide text-slate-500 uppercase">Address</span>
                    <address className="font-semibold text-navy-950 not-italic">{formatAddress()}</address>
                    <a href={directions} target="_blank" rel="noopener noreferrer" className="mt-1 inline-flex items-center gap-1 text-sm font-semibold text-navy-600 hover:text-brand-orange">
                      <Navigation className="h-4 w-4" aria-hidden="true" /> Get directions
                    </a>
                  </span>
                </li>
                <li className="flex items-start gap-4">
                  <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-navy-950 text-brand-yellow">
                    <Clock className="h-5 w-5" aria-hidden="true" />
                  </span>
                  <span>
                    <span className="block text-xs font-semibold tracking-wide text-slate-500 uppercase">Working Hours</span>
                    {formatHours().map((h) => (
                      <span key={h} className="block font-semibold text-navy-950">{h}</span>
                    ))}
                    {siteConfig.hoursNote && <span className="mt-1 block text-sm text-slate-500">{siteConfig.hoursNote}</span>}
                  </span>
                </li>
              </ul>
              <div className="mt-6 grid grid-cols-2 gap-3">
                <a href={telLink} className="btn-primary">
                  <Phone className="h-5 w-5" aria-hidden="true" /> Call
                </a>
                <a href={whatsappLink()} target="_blank" rel="noopener noreferrer" className="btn-whatsapp">
                  <WhatsAppIcon /> WhatsApp
                </a>
              </div>
            </div>
            <MapEmbed className="h-80" />
          </div>

          <div id="enquiry" className="card p-6 sm:p-8">
            <h2 className="text-2xl font-extrabold">Send an Enquiry / Book a Service</h2>
            <p className="mt-2 mb-6 text-slate-600">
              Fill in the form and our team will call you back. Fields marked * are required.
            </p>
            <Suspense fallback={<EnquiryForm />}>
              <EnquiryFormWithParams />
            </Suspense>
          </div>
        </div>
      </section>

      <section className="section bg-slate-50">
        <div className="container-x grid gap-10 lg:grid-cols-[1fr_1.6fr]">
          <SectionHeading eyebrow="FAQ" title="Questions before you call?" lead="Here are answers to the questions we hear most often." />
          <FaqList items={faqs} />
        </div>
      </section>
    </>
  );
}
