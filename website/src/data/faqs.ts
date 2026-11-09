/**
 * FREQUENTLY ASKED QUESTIONS
 * Shown on the home page and contact page, and sent to Google as FAQ data.
 * Keep answers accurate for your business.
 */

export type Faq = { q: string; a: string };

export const faqs: Faq[] = [
  {
    q: "What is a phase changeover switch and why do I need one?",
    a: "If your premises has a three-phase EB connection, a phase changeover switch lets you move your load to another phase when one phase fails or has low voltage. Instead of sitting in the dark until EB restores that phase, you can switch to a healthy phase in seconds (manual) or have it done for you (automatic).",
  },
  {
    q: "Should I choose a manual or automatic phase changeover switch?",
    a: "A manual switch is simple, economical and very reliable — you turn the knob to select a phase. An automatic phase changeover senses failure or low voltage and switches by itself, which is convenient if failures are frequent, if elders live at home, or if you are often away. We can recommend the right option after understanding your load and usage.",
  },
  {
    q: "Can you install a changeover between EB and my generator?",
    a: "Yes. We install manual changeover switches and automatic transfer arrangements between EB supply and generators, for both single-phase and three-phase systems. The switch is sized to your generator capacity and connected load, and interlocked so the two sources are never connected together.",
  },
  {
    q: "Do you repair existing changeover switches?",
    a: "Yes. We inspect existing changeover switches for loose connections, overheating, burnt contacts and wiring faults, and repair them where it is safe. If the switch is damaged beyond safe repair, we will explain why and suggest a suitable replacement.",
  },
  {
    q: "Which areas in Chennai do you serve?",
    a: "We regularly serve Velachery, Madipakkam, Medavakkam, Pallikaranai, Tambaram, Perungudi, Thoraipakkam, Adyar, Guindy, Taramani, Sholinganallur and OMR. Other Chennai locations are covered subject to availability — share your location on call or WhatsApp to confirm.",
  },
  {
    q: "How much does a phase changeover switch cost?",
    a: "The cost depends on the type (manual or automatic), rating, brand and installation work needed at your site. Send us a photo of your EB board on WhatsApp or book a visit, and we will share a clear quotation before starting any work.",
  },
  {
    q: "Do you supply products only, or installation too?",
    a: "Both. You can buy changeover switches, distribution boards, MCBs, MCCBs, contactors and panels from us, or choose supply-and-installation by our technicians.",
  },
  {
    q: "Do you work for apartments, commercial buildings and industries?",
    a: "Yes. Along with homes, we handle apartments and residential associations, shops, offices, commercial buildings, industries and builder projects — including three-phase changeover systems, custom panels and preventive maintenance.",
  },
];
