import type { Metadata } from "next";
import { siteConfig } from "@/config/site";
import { areas } from "@/data/areas";
import { services } from "@/data/services";
import { products } from "@/data/products";
import type { Faq } from "@/data/faqs";

export const absoluteUrl = (path = "/") => new URL(path, siteConfig.url).toString();

/** Page-level metadata with canonical URL and social sharing tags. */
export function pageMetadata({
  title,
  description,
  path,
  keywords,
  image,
}: {
  title: string;
  description: string;
  path: string;
  keywords?: string[];
  image?: string;
}): Metadata {
  return {
    title,
    description,
    keywords,
    alternates: { canonical: path },
    openGraph: {
      title,
      description,
      url: path,
      type: "website",
      siteName: siteConfig.name,
      locale: "en_IN",
      ...(image ? { images: [{ url: image }] } : {}),
    },
    twitter: { card: "summary_large_image", title, description },
  };
}

/** Make JSON safe to embed in a <script> tag. */
export function jsonLdString(data: unknown) {
  return JSON.stringify(data).replace(/</g, "\\u003c");
}

const dayMap: Record<string, string> = {
  Mo: "Monday", Tu: "Tuesday", We: "Wednesday", Th: "Thursday", Fr: "Friday", Sa: "Saturday", Su: "Sunday",
};

/** LocalBusiness structured data. Empty optional fields are left out. */
export function localBusinessJsonLd() {
  const s = siteConfig;
  const sameAs = [s.googleBusinessUrl, s.social.facebook, s.social.instagram, s.social.youtube].filter(Boolean);
  return {
    "@context": "https://schema.org",
    "@type": "Electrician",
    "@id": absoluteUrl("/#business"),
    name: s.name,
    description:
      "EB switch and phase changeover switch sales, installation, repair and maintenance in Chennai. Electrical panels, distribution boards, MCB, MCCB, contactors and switchgear.",
    url: absoluteUrl("/"),
    telephone: s.phone,
    email: s.email,
    image: absoluteUrl("/opengraph-image"),
    logo: absoluteUrl("/icon.svg"),
    address: {
      "@type": "PostalAddress",
      streetAddress: s.address.street,
      addressLocality: `${s.address.locality}, ${s.address.city}`,
      addressRegion: s.address.region,
      postalCode: s.address.postalCode,
      addressCountry: s.address.country,
    },
    ...(s.geo ? { geo: { "@type": "GeoCoordinates", ...s.geo } } : {}),
    openingHoursSpecification: s.hours
      .filter((h) => h.opens && h.closes)
      .map((h) => ({
        "@type": "OpeningHoursSpecification",
        dayOfWeek: h.days.map((d) => dayMap[d]),
        opens: h.opens,
        closes: h.closes,
      })),
    areaServed: [
      ...areas.map((a) => ({ "@type": "Place", name: `${a.name}, Chennai` })),
      { "@type": "City", name: "Chennai" },
    ],
    ...(sameAs.length ? { sameAs } : {}),
    hasOfferCatalog: {
      "@type": "OfferCatalog",
      name: "EB Switch & Phase Changeover Products and Services",
      itemListElement: [
        ...services.map((sv) => ({
          "@type": "Offer",
          itemOffered: { "@type": "Service", name: sv.name, description: sv.summary, areaServed: "Chennai" },
        })),
        ...products.map((p) => ({
          "@type": "Offer",
          itemOffered: { "@type": "Product", name: p.name, description: p.shortDescription },
        })),
      ],
    },
  };
}

export function faqJsonLd(items: Faq[]) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items.map((f) => ({
      "@type": "Question",
      name: f.q,
      acceptedAnswer: { "@type": "Answer", text: f.a },
    })),
  };
}

export function breadcrumbJsonLd(items: { name: string; path: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((it, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: it.name,
      item: absoluteUrl(it.path),
    })),
  };
}
