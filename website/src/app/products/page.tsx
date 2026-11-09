import { products, type Product } from "@/data/products";
import { pageMetadata } from "@/lib/seo";
import { PageHero } from "@/components/PageHero";
import { ProductCard } from "@/components/ProductCard";
import { CtaBanner } from "@/components/CtaBanner";
import { whatsappLink } from "@/lib/whatsapp";
import { WhatsAppIcon } from "@/components/WhatsAppIcon";

export const metadata = pageMetadata({
  title: "Phase Changeover Switches, EB Switches & Electrical Panels – Dealers in Chennai",
  description:
    "EB switch dealers in Chennai: manual, automatic, single phase and three phase changeover switches, EB-generator changeover, distribution boards, MCB, MCCB, contactors, switchgear and custom panels. Enquire on WhatsApp.",
  path: "/products",
});

const categories: Product["category"][] = ["Changeover Switches", "Distribution & Protection", "Switchgear & Panels"];

export default function ProductsPage() {
  return (
    <>
      <PageHero
        eyebrow="Products – Sales"
        title="EB Switch & Phase Changeover Switch Dealers in Chennai"
        lead="Browse our range of changeover switches, distribution boards, circuit breakers, contactors, switchgear and custom panels. Tap “Enquire” to get model, brand and price details on WhatsApp."
        crumbs={[{ name: "Products", path: "/products" }]}
      >
        <nav aria-label="Product categories" className="flex flex-wrap gap-2">
          {categories.map((c) => (
            <a key={c} href={`#${slug(c)}`} className="rounded-full border border-white/20 bg-white/5 px-4 py-2 text-sm font-semibold text-white hover:bg-white/15">
              {c}
            </a>
          ))}
        </nav>
      </PageHero>

      <div className="bg-slate-50">
        {categories.map((c, ci) => (
          <section key={c} id={slug(c)} className="section !pb-4 last:!pb-20" aria-labelledby={`${slug(c)}-title`}>
            <div className="container-x">
              <h2 id={`${slug(c)}-title`} className="text-2xl font-extrabold sm:text-3xl">{c}</h2>
              <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {products
                  .filter((p) => p.category === c)
                  .map((p, i) => (
                    <ProductCard key={p.slug} product={p} priority={ci === 0 && i < 3} />
                  ))}
              </div>
            </div>
          </section>
        ))}
        <div className="container-x pb-16">
          <div className="card flex flex-col items-start justify-between gap-4 p-6 sm:flex-row sm:items-center">
            <p className="text-sm text-slate-600">
              <strong className="text-navy-950">Note:</strong> Product images are illustrative. Ratings shown are
              indicative ranges; exact models, ratings, brands and prices are confirmed on enquiry based on availability
              and your requirement.
            </p>
            <a href={whatsappLink("Hello, please share your current product list and price details.")} target="_blank" rel="noopener noreferrer" className="btn-whatsapp shrink-0">
              <WhatsAppIcon /> Ask for product list
            </a>
          </div>
        </div>
      </div>
      <CtaBanner title="Not sure which changeover switch you need?" text="Send us a photo of your EB meter board and tell us your main appliances — we will recommend the right switch and rating." />
    </>
  );
}

function slug(s: string) {
  return s.toLowerCase().replace(/&/g, "and").replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}
