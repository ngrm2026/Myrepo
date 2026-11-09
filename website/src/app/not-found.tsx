import Link from "next/link";
import { Zap } from "lucide-react";

export default function NotFound() {
  return (
    <section className="section">
      <div className="container-x max-w-xl text-center">
        <Zap className="mx-auto h-12 w-12 text-brand-orange" aria-hidden="true" />
        <h1 className="mt-4 text-3xl font-extrabold">Page not found</h1>
        <p className="mt-3 text-slate-600">
          The page you are looking for has moved or does not exist. Try our products or services, or contact us
          directly.
        </p>
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <Link href="/" className="btn-primary">Go to Home</Link>
          <Link href="/products" className="btn-outline">Products</Link>
          <Link href="/contact" className="btn-outline">Contact Us</Link>
        </div>
      </div>
    </section>
  );
}
