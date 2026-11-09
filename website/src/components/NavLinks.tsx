"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { Menu, X, Phone } from "lucide-react";
import { navLinks, siteConfig } from "@/config/site";
import { telLink, whatsappLink } from "@/lib/whatsapp";
import { WhatsAppIcon } from "./WhatsAppIcon";

function isActive(pathname: string, href: string) {
  return href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);
}

export function DesktopNav() {
  const pathname = usePathname();
  return (
    <nav aria-label="Main" className="hidden lg:block">
      <ul className="flex items-center gap-1">
        {navLinks.map((l) => (
          <li key={l.href}>
            <Link
              href={l.href}
              aria-current={isActive(pathname, l.href) ? "page" : undefined}
              className="rounded-md px-3 py-2 text-sm font-semibold text-navy-900 transition hover:bg-navy-50 hover:text-brand-orange aria-[current=page]:text-brand-orange"
            >
              {l.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export function MobileNav() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  return (
    <div className="lg:hidden">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        aria-controls="mobile-menu"
        aria-label={open ? "Close menu" : "Open menu"}
        className="grid h-11 w-11 place-items-center rounded-lg border border-slate-200 text-navy-950"
      >
        {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>

      {open && (
        <div id="mobile-menu" className="fixed inset-x-0 top-[4.5rem] md:top-[6.75rem] bottom-0 z-40 overflow-y-auto bg-white">
          <nav aria-label="Mobile" className="container-x py-4">
            <ul className="divide-y divide-slate-100">
              {navLinks.map((l) => (
                <li key={l.href}>
                  <Link
                    href={l.href}
                    onClick={() => setOpen(false)}
                    aria-current={isActive(pathname, l.href) ? "page" : undefined}
                    className="block py-3.5 text-lg font-semibold text-navy-950 aria-[current=page]:text-brand-orange"
                  >
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
            <div className="mt-6 grid gap-3">
              <a href={telLink} className="btn-primary">
                <Phone className="h-5 w-5" /> Call {siteConfig.phoneDisplay}
              </a>
              <a href={whatsappLink()} target="_blank" rel="noopener noreferrer" className="btn-whatsapp">
                <WhatsAppIcon /> WhatsApp Us
              </a>
              <Link href="/contact#enquiry" onClick={() => setOpen(false)} className="btn-outline">
                Book a Service
              </Link>
            </div>
          </nav>
        </div>
      )}
    </div>
  );
}
