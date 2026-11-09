import { Clock, Mail, Phone } from "lucide-react";
import { siteConfig } from "@/config/site";
import { mailLink, telLink } from "@/lib/whatsapp";
import { Logo } from "./Logo";
import { to12h } from "@/lib/format";
import { DesktopNav, MobileNav } from "./NavLinks";

export function Header() {
  const weekday = siteConfig.hours.find((h) => h.opens);
  return (
    <header className="sticky top-0 z-50">
      <div className="hidden bg-navy-950 text-navy-100 md:block">
        <div className="container-x flex h-9 items-center justify-between text-xs">
          <p className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-brand-yellow" aria-hidden="true" />
            EB Switch &amp; Phase Changeover Sales and Services across Chennai
          </p>
          <div className="flex items-center gap-5">
            {weekday && (
              <span className="flex items-center gap-1.5">
                <Clock className="h-3.5 w-3.5 text-brand-yellow" aria-hidden="true" />
                {weekday.label}: {to12h(weekday.opens)} – {to12h(weekday.closes)}
              </span>
            )}
            <a href={mailLink} className="flex items-center gap-1.5 hover:text-white">
              <Mail className="h-3.5 w-3.5 text-brand-yellow" aria-hidden="true" />
              {siteConfig.email}
            </a>
          </div>
        </div>
      </div>
      <div className="border-b border-slate-200/80 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/85">
        <div className="container-x flex h-[4.5rem] items-center justify-between gap-4">
          <Logo />
          <DesktopNav />
          <div className="flex items-center gap-2">
            <a href={telLink} className="btn-primary hidden !px-4 !py-2.5 sm:inline-flex">
              <Phone className="h-4 w-4" aria-hidden="true" />
              <span className="hidden xl:inline">{siteConfig.phoneDisplay}</span>
              <span className="xl:hidden">Call Now</span>
            </a>
            <MobileNav />
          </div>
        </div>
      </div>
    </header>
  );
}
