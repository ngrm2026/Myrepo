#!/usr/bin/env python3
"""
Generates the illustrative SVG images used on the website
(public/images/products, public/images/gallery, hero and about images).

These are placeholders in a consistent style. Replace them with real photos
of your products and completed work whenever possible (see README).

Run:  python3 scripts/generate-illustrations.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "public" / "images"
FONT = "Arial, Helvetica, sans-serif"

NAVY = "#071328"
NAVY2 = "#142d53"
ORANGE = "#f97316"
YELLOW = "#facc15"

DEFS = f"""
<defs>
  <radialGradient id="studio" cx="50%" cy="38%" r="75%">
    <stop offset="0" stop-color="#ffffff"/><stop offset="0.6" stop-color="#eef2f7"/><stop offset="1" stop-color="#d6dee9"/>
  </radialGradient>
  <linearGradient id="wall" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#e9e4dc"/><stop offset="1" stop-color="#d9d2c6"/>
  </linearGradient>
  <linearGradient id="darkwall" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{NAVY2}"/><stop offset="1" stop-color="{NAVY}"/>
  </linearGradient>
  <linearGradient id="metal" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#f4f6f9"/><stop offset="0.55" stop-color="#dfe4ea"/><stop offset="1" stop-color="#c3cbd5"/>
  </linearGradient>
  <linearGradient id="greypanel" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#d9dde3"/><stop offset="1" stop-color="#a9b1bc"/>
  </linearGradient>
  <linearGradient id="plastic" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#e7eaee"/>
  </linearGradient>
  <linearGradient id="darkplastic" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3a414b"/><stop offset="1" stop-color="#1c2129"/>
  </linearGradient>
  <linearGradient id="knob" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#4b5563"/><stop offset="1" stop-color="#111827"/>
  </linearGradient>
  <linearGradient id="redknob" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#ef4444"/><stop offset="1" stop-color="#991b1b"/>
  </linearGradient>
  <linearGradient id="copper" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#b45309"/><stop offset="0.5" stop-color="#f59e0b"/><stop offset="1" stop-color="#b45309"/>
  </linearGradient>
  <linearGradient id="lcd" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#0f3d2e"/><stop offset="1" stop-color="#062419"/>
  </linearGradient>
  <linearGradient id="panelblue" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#e8ebef"/><stop offset="1" stop-color="#c7ced8"/>
  </linearGradient>
  <filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="14"/></filter>
  <filter id="drop" x="-20%" y="-20%" width="140%" height="150%">
    <feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#0b1a33" flood-opacity="0.28"/>
  </filter>
  <filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="6"/></filter>
