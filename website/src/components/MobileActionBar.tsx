import Link from "next/link";
import { CalendarCheck, Phone } from "lucide-react";
import { telLink, whatsappLink } from "@/lib/whatsapp";
import { WhatsAppIcon } from "./WhatsAppIcon";

/** Sticky call / WhatsApp / book bar at the bottom of the screen on phones. */
export function MobileActionBar() {
  const item = "flex flex-1 flex-col items-center justify-center gap-0.5 py-2 text-[11px] font-semibold";
  return (
    <div className="fixed inset-x-0 bottom-0 z-40 border-t border-slate-200 bg-white pb-[env(safe-area-inset-bottom)] shadow-[0_-4px_20px_rgba(7,19,40,0.08)] lg:hidden">
      <div className="flex">
        <a href={telLink} className={`${item} bg-brand-orange text-white`}>
          <Phone className="h-5 w-5" aria-hidden="true" /> Call Now
        </a>
        <a href={whatsappLink()} target="_blank" rel="noopener noreferrer" className={`${item} bg-whatsapp text-white`}>
          <WhatsAppIcon className="h-5 w-5" /> WhatsApp
        </a>
        <Link href="/contact#enquiry" className={`${item} bg-navy-950 text-white`}>
          <CalendarCheck className="h-5 w-5 text-brand-yellow" aria-hidden="true" /> Book Service
        </Link>
      </div>
    </div>
  );
}
