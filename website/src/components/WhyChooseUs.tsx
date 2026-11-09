import { BadgeCheck, Building2, CheckCircle2, HardHat, IndianRupee, ShieldCheck, ThumbsUp, Timer } from "lucide-react";
import { highlights, type HighlightIcon } from "@/data/highlights";
import { SectionHeading } from "./SectionHeading";

const icons = {
  hardhat: HardHat,
  badge: BadgeCheck,
  check: CheckCircle2,
  rupee: IndianRupee,
  timer: Timer,
  building: Building2,
  thumbs: ThumbsUp,
  shield: ShieldCheck,
} satisfies Record<HighlightIcon, unknown>;

export function WhyChooseUs() {
  return (
    <section className="section relative overflow-hidden bg-navy-950">
      <div className="bg-grid absolute inset-0" aria-hidden="true" />
      <div className="container-x relative">
        <SectionHeading
          light
          center
          eyebrow="Why Choose Us"
          title="Your trusted electrical partner in Chennai"
          lead="From a single phase changeover switch for your home to complete panels for your building — we focus on safe, neat and dependable work."
        />
        <ul className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {highlights.map((h) => {
            const Icon = icons[h.icon];
            return (
              <li key={h.title} className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur transition hover:border-brand-yellow/40 hover:bg-white/10">
                <Icon className="h-8 w-8 text-brand-yellow" aria-hidden="true" />
                <h3 className="mt-4 text-base font-bold text-white">{h.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-navy-200">{h.text}</p>
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
