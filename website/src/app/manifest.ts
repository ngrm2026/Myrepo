import type { MetadataRoute } from "next";
import { siteConfig } from "@/config/site";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: siteConfig.name,
    short_name: siteConfig.shortName,
    description: "EB Switch & Phase Changeover Sales and Services in Chennai",
    start_url: "/",
    display: "standalone",
    background_color: "#ffffff",
    theme_color: "#071328",
    icons: [{ src: "/icon.svg", sizes: "any", type: "image/svg+xml" }],
  };
}
