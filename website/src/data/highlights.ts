/** "Why Choose Us" points — qualitative only. Do not add numbers you cannot verify. */

export type Highlight = { title: string; text: string; icon: HighlightIcon };
export type HighlightIcon = "hardhat" | "badge" | "check" | "rupee" | "timer" | "building" | "thumbs" | "shield";

export const highlights: Highlight[] = [
  { icon: "hardhat", title: "Experienced Electrical Technicians", text: "Trained technicians who work on changeover switches, panels and wiring every day." },
  { icon: "badge", title: "Quality Electrical Products", text: "Genuine products from reputed manufacturers, selected for your load and usage." },
  { icon: "check", title: "Reliable Installation", text: "Correct ratings, proper terminations, neat cable dressing and full testing before handover." },
  { icon: "rupee", title: "Affordable Pricing", text: "Clear quotations before work starts, with options to suit your budget." },
  { icon: "timer", title: "Quick Response in Chennai", text: "Fast replies on call and WhatsApp, with prompt site visits across our service areas." },
  { icon: "building", title: "Residential & Commercial Support", text: "Homes, apartments, shops, offices, commercial buildings, industries and builders." },
  { icon: "thumbs", title: "Customer Satisfaction", text: "We explain the problem, the fix and how to use your changeover before we leave." },
  { icon: "shield", title: "Safety-Focused Workmanship", text: "Safe isolation, proper earthing and interlocked switching on every job." },
];
