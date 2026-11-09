import Link from "next/link";
import { CalendarCheck, Phone } from "lucide-react";
import { siteConfig } from "@/config/site";
import { telLink, whatsappLink } from "@/lib/whatsapp";
import { WhatsAppIcon } from "./WhatsAppIcon";

export function CtaBanner({
  title = "Power cut on one phase? Get a phase changeover switch installed.",
  text = "Call or WhatsApp us with a photo of your EB board — we will suggest the right changeover switch and share a quotation.",
}: {
  title?: string;
  text?: string;
}) {
  return (
    <section className="section !py-14">
      <div className="container-x">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-brand-orange to-orange-600 px-6 py-10 text-white shadow-2xl shadow-orange-600/30 sm:px-12 sm:py-14">
          <svg className="absolute -right-10 -bottom-10 h-64 w-64 text-white/10" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M13.5 2 4 13.5h6.2L9 22l10-12.2h-6.3L13.5 2Z" />
          </svg>
          <div className="relative grid items-center gap-8 lg:grid-cols-[1fr_auto]">
            <div>
              <h2 className="text-2xl font-extrabold text-white sm:text-3xl">{title}</h2>
              <p className="mt-3 max-w-2xl text-orange-50">{text}</p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              <a href={telLink} className="btn bg-navy-950 text-white hover:bg-navy-900">
                <Phone className="h-5 w-5" aria-hidden="true" /> {siteConfig.phoneDisplay}
              </a>
              <a href={whatsappLink()} target="_blank" rel="noopener noreferrer" className="btn-whatsapp">
                <WhatsAppIcon /> WhatsApp Us
              </a>
              <Link href="/contact#enquiry" className="btn bg-white text-navy-950 hover:bg-orange-50">
                <CalendarCheck className="h-5 w-5" aria-hidden="true" /> Book a Service
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
