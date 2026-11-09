import Image from "next/image";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import type { Product } from "@/data/products";
import { productWhatsappMessage, whatsappLink } from "@/lib/whatsapp";
import { WhatsAppIcon } from "./WhatsAppIcon";

export function ProductCard({ product, priority = false }: { product: Product; priority?: boolean }) {
  return (
    <article className="card group flex flex-col overflow-hidden transition hover:-translate-y-0.5 hover:shadow-xl hover:shadow-navy-900/10">
      <Link href={`/products/${product.slug}`} className="relative block aspect-[4/3] overflow-hidden bg-slate-100">
        <Image
          src={product.image}
          alt={product.imageAlt}
          fill
          priority={priority}
          sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"
          className="object-cover transition duration-500 group-hover:scale-[1.03]"
        />
        <span className="absolute top-3 left-3 rounded-full bg-navy-950/85 px-2.5 py-1 text-[11px] font-semibold text-white">
          {product.category}
        </span>
      </Link>
      <div className="flex flex-1 flex-col p-5">
        <h3 className="text-lg font-bold">
          <Link href={`/products/${product.slug}`} className="hover:text-brand-orange">{product.name}</Link>
        </h3>
        <p className="mt-2 flex-1 text-sm leading-relaxed text-slate-600">{product.shortDescription}</p>
        <p className="mt-3 text-xs font-medium text-slate-500">
          <span className="font-semibold text-navy-900">Ratings: </span>
          {product.ratings[0]}
        </p>
        <div className="mt-5 grid grid-cols-2 gap-2">
          <a
            href={whatsappLink(productWhatsappMessage(product.name))}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-whatsapp !px-3 !py-2.5 !text-sm"
          >
            <WhatsAppIcon className="h-4 w-4" /> Enquire
          </a>
          <Link href={`/products/${product.slug}`} className="btn-outline !px-3 !py-2.5 !text-sm">
            Details <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </Link>
        </div>
      </div>
    </article>
  );
}
