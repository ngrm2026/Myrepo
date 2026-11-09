import { whatsappLink } from "@/lib/whatsapp";
import { WhatsAppIcon } from "./WhatsAppIcon";

/** Floating WhatsApp button shown on every page. */
export function FloatingWhatsApp() {
  return (
    <a
      href={whatsappLink()}
      target="_blank"
      rel="noopener noreferrer"
      aria-label="Chat with us on WhatsApp"
      className="group fixed right-4 bottom-20 z-40 flex items-center gap-2 lg:right-6 lg:bottom-6"
    >
      <span className="pointer-events-none hidden rounded-full bg-white px-3 py-1.5 text-sm font-semibold text-navy-950 shadow-lg ring-1 ring-slate-200 lg:group-hover:block">
        Chat on WhatsApp
      </span>
      <span className="relative grid h-14 w-14 place-items-center rounded-full bg-whatsapp text-white shadow-xl shadow-green-700/30 transition group-hover:scale-105">
        <span className="absolute inset-0 animate-pulse-ring rounded-full bg-whatsapp" aria-hidden="true" />
        <WhatsAppIcon className="relative h-8 w-8" />
      </span>
    </a>
  );
}
