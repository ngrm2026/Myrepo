/**
 * GALLERY
 * ---------------------------------------------------------------
 * The first six items are real Nu-Gen product photos. The rest are illustrations:
 * replace them with photos of YOUR completed installations.
 * 1. Put the photo in /public/images/gallery/ (JPG or WebP, about 1200px wide).
 * 2. Change `image` below to "/images/gallery/your-photo.jpg".
 * 3. Write a short, honest caption and alt text (good for Google Images).
 */

export type GalleryItem = {
  image: string;
  alt: string;
  title: string;
  category: "Products" | "Changeover" | "Panels" | "Distribution Boards" | "Maintenance";
};

export const gallery: GalleryItem[] = [
  { image: "/images/gallery/nugen-apc1.jpg", alt: "Nu-Gen electronic automatic phase changeover unit in white enclosure", title: "Nu-Gen automatic phase changeover", category: "Products" },
  { image: "/images/gallery/nugen-apc2.jpg", alt: "Nu-Gen auto phase changer in grey wall-mount enclosure with rating label", title: "Nu-Gen auto phase changer (EAPC)", category: "Products" },
  { image: "/images/gallery/nugen-db-single.jpg", alt: "Nu-Gen single door distribution board with MCBs and phase changeover compartment", title: "Single door DB with phase changeover", category: "Products" },
  { image: "/images/gallery/nugen-db-double-open.jpg", alt: "Nu-Gen double door distribution board open, with incomer and phase changeover unit", title: "Double door DB", category: "Products" },
  { image: "/images/gallery/nugen-db-double-closed.jpg", alt: "Nu-Gen double door distribution board closed", title: "Double door DB (closed)", category: "Products" },
  { image: "/images/gallery/nugen-ats.jpg", alt: "Nu-Gen ATS panel with digital controller for EB and generator changeover", title: "ATS panel for EB / generator", category: "Products" },
  { image: "/images/gallery/phase-changeover-eb-board.svg", alt: "Phase changeover switch installed next to EB meter board", title: "Phase changeover at EB meter board", category: "Changeover" },
  { image: "/images/gallery/eb-dg-changeover-panel.svg", alt: "EB to generator changeover panel installation", title: "EB – generator changeover panel", category: "Changeover" },
  { image: "/images/gallery/distribution-board-wiring.svg", alt: "Neatly wired distribution board with MCBs and RCCB", title: "Distribution board wiring", category: "Distribution Boards" },
  { image: "/images/gallery/lt-panel-installation.svg", alt: "LT electrical panel with meters and MCCBs installed in a commercial building", title: "LT panel installation", category: "Panels" },
  { image: "/images/gallery/pump-control-panel.svg", alt: "Pump control panel with contactor and overload relay", title: "Pump control panel", category: "Panels" },
  { image: "/images/gallery/preventive-maintenance.svg", alt: "Technician performing preventive maintenance on an electrical panel", title: "Preventive panel maintenance", category: "Maintenance" },
];
