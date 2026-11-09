/**
 * BUSINESS DETAILS — EDIT THIS FILE BEFORE GOING LIVE
 * ---------------------------------------------------------------
 * Every phone number, address and link on the website comes from here.
 * Values marked "REPLACE" are placeholders. Do not publish the site until
 * they are replaced with your real, verified details.
 *
 * Optional fields (left empty) are hidden automatically on the website.
 * Only fill in credentials (licence numbers, years of experience, etc.)
 * that you can verify.
 */

export const siteConfig = {
  /** Business name shown in the header, footer, page titles and Google data. */
  name: "Chennai EB Switch & Changeover Services", // REPLACE with your registered business name
  shortName: "EB Switch Chennai", // REPLACE (used for the mobile app name / small spaces)
  tagline: "EB Switch & Phase Changeover Sales and Services",

  /** Public website address, without a trailing slash. Can also be set with NEXT_PUBLIC_SITE_URL. */
  url: process.env.NEXT_PUBLIC_SITE_URL ?? "https://www.example.com", // REPLACE

  /** Phone number in international format (digits only, with country code) — used for click-to-call. */
  phone: "+910000000000", // REPLACE e.g. "+919876543210"
  /** How the phone number is displayed on the site. */
  phoneDisplay: "+91 00000 00000", // REPLACE e.g. "+91 98765 43210"

  /** WhatsApp number: digits only, with country code, no "+" or spaces. */
  whatsapp: "910000000000", // REPLACE e.g. "919876543210"
  whatsappDisplay: "+91 00000 00000", // REPLACE

  email: "info@example.com", // REPLACE

  address: {
    street: "Your street address", // REPLACE
    locality: "Velachery", // REPLACE with your area
    city: "Chennai",
    region: "Tamil Nadu",
    postalCode: "600042", // REPLACE
    country: "IN",
  },

  /**
   * Google Maps: the text searched on Google Maps for the embedded map.
   * Best: your exact business name as listed on Google Maps, plus area.
   */
  mapQuery: "Velachery, Chennai, Tamil Nadu", // REPLACE
  /** Optional: link to your Google Business Profile (for "Get directions" / reviews). */
  googleBusinessUrl: "",
  /** Optional: link where customers can read / write Google reviews. */
  googleReviewsUrl: "",
  /** Optional: exact map coordinates of your shop (improves local search data). */
  geo: null as null | { latitude: number; longitude: number },

  /** Working hours, shown on the site and sent to Google as structured data. */
  hours: [
    { label: "Monday – Saturday", days: ["Mo", "Tu", "We", "Th", "Fr", "Sa"], opens: "09:00", closes: "19:00" },
    { label: "Sunday", days: ["Su"], opens: "", closes: "" }, // empty = closed
  ], // REPLACE with your real hours
  /** Optional note, e.g. "Emergency breakdown support available on call". Leave empty if not offered. */
  hoursNote: "",

  /**
   * VERIFIED CREDENTIALS ONLY. Leave empty to hide.
   * e.g. yearsOfExperience: 12, licence: "Electrical Contractor Licence No. EA 1234"
   */
  credentials: {
    yearsOfExperience: null as number | null,
    licence: "",
    gstin: "",
  },

  social: {
    facebook: "",
    instagram: "",
    youtube: "",
  },

  /** Prefilled WhatsApp message used by the floating WhatsApp button. */
  whatsappDefaultMessage:
    "Hello, I am looking for EB Phase Changeover Switch Sales / Installation / Repair Services in Chennai. Please share the details.",
} as const;

export type SiteConfig = typeof siteConfig;

export const navLinks = [
  { href: "/", label: "Home" },
  { href: "/about", label: "About Us" },
  { href: "/products", label: "Products" },
  { href: "/services", label: "Services" },
  { href: "/service-areas", label: "Service Areas" },
  { href: "/gallery", label: "Gallery" },
  { href: "/contact", label: "Contact Us" },
] as const;
