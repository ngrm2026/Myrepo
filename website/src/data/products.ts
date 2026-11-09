/**
 * PRODUCT CATALOGUE
 * ---------------------------------------------------------------
 * How to manage products (no coding knowledge needed):
 *  - To edit a product: change the text between the quotes.
 *  - To add a product: copy one whole { ... } block, paste it at the end of
 *    the list, and give it a new unique `slug` (lowercase, words-joined-by-dashes).
 *  - To remove a product: delete its whole { ... } block.
 *  - To use your own photo: put the image in /public/images/products/
 *    (JPG, PNG, WebP or SVG) and change `image` to "/images/products/your-file.jpg".
 *  - `brands`: list ONLY the brands you actually stock, e.g. ["Brand A", "Brand B"].
 *    When empty, the site says brand options are shared on enquiry.
 *
 * Do not add prices or specifications you cannot confirm. Ratings below are
 * indicative industry ranges; the site tells customers that exact models and
 * ratings are confirmed on enquiry.
 */

export type Product = {
  slug: string;
  name: string;
  category: "Changeover Switches" | "Distribution & Protection" | "Switchgear & Panels";
  shortDescription: string;
  description: string;
  image: string;
  imageAlt: string;
  /** General technical features of this product type. */
  specifications: string[];
  /** Commonly available ratings / capacities (indicative). */
  ratings: string[];
  /** Brands you stock — leave empty to show "brand options on enquiry". */
  brands: string[];
  idealFor: string[];
  /** Related service slug from services.ts (optional). */
  relatedService?: string;
};

