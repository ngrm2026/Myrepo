import { NextResponse, type NextRequest } from "next/server";
import { validateEnquiry, type EnquiryInput } from "@/lib/enquiry";
import { siteConfig } from "@/config/site";

/**
 * Enquiry API — receives the contact form and delivers it to the business.
 *
 * Delivery channels (configure one or both with environment variables):
 *  - Email via Resend:   RESEND_API_KEY, ENQUIRY_TO_EMAIL, ENQUIRY_FROM_EMAIL
 *  - Webhook (e.g. Google Sheets via Apps Script, Zapier, Make): ENQUIRY_WEBHOOK_URL
 * See docs/ENQUIRIES.md for setup steps.
 */

const MIN_FILL_MS = 2500; // humans take longer than this to fill the form
const RATE_LIMIT = { windowMs: 10 * 60 * 1000, max: 5 };
const hits = new Map<string, number[]>(); // best-effort, per server instance

function rateLimited(ip: string) {
  const now = Date.now();
  const recent = (hits.get(ip) ?? []).filter((t) => now - t < RATE_LIMIT.windowMs);
  recent.push(now);
  hits.set(ip, recent);
  if (hits.size > 5000) hits.clear();
  return recent.length > RATE_LIMIT.max;
}

const escapeHtml = (s: string) =>
  s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);

async function sendEmail(v: EnquiryInput, meta: { page: string; at: string }) {
  const key = process.env.RESEND_API_KEY;
  const to = process.env.ENQUIRY_TO_EMAIL;
  if (!key || !to) return null;
  const from = process.env.ENQUIRY_FROM_EMAIL ?? "Website Enquiry <onboarding@resend.dev>";
  const rows = [
    ["Name", v.name],
    ["Mobile", v.mobile],
    ["Location", v.location],
    ["Requirement", v.requirement],
    ["Description", v.description],
    ["Received", meta.at],
  ]
    .map(
      ([k, val]) =>
        `<tr><td style="padding:6px 12px;font-weight:600;vertical-align:top">${k}</td><td style="padding:6px 12px;white-space:pre-wrap">${escapeHtml(val)}</td></tr>`,
    )
    .join("");
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      from,
      to: to.split(",").map((s) => s.trim()),
      subject: `New enquiry: ${v.requirement} – ${v.name} (${v.location})`,
      html: `<h2>New website enquiry – ${escapeHtml(siteConfig.name)}</h2><table>${rows}</table><p><a href="tel:${v.mobile}">Call ${v.mobile}</a> · <a href="https://wa.me/${v.mobile.replace("+", "")}">WhatsApp</a></p>`,
      text: `New enquiry\nName: ${v.name}\nMobile: ${v.mobile}\nLocation: ${v.location}\nRequirement: ${v.requirement}\nDescription: ${v.description}\nReceived: ${meta.at}`,
    }),
    signal: AbortSignal.timeout(8000),
  });
  return res.ok;
}

async function sendWebhook(v: EnquiryInput, meta: { page: string; at: string }) {
  const url = process.env.ENQUIRY_WEBHOOK_URL;
  if (!url) return null;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...v, receivedAt: meta.at, page: meta.page, source: "website" }),
    signal: AbortSignal.timeout(8000),
    redirect: "follow",
  });
  return res.ok;
}

export async function POST(req: NextRequest) {
  // Only accept submissions from this website
  const origin = req.headers.get("origin");
  const host = req.headers.get("host");
  if (origin && host && new URL(origin).host !== host) {
    return NextResponse.json({ ok: false, message: "Invalid request origin." }, { status: 403 });
  }

  const ip = (req.headers.get("x-forwarded-for") ?? "").split(",")[0].trim() || "unknown";
  if (rateLimited(ip)) {
    return NextResponse.json(
      { ok: false, message: "Too many enquiries from this connection. Please call or WhatsApp us instead." },
      { status: 429 },
    );
  }

  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ ok: false, message: "Invalid request." }, { status: 400 });
  }

  // Bot checks: hidden field filled in, or form submitted impossibly fast.
  // Respond "ok" so bots don't learn they were blocked.
  const startedAt = Number(body.startedAt);
  if (body.website || (Number.isFinite(startedAt) && Date.now() - startedAt < MIN_FILL_MS)) {
    return NextResponse.json({ ok: true });
  }

  const { ok, errors, value } = validateEnquiry(body);
  if (!ok) {
    return NextResponse.json({ ok: false, errors, message: "Please correct the highlighted fields." }, { status: 422 });
  }

  const meta = {
    page: req.headers.get("referer") ?? "",
    at: new Date().toLocaleString("en-IN", { timeZone: "Asia/Kolkata" }),
  };

  const results = await Promise.allSettled([sendEmail(value, meta), sendWebhook(value, meta)]);
  const configured = results.some((r) => r.status === "rejected" || r.value !== null);
  const delivered = results.some((r) => r.status === "fulfilled" && r.value === true);

  if (!configured) {
    console.warn("[enquiry] No delivery channel configured (set RESEND_API_KEY + ENQUIRY_TO_EMAIL or ENQUIRY_WEBHOOK_URL).");
    return NextResponse.json(
      { ok: false, message: "Online enquiries are not set up yet." },
      { status: 503 },
    );
  }
  if (!delivered) {
    console.error("[enquiry] Delivery failed", results);
    return NextResponse.json(
      { ok: false, message: "We could not send your enquiry online right now." },
      { status: 502 },
    );
  }
  return NextResponse.json({ ok: true });
}
