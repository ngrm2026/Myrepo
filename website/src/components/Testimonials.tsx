import { MessageSquareQuote, Star } from "lucide-react";
import { testimonials } from "@/data/testimonials";
import { siteConfig } from "@/config/site";
import { whatsappLink } from "@/lib/whatsapp";
import { SectionHeading } from "./SectionHeading";

export function Testimonials() {
  return (
    <section className="section bg-slate-50">
      <div className="container-x">
        <SectionHeading center eyebrow="Testimonials" title="What our customers say" />
        {testimonials.length > 0 ? (
          <ul className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {testimonials.map((t) => (
              <li key={t.name + t.location} className="card flex flex-col p-6">
                {t.rating && (
                  <div className="flex gap-0.5" aria-label={`${t.rating} out of 5 stars`}>
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Star
                        key={i}
                        className={`h-4 w-4 ${i < t.rating! ? "fill-brand-yellow text-brand-yellow" : "text-slate-300"}`}
                        aria-hidden="true"
                      />
                    ))}
                  </div>
                )}
                <blockquote className="mt-4 flex-1 text-slate-700">“{t.text}”</blockquote>
                <p className="mt-5 text-sm font-bold text-navy-950">
                  {t.name} <span className="font-normal text-slate-500">· {t.location}</span>
                </p>
              </li>
            ))}
          </ul>
        ) : (
          <div className="card mx-auto mt-10 max-w-2xl p-8 text-center">
            <MessageSquareQuote className="mx-auto h-10 w-10 text-brand-orange" aria-hidden="true" />
            <p className="mt-4 text-slate-600">
              We are collecting feedback from our customers. Worked with us recently? We would love to hear about your
              experience.
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-3">
              {siteConfig.googleReviewsUrl && (
                <a href={siteConfig.googleReviewsUrl} target="_blank" rel="noopener noreferrer" className="btn-primary">
                  Read / Write a Google Review
                </a>
              )}
              <a
                href={whatsappLink("Hello, I would like to share feedback about your service: ")}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-outline"
              >
                Share Feedback on WhatsApp
              </a>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
