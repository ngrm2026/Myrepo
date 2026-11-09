import type { MetadataRoute } from "next";
import { navLinks } from "@/config/site";
import { products } from "@/data/products";
import { absoluteUrl } from "@/lib/seo";

export default function sitemap(): MetadataRoute.Sitemap {
  const pages = navLinks.map((l) => ({
    url: absoluteUrl(l.href),
    changeFrequency: "monthly" as const,
    priority: l.href === "/" ? 1 : l.href === "/products" || l.href === "/services" ? 0.9 : 0.7,
  }));
  const productPages = products.map((p) => ({
    url: absoluteUrl(`/products/${p.slug}`),
    changeFrequency: "monthly" as const,
    priority: 0.8,
  }));
  return [...pages, ...productPages];
}
