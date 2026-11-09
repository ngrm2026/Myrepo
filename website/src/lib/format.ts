import { siteConfig } from "@/config/site";

export function formatAddress() {
  const a = siteConfig.address;
  return `${a.street}, ${a.locality}, ${a.city}, ${a.region} – ${a.postalCode}`;
}

export function to12h(t: string) {
  const [h, m] = t.split(":").map(Number);
  const suffix = h >= 12 ? "PM" : "AM";
  const hh = h % 12 === 0 ? 12 : h % 12;
  return `${hh}:${String(m).padStart(2, "0")} ${suffix}`;
}

export function formatHours() {
  return siteConfig.hours.map((h) =>
    h.opens && h.closes ? `${h.label}: ${to12h(h.opens)} – ${to12h(h.closes)}` : `${h.label}: Closed`,
  );
}
