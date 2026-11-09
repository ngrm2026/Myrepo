/**
 * Enquiry form validation — shared by the browser form and the server API,
 * so the rules are always the same on both sides.
 */

export type EnquiryInput = {
  name: string;
  mobile: string;
  location: string;
  requirement: string;
  description: string;
};

export type EnquiryErrors = Partial<Record<keyof EnquiryInput, string>>;

export const LIMITS = {
  name: 80,
  mobile: 20,
  location: 100,
  requirement: 120,
  description: 1500,
} as const;

/** Accepts Indian mobile numbers: 10 digits starting 6–9, with optional +91 / 91 / 0 prefix. */
export function normaliseMobile(raw: string): string | null {
  const digits = raw.replace(/[\s\-().]/g, "").replace(/^\+/, "");
  const m = digits.match(/^(?:91|0)?([6-9]\d{9})$/);
  return m ? `+91${m[1]}` : null;
}

function clean(v: unknown, max: number) {
  return typeof v === "string" ? v.replace(/\s+/g, " ").trim().slice(0, max) : "";
}

export function validateEnquiry(raw: Record<string, unknown>): {
  ok: boolean;
  errors: EnquiryErrors;
  value: EnquiryInput;
} {
  const value: EnquiryInput = {
    name: clean(raw.name, LIMITS.name),
    mobile: clean(raw.mobile, LIMITS.mobile),
    location: clean(raw.location, LIMITS.location),
    requirement: clean(raw.requirement, LIMITS.requirement),
    // keep line breaks in the description
    description:
      typeof raw.description === "string" ? raw.description.trim().slice(0, LIMITS.description) : "",
  };

  const errors: EnquiryErrors = {};
  if (value.name.length < 2) errors.name = "Please enter your name.";
  else if (!/^[\p{L}\p{M} .'-]+$/u.test(value.name)) errors.name = "Please use letters only in the name.";

  const mobile = normaliseMobile(value.mobile);
  if (!value.mobile) errors.mobile = "Please enter your mobile number.";
  else if (!mobile) errors.mobile = "Please enter a valid 10-digit Indian mobile number.";
  else value.mobile = mobile;

  if (value.location.length < 2) errors.location = "Please enter your area / location in Chennai.";
  if (!value.requirement) errors.requirement = "Please choose the product or service you need.";
  if (value.description.length < 10)
    errors.description = "Please describe your requirement in a few words (at least 10 characters).";

  return { ok: Object.keys(errors).length === 0, errors, value };
}

export function enquiryToWhatsappText(v: EnquiryInput) {
  return [
    "Hello, I would like to make an enquiry.",
    `Name: ${v.name}`,
    `Mobile: ${v.mobile}`,
    `Location: ${v.location}`,
    `Requirement: ${v.requirement}`,
    `Details: ${v.description}`,
  ].join("\n");
}
