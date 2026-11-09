"use client";

import Script from "next/script";
import { useEffect } from "react";
import { GA_ID, trackEvent } from "@/lib/analytics";

/**
 * Google Analytics 4 (only loads when NEXT_PUBLIC_GA_MEASUREMENT_ID is set),
 * plus automatic tracking of phone and WhatsApp clicks as lead events.
 */
export function Analytics() {
  useEffect(() => {
    if (!GA_ID) return;
    const onClick = (e: MouseEvent) => {
      const a = (e.target as HTMLElement | null)?.closest?.("a");
      if (!a) return;
      const href = a.getAttribute("href") ?? "";
      if (href.startsWith("tel:")) trackEvent("click_to_call", { page: location.pathname });
      else if (href.includes("wa.me/")) trackEvent("whatsapp_click", { page: location.pathname });
    };
    document.addEventListener("click", onClick);
    return () => document.removeEventListener("click", onClick);
  }, []);

  if (!GA_ID) return null;
  return (
    <>
      <Script src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`} strategy="afterInteractive" />
      <Script id="ga4" strategy="afterInteractive">
        {`window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','${GA_ID}');`}
      </Script>
    </>
  );
}
