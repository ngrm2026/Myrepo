# EB Switch & Phase Changeover – Sales and Services, Chennai

A complete, mobile-first business website built to generate **phone calls, WhatsApp enquiries,
product sales leads and service bookings** across Chennai.

Built with **Next.js 16 (App Router) + React 19 + Tailwind CSS 4**. Every page is pre-rendered as
static HTML, so it loads fast and is easy for Google to read.

## Pages

| Page | URL | Highlights |
| --- | --- | --- |
| Home | `/` | Hero with Call / WhatsApp / Explore Products / Book a Service, products, services, how it works, why choose us, service areas, testimonials, FAQ |
| About Us | `/about` | Business story, mission, approach; verified credentials appear only when filled in |
| Products | `/products` | 10 products grouped by category, each with WhatsApp enquiry button |
| Product detail | `/products/[slug]` | Image, description, technical specs, ratings, brand info, WhatsApp / call / form enquiry |
| Services | `/services` | 10 services with descriptions and "Book on WhatsApp" / "Request a visit" |
| Service Areas | `/service-areas` | 12 Chennai areas (SEO), map, area-specific WhatsApp enquiries |
| Gallery | `/gallery` | Project gallery (replace with your own photos) |
| Contact Us | `/contact` | Phone, WhatsApp, email, address, Google Map, hours, validated enquiry form, FAQ |

**On every page:** floating WhatsApp button (pre-filled message), click-to-call, sticky
Call / WhatsApp / Book bar on phones, and local-business structured data for Google.

## Before going live — checklist

1. **Business details** – edit [`src/config/site.ts`](src/config/site.ts): name, phone, WhatsApp
   number, email, address, map search text, working hours. Values marked `REPLACE` are placeholders.
2. **Credentials** – in the same file, fill `credentials` (years of experience, licence, GSTIN)
   **only with verified details**. Empty values stay hidden.
3. **Products** – review [`src/data/products.ts`](src/data/products.ts). Add the brands you
   actually stock to each product's `brands` list. Ratings are written as indicative ranges;
   adjust them to what you sell.
4. **Photos** – replace the illustrations with real photos (see below).
5. **Testimonials** – add genuine customer reviews in
   [`src/data/testimonials.ts`](src/data/testimonials.ts) and set `googleReviewsUrl` in the config.
6. **Enquiry delivery** – set up email or a Google Sheet: see [`docs/ENQUIRIES.md`](docs/ENQUIRIES.md).
7. **Environment variables** – copy [`.env.example`](.env.example); set `NEXT_PUBLIC_SITE_URL`
   to your domain, and optionally `NEXT_PUBLIC_GA_MEASUREMENT_ID` for Google Analytics.
8. After launch, submit `https://your-domain/sitemap.xml` in Google Search Console and link the
   website from your Google Business Profile.

## Managing content (no coding needed)

All content lives in plain data files — edit the text between quotes and redeploy.
On GitHub you can edit these files directly in the browser; Vercel redeploys automatically.

| What | File |
| --- | --- |
| Phone, WhatsApp, address, hours, map, social links | `src/config/site.ts` |
| Products (add / edit / remove) | `src/data/products.ts` |
| Services | `src/data/services.ts` |
| Service areas | `src/data/areas.ts` |
| FAQs | `src/data/faqs.ts` |
| Testimonials | `src/data/testimonials.ts` |
| Gallery | `src/data/gallery.ts` |
| "Why Choose Us" points | `src/data/highlights.ts` |

**Adding a product:** copy an existing `{ ... }` block in `products.ts`, give it a new unique
`slug`, and change the text. A product page, sitemap entry and enquiry-form option are
created automatically.

### Images

The included images are original vector illustrations (`public/images/`), labelled on the
site as illustrative. For best results replace them with **your own photos**:

1. Save the photo (JPG/WebP, ~1200px wide, landscape 4:3) in `public/images/products/` or
   `public/images/gallery/`.
2. Update the `image` path (and `imageAlt` / `alt` text) in the data file.

JPG/PNG/WebP photos are automatically resized and optimised. To regenerate the illustrations:
`python3 scripts/generate-illustrations.py`.

## Enquiries, WhatsApp and analytics

- **WhatsApp:** all buttons open `wa.me` with a pre-filled message. Product and service buttons
  include the product/service name. The floating button uses the message in `site.ts`.
- **Enquiry form:** validated in the browser and again on the server; spam protection with a
  hidden honeypot field, minimum fill time, rate limiting and same-site check. Delivered by email
  (Resend) and/or webhook (Google Sheets, Zapier…). If delivery is not set up or fails, the customer
  is offered a one-tap WhatsApp fallback with their details pre-filled.
- **Analytics:** set `NEXT_PUBLIC_GA_MEASUREMENT_ID` to enable Google Analytics 4. Phone clicks
  (`click_to_call`), WhatsApp clicks (`whatsapp_click`) and form submissions (`generate_lead`) are
  tracked as events automatically.

## SEO

- Keyword-focused titles, meta descriptions and headings on every page (EB Switch Sales Chennai,
  Phase Changeover Switch Chennai, Automatic Phase Changeover Switch Chennai, Electrical Panel
  Installation Chennai, Electrical Services Near Me Chennai, …)
- Structured data: `Electrician` local business (address, hours, areas served, services and
  products), `Product`, `Service`, `FAQPage` and `BreadcrumbList`
- Canonical URLs, Open Graph / social image, `sitemap.xml`, `robots.txt`, web manifest
- Descriptive image alt text, semantic HTML, fast static pages

## Development

Requires Node.js 20.9+.

```bash
npm install
npm run dev      # http://localhost:3000
npm run build    # production build
npm run lint
```

## Deploying to Vercel

1. Push this repository to GitHub and import it in Vercel.
2. Set **Root Directory** to `website`.
3. Add the environment variables from `.env.example`.
4. Deploy, then add your custom domain in Vercel → Project → Domains.

Any Node.js host that supports Next.js (Netlify, Render, a VPS with `npm run build && npm start`)
also works.