export const products: Product[] = [
  {
    slug: "manual-phase-changeover-switch",
    name: "Manual Phase Changeover Switches",
    category: "Changeover Switches",
    shortDescription:
      "Rotary / lever switch that lets you move your home's single-phase load to any healthy EB phase (R, Y or B) by hand.",
    description:
      "When one phase of your three-phase EB supply fails or runs at low voltage, a manual phase changeover switch lets you shift the house load to another available phase in seconds. It is a simple, reliable and low-maintenance solution for homes, shops and small offices that receive three-phase supply but run mostly single-phase loads.",
    image: "/images/products/manual-phase-changeover.svg",
    imageAlt: "Manual phase changeover switch with R Y B rotary selector for EB supply in Chennai homes",
    specifications: [
      "Manual rotary or lever operation with clearly marked R / Y / B positions",
      "Selects one of three incoming EB phases for single-phase loads",
      "Enclosed, wall-mountable design for use near the main EB board",
      "Suitable for 230 V single-phase load circuits fed from a 415 V three-phase supply",
    ],
    ratings: ["Common current ratings for homes: 32 A and 63 A", "Higher ratings available on request"],
    brands: [],
    idealFor: ["Independent houses", "Flats with three-phase supply", "Shops", "Small offices"],
    relatedService: "eb-phase-changeover-installation",
  },
  {
    slug: "automatic-phase-changeover-switch",
    name: "Automatic Phase Changeover Switches",
    category: "Changeover Switches",
    shortDescription:
      "Electronic phase selector that senses phase failure or low voltage and switches your load to a healthy phase automatically.",
    description:
      "An automatic phase changeover switch (also called an automatic phase selector) continuously monitors the voltage on all three incoming phases. If the phase you are using fails or drops outside the safe voltage range, it automatically transfers the load to the best available phase — no need to go to the EB board in the dark. Ideal where power interruptions on one phase are common.",
    image: "/images/products/automatic-phase-changeover.svg",
    imageAlt: "Automatic phase changeover switch with digital voltage display and R Y B phase indicators",
    specifications: [
      "Automatic sensing of phase failure, low voltage and high voltage",
      "Transfers load to a healthy phase without manual intervention",
      "Phase / voltage indication (LED or digital display, depending on model)",
      "Built-in time delay to avoid repeated switching during voltage fluctuations",
      "DIN-rail or wall-mount options depending on model",
    ],
    ratings: ["Commonly available for single-phase loads of 32 A and 63 A", "Model and rating selected after load assessment"],
    brands: [],
    idealFor: ["Homes with frequent phase failures", "Apartments", "Clinics", "Shops and offices"],
    relatedService: "manual-automatic-changeover-installation",
  },
  {
    slug: "single-phase-changeover-switch",
    name: "Single Phase Changeover Switches",
    category: "Changeover Switches",
    shortDescription:
      "Two-way changeover switch for single-phase supplies — switch between EB and inverter, UPS or generator.",
    description:
      "A single-phase changeover switch safely transfers a single-phase load between two sources, such as EB mains and a generator, inverter or UPS. The OFF position between the two sources ensures both supplies are never connected together, protecting your appliances, your backup source and line workers on the EB network.",
    image: "/images/products/single-phase-changeover.svg",
    imageAlt: "Single phase changeover switch with I-0-II lever for EB and generator or inverter supply",
    specifications: [
      "Two-source, double-pole changeover (Source I – OFF – Source II)",
      "Mechanical OFF position prevents back-feeding between sources",
      "Enclosed or modular (DIN-rail) versions",
      "For 230 V single-phase circuits",
    ],
    ratings: ["Indicative range: 32 A to 125 A", "Exact rating chosen to match your load and backup source"],
    brands: [],
    idealFor: ["Homes with inverter or generator", "Shops", "Small offices"],
    relatedService: "eb-to-generator-changeover-installation",
  },
  {
    slug: "three-phase-changeover-switch",
    name: "Three Phase Changeover Switches",
    category: "Changeover Switches",
    shortDescription:
      "Four-pole on-load changeover switch for three-phase installations — commercial, industrial and large residential loads.",
    description:
      "Three-phase (four-pole) changeover switches transfer an entire three-phase installation between two supply sources, typically EB and a diesel generator. On-load changeover switches can be operated with the load connected, making them the standard choice for apartments, commercial buildings and factories that run on three-phase power.",
    image: "/images/products/three-phase-changeover.svg",
    imageAlt: "Three phase four pole on-load changeover switch with handle for EB and DG supply",
    specifications: [
      "Four-pole (3 phases + neutral) switching",
      "On-load operation: I – OFF – II positions",
      "Enclosed (sheet-steel) or open-execution for panel mounting",
      "Designed to IS/IEC 60947-3 (switch-disconnector standard) — confirm per model",
    ],
    ratings: ["Indicative range: 40 A to 3200 A", "Rating selected after load assessment"],
    brands: [],
    idealFor: ["Apartments & associations", "Commercial buildings", "Industries", "Hospitals & schools"],
    relatedService: "single-to-three-phase-changeover",
  },
  {
    slug: "eb-generator-changeover-switch",
    name: "EB and Generator Changeover Switches",
    category: "Changeover Switches",
    shortDescription:
      "Manual or automatic transfer between EB mains and your generator (DG set) — safe, interlocked switching.",
    description:
      "EB and generator changeover switches let you power your premises from the generator when EB supply fails and return to EB when power is restored. Choose a manual changeover for simple setups, or an Automatic Transfer Switch (ATS) / AMF-panel based solution that starts the generator and transfers the load automatically.",
    image: "/images/products/eb-generator-changeover.svg",
    imageAlt: "EB and generator changeover switch panel with EB and DG source indicator lamps",
    specifications: [
      "Manual changeover or Automatic Transfer Switch (ATS) options",
      "Mechanical / electrical interlocking — EB and generator never connected together",
      "Source indication lamps for EB and DG (on panel versions)",
      "Single-phase and three-phase versions",
      "Can be integrated with AMF (Auto Mains Failure) generator control",
    ],
    ratings: ["Indicative range: 32 A to 3200 A", "Matched to generator capacity (kVA) and connected load"],
    brands: [],
    idealFor: ["Homes with generators", "Apartments", "Commercial complexes", "Factories"],
    relatedService: "eb-to-generator-changeover-installation",
  },
  {
    slug: "electrical-distribution-boards",
    name: "Electrical Distribution Boards",
    category: "Distribution & Protection",
    shortDescription:
      "SPN and TPN distribution boards (DBs) to distribute and protect circuits in homes, offices and buildings.",
    description:
      "Distribution boards house your MCBs, RCCBs and isolators and distribute power safely to each circuit. We supply and install single-phase (SPN) and three-phase (TPN) distribution boards in different sizes, including double-door and IP-rated versions for demanding locations.",
    image: "/images/products/distribution-board.svg",
    imageAlt: "Electrical distribution board with row of MCBs and RCCB for homes and offices",
    specifications: [
      "SPN (single-phase) and TPN (three-phase) versions",
      "Single-door and double-door enclosures",
      "Provision for incomer (MCB / isolator / RCCB) and outgoing MCBs",
      "Surface or flush (concealed) mounting",
    ],
    ratings: ["Common sizes: 4-way to 16-way (SPN) and 4-way to 12-way (TPN)", "Larger / custom sizes on request"],
    brands: [],
    idealFor: ["New homes", "Rewiring projects", "Offices", "Shops"],
    relatedService: "electrical-panel-installation",
  },
  {
    slug: "mccb-mcb",
    name: "MCCB and MCB",
    category: "Distribution & Protection",
    shortDescription:
      "Miniature (MCB) and moulded case (MCCB) circuit breakers for overload and short-circuit protection.",
    description:
      "MCBs protect individual circuits in homes and offices, while MCCBs protect higher-current feeders, main incomers and industrial equipment. We help you select the right rating, number of poles and tripping characteristic for your load, and supply RCCBs / RCBOs for earth-leakage protection.",
    image: "/images/products/mcb-mccb.svg",
    imageAlt: "MCB miniature circuit breakers and MCCB moulded case circuit breaker",
    specifications: [
      "MCB: tripping curves B, C and D; SP, SP+N, DP, TP, TPN and 4P versions",
      "MCB standard: IS/IEC 60898-1",
      "MCCB: thermal-magnetic or electronic (microprocessor) release options",
      "MCCB: 3-pole and 4-pole versions; standard IS/IEC 60947-2",
      "RCCB / RCBO available for earth-leakage protection",
    ],
    ratings: [
      "MCB: commonly 0.5 A to 63 A (higher ratings available)",
      "MCCB: frame sizes commonly from 16 A to 1600 A",
    ],
    brands: [],
    idealFor: ["Homes", "Commercial buildings", "Panels & industries"],
    relatedService: "electrical-panel-installation",
  },
  {
    slug: "electrical-contactors",
    name: "Electrical Contactors",
    category: "Switchgear & Panels",
    shortDescription:
      "Power contactors for motor starters, automatic changeover panels, pump control and lighting control.",
    description:
      "Contactors are electrically operated switches used to start and stop motors, control pumps and lighting, and build automatic changeover systems. We supply contactors with suitable coil voltages and auxiliary contacts, and can build them into starter or control panels.",
    image: "/images/products/contactor.svg",
    imageAlt: "Three pole electrical power contactor with auxiliary contact block",
    specifications: [
      "3-pole and 4-pole power contactors",
      "AC coil voltages such as 24 V, 110 V, 230 V and 415 V (model dependent)",
      "Add-on auxiliary contact blocks and overload relays",
      "Standard: IS/IEC 60947-4-1",
    ],
    ratings: ["Commonly available from 9 A upwards (AC-3 duty)", "Selected based on motor kW / load current"],
    brands: [],
    idealFor: ["Water pump control", "Motor starters", "Automatic changeover panels", "Industries"],
    relatedService: "electrical-panel-installation",
  },
  {
    slug: "industrial-electrical-switchgear",
    name: "Industrial Electrical Switchgear",
    category: "Switchgear & Panels",
    shortDescription:
      "Switch-disconnectors, fuse units, ACBs and protection devices for industrial and commercial installations.",
    description:
      "For factories, commercial complexes and large buildings, we supply industrial switchgear including switch-disconnector fuse units, air circuit breakers (ACBs), MCCBs, isolators and protection relays — selected to match your load, fault level and existing installation.",
    image: "/images/products/industrial-switchgear.svg",
    imageAlt: "Industrial electrical switchgear cubicle with air circuit breaker and meters",
    specifications: [
      "Switch-disconnectors and switch-disconnector-fuse (SDF) units",
      "Air Circuit Breakers (ACB) for main incomers",
      "Isolators, fuse holders and HRC fuses",
      "Meters, protection relays and indication devices",
    ],
    ratings: ["Ratings depend on your installation — shared after site assessment"],
    brands: [],
    idealFor: ["Factories", "Commercial complexes", "Builders & contractors"],
    relatedService: "electrical-load-assessment",
  },
  {
    slug: "custom-electrical-panels",
    name: "Custom Electrical Panels",
    category: "Switchgear & Panels",
    shortDescription:
      "Panels built to your requirement — changeover, main LT, distribution, pump / motor control and AMF panels.",
    description:
      "We design and build custom electrical panels to suit your building and load: EB-DG changeover panels, main LT panels, sub-distribution panels, pump and motor control panels, and APFC or metering panels. Each panel is planned around your load, space and future expansion needs.",
    image: "/images/products/custom-panel.svg",
    imageAlt: "Custom electrical control panel with meters, indicator lamps and changeover handle",
    specifications: [
      "EB-DG manual / automatic changeover panels",
      "Main LT and sub-distribution panels",
      "Pump, motor starter and control panels",
      "Powder-coated sheet-steel enclosures; indoor / outdoor versions",
      "Busbar, meters, indication lamps and protection as per design",
    ],
    ratings: ["Built to your load requirement after site visit"],
    brands: [],
    idealFor: ["Apartments & associations", "Commercial buildings", "Industries", "Builders"],
    relatedService: "electrical-panel-installation",
  },
];

export function getProduct(slug: string) {
  return products.find((p) => p.slug === slug);
}
