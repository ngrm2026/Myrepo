import { siteConfig } from "@/config/site";

/** Build a wa.me link that opens WhatsApp with a prefilled message. */
export function whatsappLink(message: string = siteConfig.whatsappDefaultMessage) {
  return `https://wa.me/${siteConfig.whatsapp}?text=${encodeURIComponent(message)}`;
}

export function productWhatsappMessage(productName: string) {
  return `Hello, I am interested in ${productName}. Please share the available models, ratings, brands and price details. My location in Chennai is: `;
}

export function serviceWhatsappMessage(serviceName: string) {
  return `Hello, I would like to book a service: ${serviceName}. My location in Chennai is: `;
}

export const telLink = `tel:${siteConfig.phone}`;
export const mailLink = `mailto:${siteConfig.email}`;
