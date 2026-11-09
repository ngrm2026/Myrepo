/**
 * CUSTOMER TESTIMONIALS
 * ---------------------------------------------------------------
 * Add ONLY genuine reviews from real customers, with their permission.
 * While this list is empty, the website shows an invitation to read/leave
 * Google reviews instead of testimonials.
 *
 * Example:
 *   { name: "R. Kumar", location: "Velachery", text: "Installed an automatic phase changeover ...", rating: 5 },
 */

export type Testimonial = {
  name: string;
  location: string;
  text: string;
  /** 1 to 5 */
  rating?: number;
};

export const testimonials: Testimonial[] = [];
