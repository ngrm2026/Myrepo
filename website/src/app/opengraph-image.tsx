import { ImageResponse } from "next/og";
import { siteConfig } from "@/config/site";

export const alt = "EB Switch & Phase Changeover Sales and Services in Chennai";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpengraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: 72,
          background: "linear-gradient(135deg, #071328 0%, #142d53 60%, #1b3c6d 100%)",
          color: "white",
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          <div
            style={{
              width: 84,
              height: 84,
              borderRadius: 20,
              background: "linear-gradient(135deg, #facc15, #f97316)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <svg width="52" height="52" viewBox="0 0 24 24">
              <path d="M13.5 2 4 13.5h6.2L9 22l10-12.2h-6.3L13.5 2Z" fill="#071328" />
            </svg>
          </div>
          <div style={{ fontSize: 34, fontWeight: 700 }}>{siteConfig.name}</div>
        </div>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ fontSize: 68, fontWeight: 800, lineHeight: 1.1 }}>
            Reliable EB Switch &amp; Phase Changeover Solutions in Chennai
          </div>
          <div style={{ marginTop: 24, fontSize: 30, color: "#facc15" }}>
            Sales · Installation · Repair · Maintenance
          </div>
        </div>
        <div style={{ display: "flex", gap: 16, fontSize: 26, color: "#d9e5f4" }}>
          <span>Call / WhatsApp: {siteConfig.phoneDisplay}</span>
        </div>
      </div>
    ),
    size,
  );
}
