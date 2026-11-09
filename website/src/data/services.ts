/**
 * SERVICES
 * Edit the text below to change what appears on the Services page and home page.
 * `icon` must be one of the names listed in src/components/ServiceIcon.tsx.
 */

export type Service = {
  slug: string;
  name: string;
  icon: ServiceIconName;
  summary: string;
  details: string[];
};

export type ServiceIconName =
  | "repeat"
  | "zap"
  | "power"
  | "toggle"
  | "panel"
  | "wrench"
  | "cable"
  | "gauge"
  | "calendar"
  | "building";

export const services: Service[] = [
  {
    slug: "eb-phase-changeover-installation",
    name: "EB Phase Changeover Switch Installation",
    icon: "repeat",
    summary:
      "Supply and installation of manual and automatic phase changeover switches at your EB service board, so a single-phase failure no longer means a full power cut.",
    details: [
      "Inspection of your existing EB meter board and wiring",
      "Recommendation of manual or automatic changeover based on your needs",
      "Neat installation with proper cable sizing, lugs and earthing",
      "Testing on all three phases and a demonstration of how to use it",
    ],
  },
  {
    slug: "single-to-three-phase-changeover",
    name: "Single Phase to Three Phase Changeover Solutions",
    icon: "zap",
    summary:
      "Planning and wiring for premises moving from single-phase to three-phase EB supply, including load balancing and changeover arrangements.",
    details: [
      "Guidance on load balancing across R, Y and B phases",
      "Selection of three-phase changeover switch and distribution board",
      "Rewiring of the main board for the new three-phase connection",
      "Support with documentation you may need for your EB application",
    ],
  },
  {
    slug: "eb-to-generator-changeover-installation",
    name: "EB to Generator Changeover Installation",
    icon: "power",
    summary:
      "Safe changeover between EB supply and your generator (DG set) — manual changeover or fully automatic transfer with AMF panels.",
    details: [
      "Correct changeover rating matched to generator kVA and load",
      "Interlocked switching so EB and generator are never connected together",
      "Single-phase and three-phase installations",
      "Integration with automatic generator start (AMF / ATS) on request",
    ],
  },
  {
    slug: "manual-automatic-changeover-installation",
    name: "Manual and Automatic Changeover Installation",
    icon: "toggle",
    summary:
      "Installation of manual changeover switches and automatic changeover / phase selector units for homes, offices and commercial buildings.",
    details: [
      "Manual changeover for simple, low-maintenance setups",
      "Automatic phase selectors and ATS for hands-free switching",
      "Upgrades from manual to automatic changeover",
      "Clear labelling of all positions and circuits",
    ],
  },
  {
    slug: "electrical-panel-installation",
    name: "Electrical Panel Installation",
    icon: "panel",
    summary:
      "Installation of distribution boards, MCB / MCCB panels, changeover panels, pump control panels and custom LT panels.",
    details: [
      "Distribution board (SPN / TPN) installation and replacement",
      "MCCB, MCB, RCCB and isolator installation",
      "Changeover, pump control and motor starter panels",
      "Cable termination, dressing and circuit labelling",
    ],
  },
  {
    slug: "changeover-switch-repair",
    name: "Existing Changeover Switch Repair",
    icon: "wrench",
    summary:
      "Diagnosis and repair of faulty, burnt, loose or noisy changeover switches — or replacement when repair is not safe.",
    details: [
      "Checking for loose connections, overheating and burnt contacts",
      "Replacement of damaged terminals, lugs and cables",
      "Repair or replacement of manual and automatic changeover units",
      "Testing after repair on all positions",
    ],
  },
  {
    slug: "electrical-wiring-troubleshooting",
    name: "Electrical Wiring and Troubleshooting",
    icon: "cable",
    summary:
      "Fault finding for tripping MCBs, partial power loss, voltage issues and wiring problems, plus new and replacement wiring.",
    details: [
      "Finding the cause of frequent MCB / RCCB tripping",
      "Locating short circuits, earth leakage and loose connections",
      "New wiring, rewiring and additional points",
      "Earthing checks and improvements",
    ],
  },
  {
    slug: "electrical-load-assessment",
    name: "Electrical Load Assessment",
    icon: "gauge",
    summary:
      "Assessment of your connected load and phase balance so you choose the right changeover switch, cable size, breaker rating and EB connection.",
    details: [
      "Survey of connected appliances and equipment",
      "Phase-wise load measurement and balancing advice",
      "Recommendation of switch, MCB / MCCB and cable sizes",
      "Advice before adding AC units, EV chargers or heavy equipment",
    ],
  },
  {
    slug: "preventive-electrical-maintenance",
    name: "Preventive Electrical Maintenance",
    icon: "calendar",
    summary:
      "Scheduled inspection and maintenance of changeover switches, panels and distribution boards to prevent breakdowns.",
    details: [
      "Tightening of terminations and checking for heating",
      "Cleaning of panels and distribution boards",
      "Testing of changeover operation, breakers and indicators",
      "Maintenance plans for apartments, offices and industries",
    ],
  },
  {
    slug: "residential-commercial-electrical-services",
    name: "Residential and Commercial Electrical Services",
    icon: "building",
    summary:
      "General electrical work for homes, apartments, shops, offices, commercial buildings and industries across Chennai.",
    details: [
      "Homes, apartments and residential associations",
      "Shops, showrooms, clinics and offices",
      "Commercial buildings, industries and builder projects",
      "One point of contact for supply and installation",
    ],
  },
];
