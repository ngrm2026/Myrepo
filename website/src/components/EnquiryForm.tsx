"use client";

import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { CheckCircle2, Loader2, Send, TriangleAlert } from "lucide-react";
import { products } from "@/data/products";
import { services } from "@/data/services";
import { areas } from "@/data/areas";
import {
  LIMITS,
  enquiryToWhatsappText,
  validateEnquiry,
  type EnquiryErrors,
  type EnquiryInput,
} from "@/lib/enquiry";
import { whatsappLink } from "@/lib/whatsapp";
import { trackEvent } from "@/lib/analytics";
import { WhatsAppIcon } from "./WhatsAppIcon";

type Status =
  | { kind: "idle" }
  | { kind: "sending" }
  | { kind: "sent"; value: EnquiryInput }
  | { kind: "failed"; value: EnquiryInput; message: string };

const OTHER = "Other / Not sure — need advice";

/** Reads ?product=slug or ?service=slug so "Enquire" links can preselect the requirement. */
export function EnquiryFormWithParams() {
  const params = useSearchParams();
  const product = products.find((p) => p.slug === params.get("product"));
  const service = services.find((s) => s.slug === params.get("service"));
  const preset = product?.name ?? service?.name ?? "";
  return <EnquiryForm key={preset} defaultRequirement={preset} />;
}

