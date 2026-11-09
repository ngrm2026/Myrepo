import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowRight, CheckCircle2, Phone, Tag, Users } from "lucide-react";
import { getProduct, products } from "@/data/products";
import { services } from "@/data/services";
import { absoluteUrl, pageMetadata } from "@/lib/seo";
import { productWhatsappMessage, telLink, whatsappLink } from "@/lib/whatsapp";
import { PageHero } from "@/components/PageHero";
import { ProductCard } from "@/components/ProductCard";
import { WhatsAppIcon } from "@/components/WhatsAppIcon";
import { JsonLd } from "@/components/JsonLd";
import { CtaBanner } from "@/components/CtaBanner";

export function generateStaticParams() {
  return products.map((p) => ({ slug: p.slug }));
}

export async function generateMetadata({ params }: PageProps<"/products/[slug]">) {
  const { slug } = await params;
  const p = getProduct(slug);
  if (!p) return {};
  return pageMetadata({
    title: `${p.name} in Chennai – Sales & Installation`,
    description: `${p.shortDescription} Buy ${p.name} in Chennai with installation support. Enquire on WhatsApp.`,
    path: `/products/${p.slug}`,
    image: p.image.endsWith(".svg") ? undefined : p.image,
  });
}

export default async function ProductPage({ params }: PageProps<"/products/[slug]">) {
  const { slug } = await params;
  const product = getProduct(slug);
  if (!product) notFound();

  const related = services.find((s) => s.slug === product.relatedService);
  const others = products.filter((p) => p.slug !== product.slug && p.category === product.category).slice(0, 3);

  return (
    <>
      <PageHero
        eyebrow={product.category}
        title={`${product.name} in Chennai`}
        crumbs={[
          { name: "Products", path: "/products" },
          { name: product.name, path: `/products/${product.slug}` },
        ]}
      />

      <section className="section">
        <div className="container-x grid gap-10 lg:grid-cols-2 lg:gap-14">
          <div>
            <div className="overflow-hidden rounded-3xl border border-slate-200 bg-slate-100 shadow-lg lg:sticky lg:top-28">
              <Image src={product.image} alt={product.imageAlt} width={800} height={600} priority className="h-auto w-full" />
            </div>
          </div>

          <div>
            <p className="text-lg leading-relaxed text-slate-700">{product.description}</p>

            <div className="mt-6 flex flex-wrap gap-3">
              <a href={whatsappLink(productWhatsappMessage(product.name))} target="_blank" rel="noopener noreferrer" className="btn-whatsapp">
                <WhatsAppIcon /> Enquire on WhatsApp
              </a>
              <a href={telLink} className="btn-primary">
                <Phone className="h-5 w-5" aria-hidden="true" /> Call Now
              </a>
              <Link href={`/contact?product=${product.slug}#enquiry`} className="btn-outline">
                Send Enquiry Form
              </Link>
            </div>

            <h2 className="mt-10 text-xl font-extrabold">Technical specifications</h2>
            <ul className="mt-4 space-y-2.5">
              {product.specifications.map((s) => (
                <li key={s} className="flex items-start gap-2.5 text-slate-700">
                  <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-brand-orange" aria-hidden="true" /> {s}
                </li>
              ))}
            </ul>

            <div className="mt-8 grid gap-4 sm:grid-cols-2">
              <div className="card p-5">
                <h2 className="flex items-center gap-2 text-base font-bold">
                  <Tag className="h-5 w-5 text-brand-orange" aria-hidden="true" /> Available ratings &amp; capacities
                </h2>
                <ul className="mt-3 space-y-1.5 text-sm text-slate-600">
                  {product.ratings.map((r) => (
                    <li key={r}>• {r}</li>
                  ))}
                </ul>
              </div>
              <div className="card p-5">
                <h2 className="flex items-center gap-2 text-base font-bold">
                  <Users className="h-5 w-5 text-brand-orange" aria-hidden="true" /> Ideal for
                </h2>
                <ul className="mt-3 space-y-1.5 text-sm text-slate-600">
                  {product.idealFor.map((r) => (
                    <li key={r}>• {r}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="card mt-4 p-5">
              <h2 className="text-base font-bold">Brand information</h2>
              {product.brands.length > 0 ? (
                <ul className="mt-3 flex flex-wrap gap-2">
                  {product.brands.map((b) => (
                    <li key={b} className="rounded-full bg-navy-50 px-3 py-1 text-sm font-semibold text-navy-800">{b}</li>
                  ))}
                </ul>
              ) : (
                <p className="mt-2 text-sm text-slate-600">
                  Available in reputed brands. Current brand options and stock are shared on enquiry.
                </p>
              )}
            </div>

            <p className="mt-6 rounded-xl bg-amber-50 p-4 text-sm text-amber-900">
              Ratings are indicative. The exact model, rating and price are confirmed after understanding your supply and
              load. Product image is illustrative.
            </p>

            {related && (
              <Link href={`/services#${related.slug}`} className="mt-6 inline-flex items-center gap-1 font-semibold text-navy-700 hover:text-brand-orange">
                Need installation? See: {related.name} <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Link>
            )}
          </div>
        </div>
      </section>

      {others.length > 0 && (
        <section className="section bg-slate-50">
          <div className="container-x">
            <h2 className="text-2xl font-extrabold sm:text-3xl">Related products</h2>
            <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {others.map((p) => (
                <ProductCard key={p.slug} product={p} />
              ))}
            </div>
          </div>
        </section>
      )}

      <CtaBanner />

      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "Product",
          name: product.name,
          description: product.description,
          image: absoluteUrl(product.image),
          category: product.category,
          url: absoluteUrl(`/products/${product.slug}`),
          ...(product.brands.length ? { brand: product.brands.map((b) => ({ "@type": "Brand", name: b })) } : {}),
        }}
      />
    </>
  );
}
