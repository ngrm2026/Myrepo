import Link from "next/link";
import { Clock, Mail, MapPin, Phone } from "lucide-react";
import { navLinks, siteConfig } from "@/config/site";
import { products } from "@/data/products";
import { areas } from "@/data/areas";
import { mailLink, telLink, whatsappLink } from "@/lib/whatsapp";
import { Logo } from "./Logo";
import { WhatsAppIcon } from "./WhatsAppIcon";
import { formatAddress, formatHours } from "@/lib/format";

export function Footer() {
  const { credentials } = siteConfig;
  return (
    <footer className="bg-navy-950 pb-20 text-navy-200 lg:pb-0">
      <div className="container-x grid gap-10 py-14 sm:grid-cols-2 lg:grid-cols-12">
        <div className="lg:col-span-4">
          <Logo light />
          <p className="mt-4 max-w-sm text-sm leading-relaxed">
            {siteConfig.name} — sales, installation, repair and maintenance of EB switches, phase changeover
            switches and electrical panels for homes, apartments, commercial buildings and industries in Chennai.
          </p>
          {(credentials.licence || credentials.gstin) && (
            <ul className="mt-4 space-y-1 text-xs text-navy-300">
              {credentials.licence && <li>{credentials.licence}</li>}
              {credentials.gstin && <li>GSTIN: {credentials.gstin}</li>}
            </ul>
          )}
          <div className="mt-6 flex flex-wrap gap-3">
            <a href={telLink} className="btn-primary !py-2.5 text-sm">
              <Phone className="h-4 w-4" aria-hidden="true" /> Call Now
            </a>
            <a href={whatsappLink()} target="_blank" rel="noopener noreferrer" className="btn-whatsapp !py-2.5 text-sm">
              <WhatsAppIcon className="h-4 w-4" /> WhatsApp
            </a>
          </div>
        </div>

        <div className="lg:col-span-2">
          <h2 className="text-sm font-bold tracking-wider text-white uppercase">Quick Links</h2>
          <ul className="mt-4 space-y-2.5 text-sm">
            {navLinks.map((l) => (
              <li key={l.href}>
                <Link href={l.href} className="hover:text-brand-yellow">{l.label}</Link>
              </li>
            ))}
          </ul>
        </div>

        <div className="lg:col-span-3">
          <h2 className="text-sm font-bold tracking-wider text-white uppercase">Products</h2>
          <ul className="mt-4 space-y-2.5 text-sm">
            {products.map((p) => (
              <li key={p.slug}>
                <Link href={`/products/${p.slug}`} className="hover:text-brand-yellow">{p.name}</Link>
              </li>
            ))}
          </ul>
        </div>

        <div className="lg:col-span-3">
          <h2 className="text-sm font-bold tracking-wider text-white uppercase">Contact</h2>
          <ul className="mt-4 space-y-3 text-sm">
            <li className="flex gap-3">
              <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-brand-yellow" aria-hidden="true" />
              <address className="not-italic">{formatAddress()}</address>
            </li>
            <li className="flex gap-3">
              <Phone className="mt-0.5 h-4 w-4 shrink-0 text-brand-yellow" aria-hidden="true" />
              <a href={telLink} className="hover:text-white">{siteConfig.phoneDisplay}</a>
            </li>
            <li className="flex gap-3">
              <Mail className="mt-0.5 h-4 w-4 shrink-0 text-brand-yellow" aria-hidden="true" />
              <a href={mailLink} className="break-all hover:text-white">{siteConfig.email}</a>
            </li>
            <li className="flex gap-3">
              <Clock className="mt-0.5 h-4 w-4 shrink-0 text-brand-yellow" aria-hidden="true" />
              <span>
                {formatHours().map((h) => (
                  <span key={h} className="block">{h}</span>
                ))}
              </span>
            </li>
          </ul>
        </div>
      </div>

      <div className="border-t border-white/10">
        <div className="container-x py-6 text-xs leading-relaxed">
          <p>
            <span className="font-semibold text-navy-100">Service areas: </span>
            {areas.map((a) => a.name).join(" · ")} and other Chennai locations, subject to availability.
          </p>
          <p className="mt-3 text-navy-400">
            © <CopyrightYear /> {siteConfig.name}. All rights reserved. Product images are illustrative.
          </p>
        </div>
      </div>
    </footer>
  );
}

async function CopyrightYear() {
  "use cache";
  return <>{new Date().getFullYear()}</>;
}