export function EnquiryForm({ defaultRequirement = "" }: { defaultRequirement?: string }) {
  const [errors, setErrors] = useState<EnquiryErrors>({});
  const [status, setStatus] = useState<Status>({ kind: "idle" });
  const startedAt = useRef(0);
  const formRef = useRef<HTMLFormElement>(null);

  // Record when the form was shown (used by the server's spam check)
  useEffect(() => {
    startedAt.current = Date.now();
  }, []);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const raw = Object.fromEntries(fd.entries());
    const { ok, errors, value } = validateEnquiry(raw);
    setErrors(errors);
    if (!ok) {
      const first = Object.keys(errors)[0];
      formRef.current?.querySelector<HTMLElement>(`[name="${first}"]`)?.focus();
      return;
    }

    setStatus({ kind: "sending" });
    try {
      const res = await fetch("/api/enquiry", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...raw, startedAt: startedAt.current }),
      });
      const data = (await res.json().catch(() => ({}))) as { ok?: boolean; errors?: EnquiryErrors; message?: string };
      if (res.ok && data.ok) {
        setStatus({ kind: "sent", value });
        trackEvent("generate_lead", { method: "enquiry_form", requirement: value.requirement });
        formRef.current?.reset();
        return;
      }
      if (data.errors) setErrors(data.errors);
      setStatus({
        kind: "failed",
        value,
        message: data.message ?? "We could not send your enquiry online right now.",
      });
    } catch {
      setStatus({ kind: "failed", value, message: "Network error — we could not send your enquiry online." });
    }
  }

  if (status.kind === "sent") {
    return (
      <div role="status" className="rounded-2xl border border-green-200 bg-green-50 p-6 sm:p-8">
        <CheckCircle2 className="h-10 w-10 text-green-600" aria-hidden="true" />
        <h3 className="mt-4 text-xl font-bold">Thank you, {status.value.name}! Your enquiry has been received.</h3>
        <p className="mt-2 text-slate-600">
          Our team will call you back on {status.value.mobile} shortly. For a faster response, you can also send these
          details to us on WhatsApp.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <a
            href={whatsappLink(enquiryToWhatsappText(status.value))}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-whatsapp"
          >
            <WhatsAppIcon /> Send on WhatsApp too
          </a>
          <button type="button" className="btn-outline" onClick={() => setStatus({ kind: "idle" })}>
            Send another enquiry
          </button>
        </div>
      </div>
    );
  }

  const err = (k: keyof EnquiryInput) =>
    errors[k] ? (
      <p id={`${k}-error`} className="mt-1.5 text-sm font-medium text-red-600">
        {errors[k]}
      </p>
    ) : null;
  const aria = (k: keyof EnquiryInput) => ({
    "aria-invalid": errors[k] ? true : undefined,
    "aria-describedby": errors[k] ? `${k}-error` : undefined,
  });

  return (
    <form ref={formRef} onSubmit={onSubmit} noValidate className="grid gap-5 sm:grid-cols-2">
      <div>
        <label htmlFor="name" className="field-label">Customer Name *</label>
        <input id="name" name="name" type="text" autoComplete="name" maxLength={LIMITS.name} required className="field" placeholder="Your full name" {...aria("name")} />
        {err("name")}
      </div>
      <div>
        <label htmlFor="mobile" className="field-label">Mobile Number *</label>
        <input id="mobile" name="mobile" type="tel" inputMode="tel" autoComplete="tel" maxLength={LIMITS.mobile} required className="field" placeholder="10-digit mobile number" {...aria("mobile")} />
        {err("mobile")}
      </div>
      <div>
        <label htmlFor="location" className="field-label">Location *</label>
        <input id="location" name="location" type="text" list="area-list" autoComplete="address-level2" maxLength={LIMITS.location} required className="field" placeholder="e.g. Velachery, Chennai" {...aria("location")} />
        <datalist id="area-list">
          {areas.map((a) => (
            <option key={a.slug} value={`${a.name}, Chennai`} />
          ))}
        </datalist>
        {err("location")}
      </div>
      <div>
        <label htmlFor="requirement" className="field-label">Required Product / Service *</label>
        <select id="requirement" name="requirement" required defaultValue={defaultRequirement} className="field" {...aria("requirement")}>
          <option value="" disabled>Select product or service</option>
          <optgroup label="Products">
            {products.map((p) => (
              <option key={p.slug} value={p.name}>{p.name}</option>
            ))}
          </optgroup>
          <optgroup label="Services">
            {services.map((s) => (
              <option key={s.slug} value={s.name}>{s.name}</option>
            ))}
          </optgroup>
          <option value={OTHER}>{OTHER}</option>
        </select>
        {err("requirement")}
      </div>
      <div className="sm:col-span-2">
        <label htmlFor="description" className="field-label">Description of Requirement *</label>
        <textarea id="description" name="description" rows={5} maxLength={LIMITS.description} required className="field resize-y" placeholder="Tell us what you need — e.g. single-phase or three-phase supply, current problem, generator capacity, number of flats, preferred visit time." {...aria("description")} />
        {err("description")}
      </div>

      {/* Spam trap: hidden from people, often filled by bots */}
      <div aria-hidden="true" className="absolute -left-[9999px] h-px w-px overflow-hidden">
        <label htmlFor="website">Leave this field empty</label>
        <input id="website" name="website" type="text" tabIndex={-1} autoComplete="off" />
      </div>

      {status.kind === "failed" && (
        <div role="alert" className="flex gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900 sm:col-span-2">
          <TriangleAlert className="h-5 w-5 shrink-0" aria-hidden="true" />
          <div>
            <p className="font-semibold">{status.message}</p>
            <p className="mt-1">Please send the same details on WhatsApp or call us — we will respond quickly.</p>
            <a
              href={whatsappLink(enquiryToWhatsappText(status.value))}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-whatsapp mt-3 !py-2 !text-sm"
            >
              <WhatsAppIcon className="h-4 w-4" /> Send enquiry on WhatsApp
            </a>
          </div>
        </div>
      )}

      <div className="flex flex-col gap-3 sm:col-span-2 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-xs text-slate-500">
          We use your details only to respond to this enquiry. No spam.
        </p>
        <button type="submit" disabled={status.kind === "sending"} className="btn-primary sm:min-w-48">
          {status.kind === "sending" ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" /> Sending…
            </>
          ) : (
            <>
              <Send className="h-5 w-5" aria-hidden="true" /> Send Enquiry
            </>
          )}
        </button>
      </div>
    </form>
  );
}
