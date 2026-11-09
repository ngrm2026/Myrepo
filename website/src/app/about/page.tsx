import Image from "next/image";
import Link from "next/link";
import { CheckCircle2, Eye, Target } from "lucide-react";
import { siteConfig } from "@/config/site";
import { pageMetadata } from "@/lib/seo";
import { PageHero } from "@/components/PageHero";
import { SectionHeading } from "@/components/SectionHeading";
import { WhyChooseUs } from "@/components/WhyChooseUs";
import { CtaBanner } from "@/components/CtaBanner";

export const metadata = pageMetadata({
  title: "About Us – EB Switch & Electrical Changeover Specialists in Chennai",
  description: `About ${siteConfig.name}: EB switch dealers and electrical service providers in Chennai for phase changeover switches, generator changeover, electrical panels, installation and repair.`,
  path: "/about",
});

const values = [
  "Recommend only what your load and supply actually need",
  "Use genuine products from reputed manufacturers",
  "Follow safe isolation, earthing and interlocking practices",
  "Keep installations neat, labelled and easy to maintain",
  "Give clear quotations before work begins",
  "Explain how to operate your changeover before we leave",
];

export default function AboutPage() {
  const { credentials } = siteConfig;
  const verified = [
    credentials.yearsOfExperience ? `${credentials.yearsOfExperience}+ years of experience in electrical work` : "",
    credentials.licence,
    credentials.gstin ? `GST registered business (GSTIN: ${credentials.gstin})` : "",
  ].filter(Boolean);

  return (
    <>
      <PageHero
        eyebrow="About Us"
        title="EB switch & phase changeover specialists in Chennai"
        lead="We help homes, apartments, businesses and industries across Chennai stay powered with the right changeover switches, panels and electrical services."
        crumbs={[{ name: "About Us", path: "/about" }]}
      />

      <section className="section">
        <div className="container-x grid items-center gap-12 lg:grid-cols-2">
          <div className="overflow-hidden rounded-3xl border border-slate-200 shadow-xl">
            <Image
              src="/images/about-technician.svg"
              alt="Electrical technician installing a phase changeover switch on an EB meter board in Chennai"
              width={960}
              height={720}
              className="h-auto w-full"
            />
          </div>
          <div>
            <SectionHeading eyebrow="Who We Are" title={siteConfig.name} />
            <div className="mt-5 space-y-4 text-slate-600">
              <p>
                We are an electrical sales and services business in Chennai focused on EB switches, phase changeover
                switches and electrical panels. We supply the products you need and our technicians install, repair and
                maintain them — so you have one dependable point of contact.
              </p>
              <p>
                Frequent single-phase failures and voltage problems are a daily reality for many homes and businesses.
                A correctly selected and properly installed changeover switch keeps your lights, fans, pumps and
                equipment running. That is the work we specialise in — along with distribution boards, MCB / MCCB
                protection, generator changeover and custom panels.
              </p>
              <p>
                Our customers include homeowners, apartments and residential associations, shops, offices, commercial
                buildings, industries and builders across South Chennai and the OMR corridor.
              </p>
            </div>
            {verified.length > 0 && (
              <ul className="mt-6 space-y-2">
                {verified.map((v) => (
                  <li key={v} className="flex items-start gap-2 font-semibold text-navy-900">
                    <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-green-600" aria-hidden="true" /> {v}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </section>

      <section className="section bg-slate-50">
        <div className="container-x grid gap-6 md:grid-cols-2">
          <div className="card p-8">
            <Target className="h-9 w-9 text-brand-orange" aria-hidden="true" />
            <h2 className="mt-4 text-2xl font-extrabold">Our Mission</h2>
            <p className="mt-3 text-slate-600">
              To give every customer in Chennai a safe, reliable and affordable power changeover solution — with honest
              advice, quality products and careful workmanship.
            </p>
          </div>
          <div className="card p-8">
            <Eye className="h-9 w-9 text-brand-orange" aria-hidden="true" />
            <h2 className="mt-4 text-2xl font-extrabold">Our Approach</h2>
            <ul className="mt-3 space-y-2 text-slate-600">
              {values.map((v) => (
                <li key={v} className="flex items-start gap-2">
                  <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-brand-orange" aria-hidden="true" /> {v}
                </li>
              ))}
            </ul>
          </div>
        </div>
        <div className="container-x mt-10 text-center">
          <Link href="/services" className="btn-primary">See our services</Link>
        </div>
      </section>

      <WhyChooseUs />
      <CtaBanner />
    </>
  );
}
