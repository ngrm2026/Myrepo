/**
 * SERVICE AREAS
 * Add or remove areas here. Each area appears on the Service Areas page,
 * in the footer and in the Google structured data ("areaServed").
 */

export type Area = {
  slug: string;
  name: string;
  /** Short local note shown on the Service Areas page. */
  note: string;
};

export const areas: Area[] = [
  { slug: "velachery", name: "Velachery", note: "Phase changeover installation and repair for homes, apartments and shops in Velachery." },
  { slug: "madipakkam", name: "Madipakkam", note: "EB switch sales, phase changeover and wiring services for Madipakkam homes and apartments." },
  { slug: "medavakkam", name: "Medavakkam", note: "Changeover switch installation and electrical panel work for houses and new apartments in Medavakkam." },
  { slug: "pallikaranai", name: "Pallikaranai", note: "Automatic and manual phase changeover solutions for Pallikaranai residences and offices." },
  { slug: "tambaram", name: "Tambaram", note: "EB and generator changeover, distribution boards and repairs across Tambaram." },
  { slug: "perungudi", name: "Perungudi", note: "Electrical panel installation and changeover services for Perungudi offices and homes." },
  { slug: "thoraipakkam", name: "Thoraipakkam", note: "Three-phase changeover and load assessment for apartments and commercial spaces in Thoraipakkam." },
  { slug: "adyar", name: "Adyar", note: "Changeover switch repair, rewiring and preventive maintenance for homes and shops in Adyar." },
  { slug: "guindy", name: "Guindy", note: "Switchgear, MCCB and panel services for commercial and industrial customers in and around Guindy." },
  { slug: "taramani", name: "Taramani", note: "Phase changeover switches and electrical troubleshooting for Taramani homes and offices." },
  { slug: "sholinganallur", name: "Sholinganallur", note: "EB-DG changeover and electrical panel work for apartments and gated communities in Sholinganallur." },
  { slug: "omr", name: "OMR", note: "Changeover, panel and maintenance services for apartments, offices and commercial buildings along OMR." },
];

export const otherAreasNote =
  "We also serve other locations across Chennai, subject to service availability. Call or WhatsApp us with your location to confirm.";
