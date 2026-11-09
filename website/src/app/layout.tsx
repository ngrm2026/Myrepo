import type { Metadata, Viewport } from "next";
import { Inter, Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";
import { siteConfig } from "@/config/site";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { FloatingWhatsApp } from "@/components/FloatingWhatsApp";
import { MobileActionBar } from "@/components/MobileActionBar";
import { Analytics } from "@/components/Analytics";
import { JsonLd } from "@/components/JsonLd";
import { localBusinessJsonLd } from "@/lib/seo";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });
const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-jakarta",
  weight: ["600", "700", "800"],
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL(siteConfig.url),
  title: {
    default: `EB Switch & Phase Changeover Switch Sales and Services in Chennai | ${siteConfig.name}`,
    template: `%s | ${siteConfig.name}`,
  },
  description:
    "EB switch sales, phase changeover switch installation and repair in Chennai. Manual & automatic phase changeover, EB to generator changeover, electrical panels, MCB, MCCB. Call or WhatsApp now.",
  applicationName: siteConfig.name,
  keywords: [
    "EB Switch Sales Chennai",
    "Phase Changeover Switch Chennai",
    "EB Phase Changeover Installation Chennai",
    "Automatic Phase Changeover Switch Chennai",
    "Electrical Changeover Switch Repair Chennai",
    "Three Phase Changeover Switch Chennai",
    "Electrical Panel Installation Chennai",
    "EB Switch Dealers Chennai",
    "Electrical Services Near Me Chennai",
  ],
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    locale: "en_IN",
    siteName: siteConfig.name,
    url: "/",
  },
  twitter: { card: "summary_large_image" },
  robots: { index: true, follow: true },
  formatDetection: { telephone: false },
  verification: process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION
    ? { google: process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION }
    : undefined,
  other: { "geo.region": "IN-TN", "geo.placename": "Chennai" },
};

export const viewport: Viewport = {
  themeColor: "#071328",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en-IN" className={`${inter.variable} ${jakarta.variable}`}>
      <body className="flex min-h-dvh flex-col">
        <a href="#main" className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-[60] focus:rounded focus:bg-white focus:px-4 focus:py-2 focus:shadow">
          Skip to content
        </a>
        <Header />
        <main id="main" className="flex-1">{children}</main>
        <Footer />
        <FloatingWhatsApp />
        <MobileActionBar />
        <Analytics />
        <JsonLd data={localBusinessJsonLd()} />
      </body>
    </html>
  );
}
