/**
 * GALLERY
 * ---------------------------------------------------------------
 * Replace these illustrations with photos of YOUR completed work.
 * 1. Put the photo in /public/images/gallery/ (JPG or WebP, about 1200px wide).
 * 2. Change `image` below to "/images/gallery/your-photo.jpg".
 * 3. Write a short, honest caption and alt text (good for Google Images).
 */

export type GalleryItem = {
  image: string;
  alt: string;
  title: string;
  category: "Changeover" | "Panels" | "Distribution Boards" | "Maintenance";
};

export const gallery: GalleryItem[] = [
  { image: "/images/gallery/phase-changeover-eb-board.svg", alt: "Phase changeover switch installed next to EB meter board", title: "Phase changeover at EB meter board", category: "Changeover" },
  { image: "/images/gallery/eb-dg-changeover-panel.svg", alt: "EB to generator changeover panel installation", title: "EB – generator changeover panel", category: "Changeover" },
  { image: "/images/gallery/distribution-board-wiring.svg", alt: "Neatly wired distribution board with MCBs and RCCB", title: "Distribution board wiring", category: "Distribution Boards" },
  { image: "/images/gallery/lt-panel-installation.svg", alt: "LT electrical panel with meters and MCCBs installed in a commercial building", title: "LT panel installation", category: "Panels" },
  { image: "/images/gallery/pump-control-panel.svg", alt: "Pump control panel with contactor and overload relay", title: "Pump control panel", category: "Panels" },
  { image: "/images/gallery/preventive-maintenance.svg", alt: "Technician performing preventive maintenance on an electrical panel", title: "Preventive panel maintenance", category: "Maintenance" },
];
