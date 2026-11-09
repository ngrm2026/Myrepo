/** Google Analytics 4 measurement ID — set NEXT_PUBLIC_GA_MEASUREMENT_ID to enable analytics. */
export const GA_ID = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID ?? "";

type Gtag = (command: "event", name: string, params?: Record<string, unknown>) => void;

/** Send an analytics event (no-op when analytics is not configured). */
export function trackEvent(name: string, params?: Record<string, unknown>) {
  if (typeof window === "undefined") return;
  const gtag = (window as unknown as { gtag?: Gtag }).gtag;
  gtag?.("event", name, params);
}
