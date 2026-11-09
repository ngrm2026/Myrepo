import Image from "next/image";
import { gallery } from "@/data/gallery";
import { pageMetadata } from "@/lib/seo";
import { whatsappLink } from "@/lib/whatsapp";
import { PageHero } from "@/components/PageHero";
import { WhatsAppIcon } from "@/components/WhatsAppIcon";
import { CtaBanner } from "@/components/CtaBanner";

export const metadata = pageMetadata({
  title: "Gallery – Phase Changeover & Electrical Panel Installations in Chennai",
  description:
    "See phase changeover switch installations, EB to generator changeover panels, distribution boards and electrical panel work in Chennai.",
  path: "/gallery",
});

export default function GalleryPage() {
  return (
    <>
      <PageHero
        eyebrow="Gallery"
        title="Our Electrical Installation Work"
        lead="Phase changeover switches, generator changeover panels, distribution boards and electrical panels installed for customers in Chennai."
        crumbs={[{ name: "Gallery", path: "/gallery" }]}
      />
      <section className="section">
        <div className="container-x">
          <ul className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {gallery.map((g) => (
              <li key={g.image}>
                <figure className="card group overflow-hidden">
                  <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
                    <Image
                      src={g.image}
                      alt={g.alt}
                      fill
                      sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"
                      className="object-cover transition duration-500 group-hover:scale-[1.03]"
                    />
                    <span className="absolute top-3 left-3 rounded-full bg-brand-orange px-2.5 py-1 text-[11px] font-bold text-white">
                      {g.category}
                    </span>
                  </div>
                  <figcaption className="p-4 font-semibold text-navy-950">{g.title}</figcaption>
                </figure>
              </li>
            ))}
          </ul>
          <div className="mt-10 flex flex-col items-center gap-4 text-center">
            <p className="max-w-2xl text-sm text-slate-500">
              Want to see more examples of our work, or similar installations for your type of building? Ask us on
              WhatsApp.
            </p>
            <a href={whatsappLink("Hello, can you share photos of similar changeover / panel installations you have done?")} target="_blank" rel="noopener noreferrer" className="btn-whatsapp">
              <WhatsAppIcon /> Request more photos
            </a>
          </div>
        </div>
      </section>
      <CtaBanner />
    </>
  );
}