</defs>"""


def svg(w, h, body, title, vb=None, vw=None, vh=None):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb or f'0 0 {w} {h}'}" width="{vw or w}" height="{vh or h}" role="img">'
        f"<title>{title}</title>{DEFS}{body}</svg>\n"
    )


def text(x, y, s, size=14, fill="#1f2937", weight="700", anchor="middle", extra="", family=FONT):
    return (
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
        f'fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>'
    )


# ---------- backgrounds ----------
def studio_bg(w=800, h=600):
    return (
        f'<rect width="{w}" height="{h}" fill="url(#studio)"/>'
        f'<path d="M0 {h-150} L{w} {h-190} L{w} {h} L0 {h} Z" fill="#cfd8e4" opacity="0.45"/>'
        f'<path d="M{w-170} 0 L{w} 0 L{w} 170 Z" fill="{ORANGE}" opacity="0.9"/>'
        f'<path d="M{w-120} 0 L{w} 0 L{w} 120 Z" fill="{YELLOW}"/>'
    )


def wall_bg(w=800, h=600):
    tiles = "".join(
        f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="#cbc3b5" stroke-width="1" opacity="0.5"/>' for y in range(60, h, 60)
    )
    return f'<rect width="{w}" height="{h}" fill="url(#wall)"/>{tiles}<rect y="{h-40}" width="{w}" height="40" fill="#b9b0a2"/>'


def dark_bg(w, h):
    grid = "".join(
        f'<line x1="{x}" y1="0" x2="{x}" y2="{h}" stroke="#ffffff" stroke-opacity="0.05"/>' for x in range(0, w, 40)
    ) + "".join(
        f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="#ffffff" stroke-opacity="0.05"/>' for y in range(0, h, 40)
    )
    return (
        f'<rect width="{w}" height="{h}" fill="url(#darkwall)"/>{grid}'
        f'<circle cx="{w*0.8}" cy="{h*0.2}" r="{w*0.28}" fill="{ORANGE}" opacity="0.18" filter="url(#soft)"/>'
        f'<circle cx="{w*0.15}" cy="{h*0.85}" r="{w*0.25}" fill="#3463a6" opacity="0.35" filter="url(#soft)"/>'
    )


def floor_shadow(cx, cy, rx, ry=18):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#0b1a33" opacity="0.25" filter="url(#soft)"/>'


# ---------- components ----------
def screw(cx, cy, r=5):
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#9aa3ae" stroke="#6b7480" stroke-width="1"/>'
        f'<line x1="{cx-r+1.5}" y1="{cy}" x2="{cx+r-1.5}" y2="{cy}" stroke="#4b5563" stroke-width="1.4"/>'
    )


def enclosure(x, y, w, h, fill="url(#metal)", rx=14, screws=True):
    s = (
        f'<g filter="url(#drop)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="#9aa5b3" stroke-width="2"/></g>'
        f'<rect x="{x+10}" y="{y+10}" width="{w-20}" height="{h-20}" rx="{rx-6}" fill="none" stroke="#ffffff" stroke-opacity="0.7" stroke-width="2"/>'
    )
    if screws:
        s += screw(x + 22, y + 22) + screw(x + w - 22, y + 22) + screw(x + 22, y + h - 22) + screw(x + w - 22, y + h - 22)
    return s


def gland(cx, cy, cable="#111827"):
    return (
        f'<rect x="{cx-16}" y="{cy}" width="32" height="18" rx="4" fill="#374151"/>'
        f'<rect x="{cx-9}" y="{cy+18}" width="18" height="60" rx="6" fill="{cable}"/>'
    )


def rotary_knob(cx, cy, r=62, angle=-35, fill="url(#knob)"):
    ridges = "".join(
        f'<line x1="{cx}" y1="{cy-r+4}" x2="{cx}" y2="{cy-r+14}" stroke="#ffffff" stroke-opacity="0.18" stroke-width="3" transform="rotate({a} {cx} {cy})"/>'
        for a in range(0, 360, 20)
    )
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r+14}" fill="#cfd5dd" stroke="#9aa5b3" stroke-width="2"/>'
        f'<circle cx="{cx}" cy="{cy+4}" r="{r}" fill="#000" opacity="0.25" filter="url(#glow)"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>{ridges}'
        f'<g transform="rotate({angle} {cx} {cy})">'
        f'<rect x="{cx-13}" y="{cy-r-6}" width="26" height="{2*r+12}" rx="13" fill="#1f2937" stroke="#0b0f15" stroke-width="2"/>'
        f'<rect x="{cx-4}" y="{cy-r+2}" width="8" height="34" rx="4" fill="{YELLOW}"/></g>'
        f'<circle cx="{cx}" cy="{cy}" r="9" fill="#6b7280"/>'
    )


def mcb(x, y, w=34, h=120, label="C16", on=True, body="url(#plastic)", toggle="#1f2937", poles_label=None):
    ty = y + h * 0.42
    t = (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{body}" stroke="#aab2bd"/>'
        f'<rect x="{x+3}" y="{y+6}" width="{w-6}" height="14" rx="2" fill="#d1d6dc"/>'
        f'<rect x="{x+3}" y="{y+h-20}" width="{w-6}" height="14" rx="2" fill="#d1d6dc"/>'
        f'<circle cx="{x+w/2}" cy="{y+13}" r="4" fill="#8a929c"/><circle cx="{x+w/2}" cy="{y+h-13}" r="4" fill="#8a929c"/>'
        f'<rect x="{x+w/2-9}" y="{ty-14}" width="18" height="34" rx="3" fill="#c5cbd3"/>'
        f'<rect x="{x+w/2-7}" y="{ty-12 if on else ty+2}" width="14" height="16" rx="3" fill="{toggle}"/>'
        f'<rect x="{x+w/2-6}" y="{y+h*0.68}" width="12" height="6" rx="1" fill="{"#22c55e" if on else "#ef4444"}"/>'
    )
    t += text(x + w / 2, y + h * 0.82, label, size=10, fill="#374151")
    return t


def lamp(cx, cy, r, color, label=None, label_fill="#e5e7eb"):
    s = (
        f'<circle cx="{cx}" cy="{cy}" r="{r+6}" fill="#9ca3af"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r+6}" fill="none" stroke="#6b7280"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r*1.6}" fill="{color}" opacity="0.45" filter="url(#glow)"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/>'
        f'<circle cx="{cx-r*0.35}" cy="{cy-r*0.35}" r="{r*0.3}" fill="#fff" opacity="0.6"/>'
    )
    if label:
        s += text(cx, cy + r + 24, label, size=13, fill=label_fill)
    return s


def analog_meter(x, y, s=96, label="V", needle=-20):
    cx, cy = x + s / 2, y + s * 0.68
    ticks = "".join(
        f'<line x1="{cx}" y1="{cy-s*0.42}" x2="{cx}" y2="{cy-s*0.36}" stroke="#111827" stroke-width="1.5" transform="rotate({a} {cx} {cy})"/>'
        for a in range(-50, 51, 10)
    )
    return (
        f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="6" fill="#111827"/>'
        f'<rect x="{x+6}" y="{y+6}" width="{s-12}" height="{s-12}" rx="4" fill="#f8fafc"/>'
        f'<path d="M{cx-s*0.4} {cy-s*0.06} A{s*0.42} {s*0.42} 0 0 1 {cx+s*0.4} {cy-s*0.06}" fill="none" stroke="#ef4444" stroke-width="3" stroke-dasharray="0 {s*0.55} {s*0.2} 999"/>'
        f"{ticks}"
        f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy-s*0.4}" stroke="#dc2626" stroke-width="2.2" transform="rotate({needle} {cx} {cy})"/>'
        f'<circle cx="{cx}" cy="{cy}" r="4" fill="#111827"/>'
        + text(cx, y + s - 12, label, size=s * 0.14, fill="#111827")
    )


def digital_meter(x, y, w=120, h=80, value="230.4", unit="V"):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#1f2937"/>'
        f'<rect x="{x+8}" y="{y+8}" width="{w-16}" height="{h-30}" rx="3" fill="url(#lcd)"/>'
        + text(x + w / 2, y + h * 0.52, value, size=h * 0.3, fill="#4ade80", extra='letter-spacing="2"', family="'Courier New', monospace")
        + text(x + w / 2, y + h - 8, unit, size=11, fill="#9ca3af")
    )


def selector(cx, cy, r=16, angle=40):
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r+6}" fill="#d1d5db" stroke="#9ca3af"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#knob)"/>'
        f'<rect x="{cx-4}" y="{cy-r}" width="8" height="{2*r}" rx="4" fill="#e5e7eb" transform="rotate({angle} {cx} {cy})"/>'
    )


def handle(x, y, w=26, h=90):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{w/2}" fill="url(#darkplastic)" stroke="#0b0f15"/><rect x="{x+w/2-3}" y="{y+12}" width="6" height="{h-24}" rx="3" fill="#6b7280"/>'


def nameplate(x, y, w, h, s, size=13, fill=NAVY, color="#ffffff"):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}"/>' + text(
        x + w / 2, y + h / 2 + size * 0.36, s, size=size, fill=color
    )


def bolt(x, y, s=1.0, fill=YELLOW):
    return f'<path transform="translate({x} {y}) scale({s})" d="M13.5 2 4 13.5h6.2L9 22l10-12.2h-6.3L13.5 2Z" fill="{fill}"/>'


def energy_meter(x, y, w=150, h=210):
    return (
        f'<g filter="url(#drop)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#f1f5f9" stroke="#94a3b8" stroke-width="2"/></g>'
        f'<rect x="{x+14}" y="{y+16}" width="{w-28}" height="{h*0.55}" rx="6" fill="#e2e8f0" stroke="#cbd5e1"/>'
        + digital_meter(x + 24, y + 30, w - 48, 56, "04127", "kWh")
        + f'<circle cx="{x+40}" cy="{y+h*0.5}" r="5" fill="#ef4444"/>'
        + text(x + 52, y + h * 0.5 + 4, "imp/kWh", size=9, fill="#475569", anchor="start", weight="400")
        + nameplate(x + 20, y + h * 0.66, w - 40, 22, "ENERGY METER", size=10, fill="#334155")
        + f'<rect x="{x+20}" y="{y+h-46}" width="{w-40}" height="28" rx="4" fill="#cbd5e1"/>'
        + "".join(f'<circle cx="{x+34+i*((w-68)/3)}" cy="{y+h-32}" r="5" fill="#64748b"/>' for i in range(4))
    )


def cable_path(d, color="#111827", width=10):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>'


def person(x, y, s=1.0, facing=1):
    """Simple flat illustration of a technician (helmet, uniform)."""
    f = facing
    return f"""<g transform="translate({x} {y}) scale({s*f} {s})">
      <path d="M-55 300 C-60 210 -45 150 0 140 C45 150 60 210 55 300 Z" fill="#1b3c6d"/>
      <path d="M-20 142 L0 190 L20 142 Z" fill="#e2e8f0"/>
      <rect x="-48" y="196" width="96" height="10" fill="{ORANGE}"/>
      <rect x="-48" y="236" width="96" height="10" fill="{ORANGE}"/>
      <rect x="-14" y="112" width="28" height="34" rx="8" fill="#a16207"/>
      <ellipse cx="0" cy="88" rx="36" ry="42" fill="#b4743b"/>
      <path d="M-42 78 C-42 30 42 30 42 78 Z" fill="{YELLOW}"/>
      <rect x="-48" y="72" width="96" height="12" rx="6" fill="#eab308"/>
      <rect x="-6" y="34" width="12" height="40" rx="5" fill="#eab308"/>
      <circle cx="14" cy="96" r="3.5" fill="#1f2937"/>
      <path d="M8 116 Q16 122 24 116" stroke="#1f2937" stroke-width="3" fill="none" stroke-linecap="round"/>
      <path d="M40 170 C80 170 105 150 120 120" stroke="#1b3c6d" stroke-width="30" fill="none" stroke-linecap="round"/>
      <circle cx="122" cy="116" r="16" fill="#b4743b"/>
      <rect x="128" y="88" width="10" height="34" rx="3" fill="{ORANGE}" transform="rotate(30 133 105)"/>
      <rect x="140" y="62" width="4" height="30" fill="#9ca3af" transform="rotate(30 142 77)"/>
    </g>"""


# ---------- products ----------
def p_manual_phase():
    b = studio_bg() + floor_shadow(400, 545, 190)
    b += enclosure(250, 70, 300, 450)
    b += nameplate(300, 100, 200, 34, "PHASE SELECTOR", 15)
    b += rotary_knob(400, 300, 70, -40)
    for lbl, ang, col in (("R", -50, "#dc2626"), ("Y", 0, "#ca8a04"), ("B", 50, "#2563eb")):
        import math

        a = math.radians(ang - 90)
        x, y = 400 + 118 * math.cos(a), 300 + 118 * math.sin(a)
        b += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="19" fill="{col}"/>' + text(f"{x:.1f}", f"{y+6:.1f}", lbl, 18, "#fff")
    b += text(400, 452, "MANUAL PHASE CHANGEOVER", 13, "#334155")
    b += gland(330, 520) + gland(400, 520) + gland(470, 520)
    return svg(800, 600, b, "Manual phase changeover switch illustration")


def p_auto_phase():
    b = studio_bg() + floor_shadow(400, 535, 170)
    b += f'<rect x="150" y="140" width="500" height="22" rx="3" fill="#9ca3af"/>'  # DIN rail
    b += enclosure(270, 80, 260, 420, fill="url(#plastic)", screws=False)
    for i in range(4):
        b += f'<rect x="{298+i*56}" y="96" width="36" height="26" rx="4" fill="#cbd5e1"/>' + screw(316 + i * 56, 109, 7)
        b += f'<rect x="{298+i*56}" y="458" width="36" height="26" rx="4" fill="#cbd5e1"/>' + screw(316 + i * 56, 471, 7)
    b += nameplate(300, 140, 200, 30, "AUTO PHASE SELECTOR", 13)
    b += digital_meter(310, 186, 180, 92, "231.6", "VOLTS · OUTPUT")
    for i, (c, l) in enumerate((("#ef4444", "R"), ("#facc15", "Y"), ("#3b82f6", "B"))):
        b += lamp(340 + i * 60, 318, 11, c, l, label_fill="#334155")
    b += f'<rect x="318" y="380" width="164" height="54" rx="8" fill="#e2e8f0" stroke="#cbd5e1"/>'
    b += text(400, 403, "AUTO", 15, ORANGE) + text(400, 423, "PHASE CHANGEOVER", 10, "#475569")
    return svg(800, 600, b, "Automatic phase changeover switch illustration")


def p_single_phase():
    b = studio_bg() + floor_shadow(400, 540, 180)
    b += enclosure(260, 80, 280, 420, fill="url(#greypanel)")
    b += nameplate(305, 108, 190, 32, "CHANGEOVER SWITCH", 13)
    b += f'<rect x="320" y="170" width="160" height="230" rx="16" fill="#e5e7eb" stroke="#9ca3af" stroke-width="2"/>'
    b += text(400, 200, "I", 26, "#16a34a") + text(400, 292, "0", 22, "#6b7280") + text(400, 390, "II", 26, "#dc2626")
    b += text(455, 200, "MAINS", 11, "#374151") + text(455, 390, "DG / INV", 11, "#374151")
    b += f'<g transform="rotate(-28 400 285)"><rect x="384" y="198" width="32" height="96" rx="12" fill="url(#redknob)"/><circle cx="400" cy="285" r="22" fill="#111827"/></g>'
    b += text(400, 450, "SINGLE PHASE · DP", 13, "#1f2937")
    b += gland(350, 500) + gland(450, 500)
    return svg(800, 600, b, "Single phase changeover switch illustration")


def p_three_phase():
    b = studio_bg() + floor_shadow(400, 530, 260)
    # open-execution 4 pole changeover
    b += f'<g filter="url(#drop)"><rect x="160" y="140" width="480" height="340" rx="16" fill="url(#darkplastic)"/></g>'
    for row_y in (150, 440):
        for i in range(8):
            x = 182 + i * 56
            b += f'<rect x="{x}" y="{row_y}" width="44" height="30" rx="4" fill="url(#copper)"/>' + screw(x + 22, row_y + 15, 7)
    b += f'<rect x="200" y="200" width="400" height="220" rx="12" fill="#2b313a" stroke="#4b5563"/>'
    b += text(260, 240, "I", 30, "#4ade80") + text(400, 240, "0", 26, "#e5e7eb") + text(540, 240, "II", 30, "#f87171")
    b += f'<circle cx="400" cy="320" r="70" fill="#1f2937" stroke="#6b7280" stroke-width="3"/>'
    b += f'<g transform="rotate(-45 400 320)"><rect x="384" y="230" width="32" height="140" rx="16" fill="url(#redknob)"/></g><circle cx="400" cy="320" r="18" fill="#111827"/>'
    b += text(400, 412, "4 POLE · ON-LOAD CHANGEOVER", 12, "#cbd5e1")
    b += text(220, 135, "SOURCE I", 12, "#334155", anchor="start") + text(580, 135, "SOURCE II", 12, "#334155", anchor="end")
    return svg(800, 600, b, "Three phase four pole changeover switch illustration")


def p_eb_dg():
    b = studio_bg() + floor_shadow(400, 545, 220)
    b += enclosure(220, 60, 360, 470, fill="url(#panelblue)")
    b += nameplate(270, 90, 260, 34, "EB / DG CHANGEOVER", 15)
    b += f'<rect x="262" y="140" width="276" height="120" rx="10" fill="#1f2937"/>'
    b += lamp(330, 190, 18, "#22c55e", "EB ON") + lamp(470, 190, 18, "#f59e0b", "DG ON")
    b += digital_meter(300, 280, 200, 70, "415 V", "SUPPLY")
    b += f'<rect x="300" y="370" width="200" height="110" rx="10" fill="#e5e7eb" stroke="#9ca3af"/>'
    b += text(330, 400, "EB", 16, "#16a34a") + text(400, 400, "OFF", 14, "#6b7280") + text(470, 400, "DG", 16, "#d97706")
    b += f'<g transform="rotate(-35 400 450)"><rect x="388" y="400" width="24" height="70" rx="10" fill="url(#redknob)"/></g><circle cx="400" cy="450" r="16" fill="#111827"/>'
    b += handle(540, 270, 22, 90)
    # generator icon
    b += f'<g transform="translate(610 400)"><rect x="0" y="40" width="130" height="90" rx="10" fill="{NAVY2}"/><rect x="12" y="54" width="60" height="40" rx="4" fill="#1b3c6d"/>{bolt(84,58,2.2)}<rect x="10" y="130" width="20" height="10" fill="#334155"/><rect x="100" y="130" width="20" height="10" fill="#334155"/></g>'
    b += text(675, 560, "GENERATOR", 12, "#334155")
    return svg(800, 600, b, "EB and generator changeover switch panel illustration")


def p_db():
    b = studio_bg() + floor_shadow(400, 540, 260)
    b += enclosure(150, 90, 500, 420, fill="url(#metal)")
    # door open to the right
    b += f'<path d="M650 100 L740 130 L740 480 L650 500 Z" fill="#cfd6df" stroke="#9aa5b3" stroke-width="2"/>'
    b += f'<rect x="185" y="125" width="430" height="350" rx="8" fill="#f8fafc" stroke="#cbd5e1"/>'
    b += nameplate(200, 140, 120, 26, "DB · TPN", 12)
    b += f'<rect x="190" y="260" width="420" height="10" rx="2" fill="#94a3b8"/>'
    # RCCB + MCBs
    b += mcb(205, 200, 66, 140, "RCCB 63A", body="url(#plastic)", toggle="#2563eb")
    b += f'<rect x="230" y="320" width="16" height="10" rx="2" fill="#facc15"/>'
    for i in range(9):
        b += mcb(282 + i * 36, 200, 34, 140, ["C32", "C16", "C16", "C10", "C10", "C6", "C20", "C16", "C6"][i], on=(i != 6))
    for i, c in enumerate(["#dc2626", "#111827", "#2563eb", "#facc15", "#16a34a"]):
        b += cable_path(f"M{240+i*80} 345 C{240+i*80} 400 {260+i*70} 420 {270+i*65} 470", c, 7)
    b += text(400, 460, "", 12)
    return svg(800, 600, b, "Electrical distribution board illustration")


def p_mcb_mccb():
    b = studio_bg() + floor_shadow(400, 520, 300)
    labels = ["B6", "C16", "C32", "D40"]
    for i, l in enumerate(labels):
        b += f'<g filter="url(#drop)">{mcb(110 + i * 52, 210, 48, 240, l)}</g>'
    # MCCB
    b += f'<g filter="url(#drop)"><rect x="380" y="130" width="300" height="360" rx="14" fill="url(#darkplastic)"/></g>'
    for i in range(3):
        b += f'<rect x="{405+i*90}" y="145" width="70" height="40" rx="5" fill="#2b313a"/>' + screw(440 + i * 90, 165, 9)
        b += f'<rect x="{405+i*90}" y="435" width="70" height="40" rx="5" fill="#2b313a"/>' + screw(440 + i * 90, 455, 9)
    b += f'<rect x="420" y="205" width="220" height="210" rx="10" fill="#2f3640" stroke="#4b5563"/>'
    b += f'<rect x="500" y="230" width="60" height="120" rx="8" fill="#1f2937"/><rect x="510" y="236" width="40" height="60" rx="6" fill="#d1d5db"/>'
    b += text(530, 380, "ON  I", 12, "#e5e7eb") + text(530, 400, "MCCB", 14, YELLOW)
    b += selector(600, 330, 13, 30) + text(600, 365, "Ir", 11, "#cbd5e1")
    b += f'<rect x="440" y="320" width="40" height="18" rx="3" fill="#ef4444"/>' + text(460, 354, "TEST", 9, "#cbd5e1")
    return svg(800, 600, b, "MCB and MCCB circuit breakers illustration")


def p_contactor():
    b = studio_bg() + floor_shadow(400, 530, 200)
    b += f'<g filter="url(#drop)"><rect x="270" y="110" width="260" height="380" rx="16" fill="url(#greypanel)"/></g>'
    b += f'<rect x="300" y="70" width="200" height="60" rx="8" fill="#cbd5e1" stroke="#94a3b8"/>'  # aux block
    b += text(400, 105, "AUX 1NO+1NC", 11, "#334155")
    for row_y in (140, 430):
        for i in range(3):
            b += f'<rect x="{290+i*78}" y="{row_y}" width="62" height="40" rx="5" fill="#9ca3af"/>' + screw(321 + i * 78, row_y + 20, 10)
    b += f'<rect x="300" y="200" width="200" height="210" rx="10" fill="#e5e7eb" stroke="#9ca3af"/>'
    b += f'<rect x="345" y="230" width="110" height="70" rx="6" fill="#111827"/><rect x="365" y="250" width="70" height="30" rx="4" fill="#f8fafc"/>'
    b += text(400, 336, "CONTACTOR", 16, NAVY) + text(400, 360, "3 POLE · AC-3", 12, "#475569")
    b += text(400, 390, "Coil 230V AC", 11, "#64748b", weight="400")
    for i, l in enumerate(("1/L1", "3/L2", "5/L3")):
        b += text(321 + i * 78, 194, l, 10, "#334155")
    return svg(800, 600, b, "Electrical power contactor illustration")


def p_industrial():
    b = studio_bg() + floor_shadow(400, 560, 260)
    b += f'<g filter="url(#drop)"><rect x="200" y="40" width="400" height="510" rx="8" fill="url(#panelblue)" stroke="#94a3b8" stroke-width="2"/></g>'
    b += f'<line x1="200" y1="190" x2="600" y2="190" stroke="#94a3b8" stroke-width="2"/><line x1="200" y1="450" x2="600" y2="450" stroke="#94a3b8" stroke-width="2"/>'
    b += analog_meter(240, 70, 96, "V", -15) + analog_meter(352, 70, 96, "A", 10) + digital_meter(464, 78, 100, 80, "49.9", "Hz")
    # ACB
    b += f'<rect x="250" y="215" width="300" height="210" rx="10" fill="url(#darkplastic)"/>'
    b += f'<rect x="275" y="240" width="110" height="60" rx="6" fill="#2b313a"/>' + text(330, 278, "ACB", 22, YELLOW)
    b += f'<circle cx="440" cy="268" r="20" fill="#16a34a"/>' + text(440, 274, "I", 16, "#fff")
    b += f'<circle cx="500" cy="268" r="20" fill="#dc2626"/>' + text(500, 274, "O", 16, "#fff")
    b += f'<rect x="275" y="320" width="250" height="80" rx="6" fill="#2b313a"/>'
    b += f'<rect x="300" y="340" width="90" height="40" rx="4" fill="#e5e7eb"/>' + text(345, 366, "CHARGED", 10, "#111827")
    b += f'<rect x="410" y="340" width="90" height="40" rx="4" fill="#facc15"/>' + text(455, 366, "OPEN", 11, "#111827")
    for i, c in enumerate(("#ef4444", "#facc15", "#3b82f6")):
        b += lamp(290 + i * 50, 495, 12, c)
    b += handle(540, 470, 22, 60)
    return svg(800, 600, b, "Industrial switchgear panel with air circuit breaker illustration")


def p_custom_panel():
    b = studio_bg() + floor_shadow(400, 565, 330)
    b += f'<g filter="url(#drop)"><rect x="80" y="50" width="640" height="500" rx="8" fill="url(#panelblue)" stroke="#94a3b8" stroke-width="2"/></g>'
    for x in (293, 506):
        b += f'<line x1="{x}" y1="50" x2="{x}" y2="550" stroke="#94a3b8" stroke-width="2"/>'
    # door 1: meters + lamps
    b += analog_meter(110, 80, 80, "V", -10) + analog_meter(198, 80, 80, "A", 15)
    for i, c in enumerate(("#ef4444", "#facc15", "#3b82f6")):
        b += lamp(135 + i * 55, 220, 12, c, "RYB"[i], "#334155")
    b += selector(150, 310, 18, -40) + selector(240, 310, 18, 40)
    b += text(150, 352, "V SEL", 10, "#334155") + text(240, 352, "A SEL", 10, "#334155")
    b += nameplate(110, 400, 160, 30, "INCOMER", 12)
    # door 2: changeover
    b += nameplate(323, 80, 160, 30, "EB / DG", 12)
    b += lamp(360, 150, 14, "#22c55e", "EB", "#334155") + lamp(446, 150, 14, "#f59e0b", "DG", "#334155")
    b += f'<circle cx="400" cy="290" r="60" fill="#e5e7eb" stroke="#9ca3af" stroke-width="2"/>'
    b += f'<g transform="rotate(-30 400 290)"><rect x="386" y="225" width="28" height="130" rx="12" fill="url(#redknob)"/></g><circle cx="400" cy="290" r="16" fill="#111827"/>'
    b += digital_meter(340, 390, 120, 70, "18.6", "kW")
    # door 3: outgoing
    b += nameplate(536, 80, 160, 30, "OUTGOING", 12)
    for r in range(3):
        b += f'<rect x="540" y="{130+r*120}" width="150" height="100" rx="6" fill="#d7dde5" stroke="#9ca3af"/>'
        b += f'<rect x="555" y="{148+r*120}" width="56" height="64" rx="4" fill="#1f2937"/><rect x="573" y="{158+r*120}" width="20" height="30" rx="3" fill="#d1d5db"/>'
        b += lamp(650, 180 + r * 120, 10, "#22c55e")
    for x in (270, 483, 696):
        b += handle(x, 260, 16, 60)
    return svg(800, 600, b, "Custom electrical control panel illustration")


# ---------- hero / about ----------
def hero():
    w, h = 960, 760
    b = dark_bg(w, h)
    # wall plate
    b += f'<rect x="60" y="80" width="840" height="600" rx="24" fill="#e7e2d9"/>'
    b += "".join(f'<line x1="60" y1="{y}" x2="900" y2="{y}" stroke="#cfc6b8" opacity="0.6"/>' for y in range(140, 680, 60))
    # conduit
    b += f'<rect x="120" y="80" width="26" height="140" fill="#d1d5db"/><rect x="814" y="80" width="26" height="160" fill="#d1d5db"/>'
    b += energy_meter(110, 210, 160, 230)
    # manual phase changeover
    b += enclosure(310, 200, 200, 270, fill="url(#metal)")
    b += nameplate(340, 222, 140, 26, "PHASE SELECTOR", 11)
    b += rotary_knob(410, 335, 46, -35)
    import math

    for lbl, ang, col in (("R", -50, "#dc2626"), ("Y", 0, "#ca8a04"), ("B", 50, "#2563eb")):
        a = math.radians(ang - 90)
        x, y = 410 + 80 * math.cos(a), 335 + 80 * math.sin(a)
        b += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="{col}"/>' + text(f"{x:.1f}", f"{y+5:.1f}", lbl, 13, "#fff")
    # DB with MCBs
    b += enclosure(550, 180, 310, 300, fill="url(#metal)")
    b += f'<rect x="572" y="205" width="266" height="250" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>'
    b += nameplate(585, 216, 100, 22, "MAIN DB", 10)
    b += mcb(585, 255, 50, 120, "RCCB", toggle="#2563eb")
    for i in range(6):
        b += mcb(642 + i * 31, 255, 29, 120, ["C32", "C16", "C16", "C10", "C6", "C6"][i])
    b += text(705, 420, "ELCB / MCB PROTECTION", 10, "#64748b")
    # cables
    b += cable_path("M190 440 C190 520 300 520 330 470", "#dc2626", 9)
    b += cable_path("M210 440 C210 540 360 540 380 470", "#111827", 9)
    b += cable_path("M470 470 C480 540 600 540 620 480", "#dc2626", 9)
    b += cable_path("M490 470 C500 560 680 560 700 480", "#111827", 9)
    b += cable_path("M800 480 L800 680", "#1f2937", 14)
    # label strip
    b += f'<rect x="110" y="560" width="740" height="80" rx="14" fill="{NAVY}"/>'
    b += bolt(132, 578, 2.0) + text(190, 604, "EB SUPPLY  →  PHASE CHANGEOVER  →  DISTRIBUTION", 18, "#ffffff", anchor="start")
    b += text(190, 628, "Safe · Neat · Tested installation", 14, YELLOW, anchor="start", weight="600")
    # glow bolts
    b += f'<circle cx="880" cy="110" r="46" fill="{ORANGE}" opacity="0.35" filter="url(#glow)"/>'
    b += f'<circle cx="880" cy="110" r="38" fill="{ORANGE}"/>' + bolt(860, 88, 1.8, "#fff")
    return svg(w, h, b, "EB meter board with phase changeover switch and distribution board", vb="40 50 890 650", vw=890, vh=650)


def about():
    w, h = 960, 720
    b = wall_bg(w, h)
    b += energy_meter(110, 180, 150, 210)
    b += enclosure(300, 170, 200, 260)
    b += nameplate(330, 190, 140, 26, "PHASE SELECTOR", 11)
    b += rotary_knob(400, 300, 44, 0)
    b += cable_path("M185 390 C185 470 300 470 340 430", "#dc2626", 8)
    b += cable_path("M205 390 C205 490 360 490 380 430", "#111827", 8)
    b += person(640, 300, 1.25, -1)
    b += f'<rect x="760" y="560" width="120" height="60" rx="8" fill="{ORANGE}"/><rect x="790" y="545" width="60" height="18" rx="6" fill="none" stroke="{ORANGE}" stroke-width="6"/>'
    b += text(820, 597, "TOOLS", 14, "#fff")
    return svg(w, h, b, "Technician installing a phase changeover switch")


# ---------- gallery ----------
def g_eb_board():
    b = wall_bg()
    b += energy_meter(90, 140, 150, 210)
    b += energy_meter(270, 140, 150, 210)
    b += enclosure(470, 130, 220, 290)
    b += nameplate(500, 150, 160, 28, "PHASE SELECTOR", 12)
    b += rotary_knob(580, 280, 50, 35)
    b += cable_path("M165 350 C165 440 480 450 520 420", "#dc2626", 8)
    b += cable_path("M345 350 C345 430 560 450 580 420", "#111827", 8)
    b += cable_path("M650 420 L650 560", "#1f2937", 12)
    return svg(800, 600, b, "Phase changeover switch next to EB meters")


def g_eb_dg():
    b = wall_bg()
    b += enclosure(80, 90, 300, 420, fill="url(#panelblue)")
    b += nameplate(130, 115, 200, 30, "EB / DG PANEL", 13)
    b += lamp(170, 200, 16, "#22c55e", "EB", "#334155") + lamp(290, 200, 16, "#f59e0b", "DG", "#334155")
    b += f'<circle cx="230" cy="330" r="56" fill="#e5e7eb" stroke="#9ca3af" stroke-width="2"/><g transform="rotate(-35 230 330)"><rect x="216" y="270" width="28" height="120" rx="12" fill="url(#redknob)"/></g><circle cx="230" cy="330" r="15" fill="#111827"/>'
    b += digital_meter(170, 410, 120, 64, "415", "VOLTS")
    b += f'<g filter="url(#drop)"><rect x="460" y="300" width="290" height="190" rx="14" fill="#facc15"/></g>'
    b += f'<rect x="480" y="320" width="150" height="90" rx="8" fill="#eab308"/>'
    b += "".join(f'<line x1="{490+i*14}" y1="330" x2="{490+i*14}" y2="400" stroke="#a16207" stroke-width="5"/>' for i in range(10))
    b += f'<rect x="650" y="320" width="80" height="60" rx="6" fill="#1f2937"/>' + text(690, 356, "DG", 18, YELLOW)
    b += text(605, 460, "DIESEL GENERATOR", 16, "#422006")
    b += cable_path("M380 400 C420 400 420 420 460 420", "#111827", 12)
    return svg(800, 600, b, "EB to generator changeover panel with generator")


def g_db_wiring():
    b = wall_bg()
    b += enclosure(100, 70, 600, 460)
    b += f'<rect x="135" y="105" width="530" height="390" rx="8" fill="#f8fafc" stroke="#cbd5e1"/>'
    b += f'<rect x="140" y="150" width="520" height="10" rx="2" fill="#94a3b8"/>'
    b += mcb(155, 120, 70, 150, "RCCB 40A", toggle="#2563eb")
    for i in range(11):
        b += mcb(232 + i * 38, 120, 36, 150, ["C40", "C16", "C16", "C16", "C10", "C10", "C10", "C6", "C6", "C20", "C20"][i])
    for i in range(12):
        c = ["#dc2626", "#111827", "#2563eb", "#16a34a", "#facc15"][i % 5]
        b += cable_path(f"M{190+i*38} 270 L{190+i*38} 330 Q{190+i*38} 360 {200+i*30} 380 L{200+i*30} 480", c, 6)
    b += nameplate(530, 440, 120, 30, "LABELLED ✓", 12, fill="#16a34a")
    return svg(800, 600, b, "Neatly wired distribution board")


def g_lt_panel():
    b = f'<rect width="800" height="600" fill="#cfd6df"/><rect y="500" width="800" height="100" fill="#9aa5b3"/>'
    b += "".join(f'<line x1="0" y1="{y}" x2="800" y2="{y}" stroke="#b8c1cc"/>' for y in range(60, 500, 60))
    for i in range(4):
        x = 60 + i * 175
        b += f'<g filter="url(#drop)"><rect x="{x}" y="90" width="165" height="420" rx="6" fill="url(#panelblue)" stroke="#94a3b8" stroke-width="2"/></g>'
        b += analog_meter(x + 15, 110, 64, "A", -20 + i * 12) + analog_meter(x + 86, 110, 64, "V", 5)
        b += f'<rect x="{x+20}" y="200" width="125" height="150" rx="6" fill="url(#darkplastic)"/><rect x="{x+60}" y="230" width="45" height="70" rx="5" fill="#d1d5db"/>'
        for j, c in enumerate(("#ef4444", "#facc15", "#3b82f6")):
            b += lamp(x + 45 + j * 38, 390, 9, c)
        b += handle(x + 135, 420, 16, 50)
        b += nameplate(x + 20, 450, 100, 22, ["INCOMER", "FEEDER 1", "FEEDER 2", "APFC"][i], 10)
    return svg(800, 600, b, "LT electrical panels installed in a commercial building")


def g_pump_panel():
    b = wall_bg()
    b += enclosure(90, 70, 330, 460, fill="url(#panelblue)")
    b += nameplate(140, 95, 230, 30, "PUMP CONTROL", 13)
    b += f'<rect x="130" y="150" width="250" height="220" rx="8" fill="#f8fafc" stroke="#cbd5e1"/>'
    b += f'<rect x="150" y="170" width="100" height="120" rx="8" fill="url(#greypanel)"/>' + text(200, 240, "CONT.", 12, NAVY)
    b += f'<rect x="150" y="300" width="100" height="50" rx="6" fill="#cbd5e1"/>' + text(200, 330, "O/L RELAY", 10, "#334155")
    b += mcb(275, 180, 40, 140, "C10") + mcb(320, 180, 40, 140, "C10")
    b += f'<circle cx="170" cy="420" r="22" fill="#16a34a"/>' + text(170, 426, "ON", 12, "#fff")
    b += f'<circle cx="250" cy="420" r="22" fill="#dc2626"/>' + text(250, 426, "OFF", 11, "#fff")
    b += lamp(330, 420, 12, "#22c55e", "RUN", "#334155")
    # pump
    b += f'<g filter="url(#drop)"><rect x="500" y="360" width="200" height="120" rx="20" fill="#2563eb"/></g>'
    b += "".join(f'<line x1="{515+i*18}" y1="372" x2="{515+i*18}" y2="468" stroke="#1d4ed8" stroke-width="6"/>' for i in range(6))
    b += f'<circle cx="700" cy="420" r="44" fill="#1e3a8a"/><rect x="690" y="300" width="20" height="80" fill="#64748b"/>'
    b += f'<rect x="490" y="480" width="220" height="20" rx="4" fill="#475569"/>'
    b += text(600, 540, "WATER PUMP MOTOR", 14, "#334155")
    b += cable_path("M420 450 C460 450 460 420 500 420", "#111827", 10)
    return svg(800, 600, b, "Pump control panel with contactor and overload relay")


def g_maintenance():
    b = wall_bg()
    b += enclosure(80, 80, 330, 440, fill="url(#panelblue)")
    b += f'<rect x="110" y="110" width="270" height="380" rx="8" fill="#f8fafc" stroke="#cbd5e1"/>'
    for r in range(2):
        for i in range(6):
            b += mcb(122 + i * 42, 130 + r * 170, 38, 140, ["C32", "C16", "C16", "C10", "C10", "C6"][i])
    b += person(560, 230, 1.0, -1)
    # clipboard
    b += f'<g transform="translate(640 420) rotate(8)"><rect x="0" y="0" width="110" height="140" rx="8" fill="#92400e"/><rect x="10" y="16" width="90" height="116" rx="4" fill="#fff"/>'
    for i in range(4):
        b += f'<path d="M20 {40+i*24} l6 6 l12 -12" stroke="#16a34a" stroke-width="4" fill="none"/><rect x="44" y="{38+i*24}" width="46" height="6" rx="3" fill="#cbd5e1"/>'
    b += f'<rect x="35" y="-8" width="40" height="18" rx="4" fill="#475569"/></g>'
    return svg(800, 600, b, "Technician carrying out preventive maintenance on an electrical panel")


FILES = {
    "products/manual-phase-changeover.svg": p_manual_phase,
    "products/automatic-phase-changeover.svg": p_auto_phase,
    "products/single-phase-changeover.svg": p_single_phase,
    "products/three-phase-changeover.svg": p_three_phase,
    "products/eb-generator-changeover.svg": p_eb_dg,
    "products/distribution-board.svg": p_db,
    "products/mcb-mccb.svg": p_mcb_mccb,
    "products/contactor.svg": p_contactor,
    "products/industrial-switchgear.svg": p_industrial,
    "products/custom-panel.svg": p_custom_panel,
    "hero-changeover-panel.svg": hero,
    "about-technician.svg": about,
    "gallery/phase-changeover-eb-board.svg": g_eb_board,
    "gallery/eb-dg-changeover-panel.svg": g_eb_dg,
    "gallery/distribution-board-wiring.svg": g_db_wiring,
    "gallery/lt-panel-installation.svg": g_lt_panel,
    "gallery/pump-control-panel.svg": g_pump_panel,
    "gallery/preventive-maintenance.svg": g_maintenance,
}

if __name__ == "__main__":
    for rel, fn in FILES.items():
        out = ROOT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(fn())
        print("wrote", out.relative_to(ROOT.parent.parent))
