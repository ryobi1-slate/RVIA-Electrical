#!/usr/bin/env python3
"""
Generate the Slate 2026 RV electrical one-line schematic as an
AutoCAD-ready ASCII DXF file and a companion SVG file.

Geometry is intentionally simple: rectangles, straight lines, and text,
all orthogonal. Layout follows system-spec.md bands:
  - Top band:    charging sources
  - Middle band: battery and main DC protection
  - Right band:  DC distribution panel and DC loads
  - Bottom band: AC distribution and AC loads
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Layer definitions (ACI color numbers)
# ---------------------------------------------------------------------------
LAYERS = {
    "ELEC-DC":  1,   # red
    "ELEC-AC":  5,   # blue
    "ELEC-GND": 3,   # green
    "TEXT":     7,   # white/black (auto)
}

# SVG stroke colors per layer
SVG_STROKE = {
    "ELEC-DC":  "#c0392b",   # red
    "ELEC-AC":  "#2c5aa0",   # blue
    "ELEC-GND": "#1e8449",   # green
    "TEXT":     "#111111",
}

# ---------------------------------------------------------------------------
# Component definitions: key -> (label, x, y, w, h, layer)
# (x, y) is the lower-left corner in drawing units.
# ---------------------------------------------------------------------------
COMPONENTS = {
    # Charging band (top)
    "SOLAR":  ("200W SOLAR PANEL",                         120, 1700, 220, 120, "ELEC-DC"),
    "B25A":   ("25A SOLAR INPUT\nPROTECTION",              420, 1720, 180, 80,  "ELEC-DC"),
    "DCDC":   ("DC-DC + MPPT",                             680, 1700, 220, 120, "ELEC-DC"),
    "B60A":   ("60A MAIN CHARGE\nPROTECTION",              980, 1720, 200, 80,  "ELEC-DC"),
    "B80A":   ("80A ALTERNATOR\nPROTECTION",              1260, 1720, 200, 80,  "ELEC-DC"),
    "CHASBAT":("CHASSIS BATTERY",                         1540, 1700, 220, 120, "ELEC-DC"),

    # Main DC (middle band)
    "BAT":    ("12V 200Ah LiFePO4\nBATTERY (UL1973)",      640, 1300, 220, 160, "ELEC-DC"),
    "B200A":  ("200A BREAKER",                             940, 1400, 160, 60,  "ELEC-DC"),
    "SHUNT":  ("300A SHUNT",                               940, 1280, 160, 60,  "ELEC-DC"),
    "NBUS":   ("NEGATIVE BUS",                            1140, 1280, 180, 60,  "ELEC-DC"),

    # Grounds
    "CHGND":  ("CHASSIS GROUND",                          1380, 1290, 180, 50,  "ELEC-GND"),
    "RGND":   ("REAR OEM GROUND",                         1380, 1210, 180, 50,  "ELEC-GND"),

    # DC distribution
    "DCDIST": ("DC DISTRIBUTION\nPANEL",                  1640, 1350, 220, 140, "ELEC-DC"),

    # DC loads (right-side vertical stack)
    "L_REF":  ("REFRIGERATOR (10A FUSE)",                 2200, 1790, 280, 50, "ELEC-DC"),
    "L_DH":   ("DIESEL HEATER (15A FUSE)",                2200, 1690, 280, 50, "ELEC-DC"),
    "L_USBC": ("USB-C 100W (15A FUSE)",                   2200, 1590, 280, 50, "ELEC-DC"),
    "L_UA1":  ("USB-A 1 (10A FUSE)",                      2200, 1490, 280, 50, "ELEC-DC"),
    "L_UA2":  ("USB-A 2 (10A FUSE)",                      2200, 1390, 280, 50, "ELEC-DC"),
    "L_S1":   ("12V POWER SOCKET 1 (15A FUSE)",           2200, 1290, 280, 50, "ELEC-DC"),
    "L_S2":   ("12V POWER SOCKET 2 (15A FUSE)",           2200, 1190, 280, 50, "ELEC-DC"),
    "L_RL":   ("READING LIGHTS (7.5A FUSE)",              2200, 1090, 280, 50, "ELEC-DC"),
    "L_PL":   ("CEILING PUCK LIGHTS (10A FUSE)",          2200,  990, 280, 50, "ELEC-DC"),
    "L_WP":   ("WATER PUMP (15A FUSE)",                   2200,  890, 280, 50, "ELEC-DC"),
    "L_F1":   ("FAN 1 (7.5A FUSE)",                       2200,  790, 280, 50, "ELEC-DC"),
    "L_F2":   ("FAN 2 (7.5A FUSE)",                       2200,  690, 280, 50, "ELEC-DC"),

    # AC (bottom band)
    "SHORE":  ("SHORE INLET 30A",                          120,  400, 220, 100, "ELEC-AC"),
    "INV":    ("INVERTER + CHARGER\n+ TRANSFER SWITCH\n2000W PASS-THRU\nUL 458",
                                                           640,  300, 260, 220, "ELEC-AC"),
    "ACDIST": ("AC DISTRIBUTION\nPANEL (UL LISTED)",      1100,  360, 240, 180, "ELEC-AC"),
    "GFCI1":  ("GFCI 1 (15A BREAKER)",                    1500,  520, 240, 60,  "ELEC-AC"),
    "GFCI2":  ("GFCI 2 (15A BREAKER)",                    1500,  430, 240, 60,  "ELEC-AC"),
    "OPTAC":  ("OPT. AIR CONDITIONER\n(20A BREAKER)",     1500,  310, 240, 80,  "ELEC-AC"),
}


def edge(key, side):
    """Return (x, y) of the midpoint of a component edge."""
    _label, x, y, w, h, _layer = COMPONENTS[key]
    if side == "left":   return (x,       y + h / 2)
    if side == "right":  return (x + w,   y + h / 2)
    if side == "top":    return (x + w/2, y + h)
    if side == "bottom": return (x + w/2, y)
    raise ValueError(side)


def pt(key, side, offset_along=0, offset_out=0):
    """Edge point with optional offsets along or perpendicular to the edge."""
    _label, x, y, w, h, _layer = COMPONENTS[key]
    if side == "left":
        return (x - offset_out, y + h / 2 + offset_along)
    if side == "right":
        return (x + w + offset_out, y + h / 2 + offset_along)
    if side == "top":
        return (x + w / 2 + offset_along, y + h + offset_out)
    if side == "bottom":
        return (x + w / 2 + offset_along, y - offset_out)
    raise ValueError(side)


# ---------------------------------------------------------------------------
# Wires: list of polylines. Each is (layer, label, [(x,y), (x,y), ...]).
# Label is drawn at midpoint of the first segment.
# All segments are strictly horizontal or vertical.
# ---------------------------------------------------------------------------
WIRES = []

# Marine-grade tinned copper conductors on this build are specified with a
# 125°C insulation rating (per the conductor schedule in the BOM). Append
# the rating to every AWG / cable-size callout so it prints on the TEXT
# layer alongside the wire size.
WIRE_TEMP_RATING = "125°C"


def w(layer, label, *points):
    if label and ("AWG" in label or "/" in label):
        label = f"{label} {WIRE_TEMP_RATING}"
    WIRES.append((layer, label, list(points)))

# --- Charging chain (top band) ------------------------------------------------
w("ELEC-DC", "6 AWG",
  edge("SOLAR","right"), edge("B25A","left"))
w("ELEC-DC", "6 AWG",
  edge("B25A","right"),  edge("DCDC","left"))
w("ELEC-DC", "4 AWG",
  edge("DCDC","right"),  edge("B60A","left"))

# 60A breaker -> down -> battery top positive terminal (rail at y=1480)
w("ELEC-DC", "4 AWG",
  edge("B60A","bottom"),
  (edge("B60A","bottom")[0], 1480),
  (edge("BAT","top")[0] + 70, 1480),
  (edge("BAT","top")[0] + 70, edge("BAT","top")[1]))

# Chassis Battery -> 80A Alternator Protection (4 AWG input tap)
w("ELEC-DC", "4 AWG",
  edge("CHASBAT","left"), edge("B80A","right"))

# 80A Alternator Protection -> up and over into DC-DC + MPPT top
# (alternator-charging input to the DC-DC charger). Routed above the
# top-band rectangles to avoid crossing the DCDC and B60A boxes.
w("ELEC-DC", "4 AWG",
  edge("B80A","top"),
  (edge("B80A","top")[0], 1870),
  (edge("DCDC","top")[0], 1870),
  edge("DCDC","top"))

# --- Battery / main DC bus (middle band) -------------------------------------
# Battery + (top-left area of battery) -> 200A breaker -> main positive rail
w("ELEC-DC", "2/0 AWG",
  edge("BAT","top"),
  (edge("BAT","top")[0], 1540),
  (edge("B200A","top")[0], 1540),
  edge("B200A","top"))

# 200A breaker right -> main + rail (virtual node at x=1540, y=1430)
w("ELEC-DC", "2/0 AWG",
  edge("B200A","right"),
  (1540, edge("B200A","right")[1]),
  (1540, 1430))

# Main + rail feeds DC Distribution panel (left-middle)
w("ELEC-DC", "2/0 AWG",
  (1540, 1430),
  (edge("DCDIST","left")[0], 1430),
  edge("DCDIST","left"))

# Main + rail feeds Inverter DC+ input (drop down into inverter top)
w("ELEC-DC", "2/0 AWG",
  (1540, 1430),
  (1540, 560),
  (edge("INV","top")[0] + 40, 560),
  (edge("INV","top")[0] + 40, edge("INV","top")[1]))

# Battery - (bottom) -> shunt -> negative bus
w("ELEC-DC", "2/0 AWG",
  edge("BAT","bottom"),
  (edge("BAT","bottom")[0], 1240),
  (edge("SHUNT","bottom")[0], 1240),
  edge("SHUNT","bottom"))
w("ELEC-DC", None,
  edge("SHUNT","right"), edge("NBUS","left"))

# Negative bus -> chassis ground (ground layer)
w("ELEC-GND", "4 AWG",
  edge("NBUS","right"), edge("CHGND","left"))
# Chassis -> rear OEM ground
w("ELEC-GND", "8 AWG",
  edge("CHGND","bottom"),
  (edge("CHGND","bottom")[0], edge("RGND","top")[1]),
  edge("RGND","top"))

# Negative bus -> down to inverter DC-
w("ELEC-DC", "2/0 AWG",
  edge("NBUS","bottom"),
  (edge("NBUS","bottom")[0], 580),
  (edge("INV","top")[0] - 40, 580),
  (edge("INV","top")[0] - 40, edge("INV","top")[1]))

# --- DC Distribution -> loads ------------------------------------------------
# Trunk: from DC Dist right edge, run east, then a vertical trunk at x=2160
# that each load taps into.
TRUNK_X = 2160
trunk_bottom = 690 + 25   # Fan 2 midline
trunk_top    = 1790 + 25  # Refrigerator midline

# Horizontal feed from DC Dist right edge to the trunk (entry point at y=1420)
w("ELEC-DC", "2/0 AWG",
  edge("DCDIST","right"),
  (TRUNK_X, edge("DCDIST","right")[1]))

# Vertical trunk
w("ELEC-DC", None,
  (TRUNK_X, trunk_bottom),
  (TRUNK_X, trunk_top))

# Individual load taps with implicit wire sizes per load
LOAD_WIRE = {
    "L_REF":  "8 AWG",
    "L_DH":   "SUPPLIED WIRE",
    "L_USBC": "12/2",
    "L_UA1":  "14/2",
    "L_UA2":  "14/2",
    "L_S1":   "12/2",
    "L_S2":   "12/2",
    "L_RL":   "14/2",
    "L_PL":   "14/2",
    "L_WP":   "12/2",
    "L_F1":   "14/2",
    "L_F2":   "14/2",
}
for key, wire_size in LOAD_WIRE.items():
    lx, ly = edge(key, "left")
    w("ELEC-DC", wire_size, (TRUNK_X, ly), (lx, ly))

# --- AC branch (bottom) ------------------------------------------------------
w("ELEC-AC", "10/3",
  edge("SHORE","right"),
  (edge("INV","left")[0], edge("SHORE","right")[1]),
  edge("INV","left"))

w("ELEC-AC", "10/3",
  edge("INV","right"),
  edge("ACDIST","left"))

# AC Dist -> AC branch circuits; vertical taps at x = ACDIST right + 20
ac_trunk_x = edge("ACDIST","right")[0] + 40
w("ELEC-AC", None,
  edge("ACDIST","right"),
  (ac_trunk_x, edge("ACDIST","right")[1]))

w("ELEC-AC", None,
  (ac_trunk_x, edge("OPTAC","left")[1]),
  (ac_trunk_x, edge("GFCI1","left")[1]))

for key in ("GFCI1", "GFCI2", "OPTAC"):
    lx, ly = edge(key, "left")
    w("ELEC-AC", "12/3", (ac_trunk_x, ly), (lx, ly))

# Rear OEM Ground bonds to AC Distribution Panel (8 AWG green)
w("ELEC-GND", "8 AWG",
  edge("RGND","left"),
  (edge("ACDIST","top")[0], edge("RGND","left")[1]),
  edge("ACDIST","top"))


# ---------------------------------------------------------------------------
# DXF writer (ASCII R12-compatible, minimal)
# ---------------------------------------------------------------------------
def dxf_line(x1, y1, x2, y2, layer):
    return ("0\nLINE\n"
            f"8\n{layer}\n"
            f"10\n{x1:.3f}\n20\n{y1:.3f}\n30\n0.0\n"
            f"11\n{x2:.3f}\n21\n{y2:.3f}\n31\n0.0\n")


def dxf_text(x, y, height, text, layer="TEXT"):
    # DXF TEXT uses group 1 for content, 40 for height
    return ("0\nTEXT\n"
            f"8\n{layer}\n"
            f"10\n{x:.3f}\n20\n{y:.3f}\n30\n0.0\n"
            f"40\n{height:.2f}\n"
            f"1\n{text}\n"
            f"7\nSTANDARD\n")


def write_dxf(path):
    out = []
    # HEADER
    out.append("999\nSlate 2026 RV Electrical Schematic\n")
    out.append("0\nSECTION\n2\nHEADER\n")
    out.append("9\n$ACADVER\n1\nAC1009\n")   # R12
    out.append("9\n$INSBASE\n10\n0.0\n20\n0.0\n30\n0.0\n")
    out.append("9\n$EXTMIN\n10\n0.0\n20\n0.0\n30\n0.0\n")
    out.append("9\n$EXTMAX\n10\n3000.0\n20\n2000.0\n30\n0.0\n")
    out.append("0\nENDSEC\n")

    # TABLES: LAYER + STYLE
    out.append("0\nSECTION\n2\nTABLES\n")
    # STYLE table (one default STANDARD style)
    out.append("0\nTABLE\n2\nSTYLE\n70\n1\n")
    out.append("0\nSTYLE\n2\nSTANDARD\n70\n0\n40\n0.0\n41\n1.0\n50\n0.0\n71\n0\n42\n2.5\n3\ntxt\n4\n\n")
    out.append("0\nENDTAB\n")
    # LAYER table
    out.append(f"0\nTABLE\n2\nLAYER\n70\n{len(LAYERS)}\n")
    for name, color in LAYERS.items():
        out.append(f"0\nLAYER\n2\n{name}\n70\n0\n62\n{color}\n6\nCONTINUOUS\n")
    out.append("0\nENDTAB\n")
    out.append("0\nENDSEC\n")

    # ENTITIES
    out.append("0\nSECTION\n2\nENTITIES\n")

    # Component rectangles + labels
    for key, (label, x, y, wd, ht, layer) in COMPONENTS.items():
        # 4 sides of rectangle
        out.append(dxf_line(x,      y,      x + wd, y,       layer))
        out.append(dxf_line(x + wd, y,      x + wd, y + ht,  layer))
        out.append(dxf_line(x + wd, y + ht, x,      y + ht,  layer))
        out.append(dxf_line(x,      y + ht, x,      y,       layer))
        # Label text - one TEXT entity per line, stacked top-down inside the box
        lines = label.split("\n")
        line_h = 14
        total_h = len(lines) * line_h
        start_y = y + ht/2 + total_h/2 - line_h  # baseline of first line
        for i, line in enumerate(lines):
            # center horizontally: approximate by offsetting left from center
            approx_width = len(line) * 6.5
            tx = x + wd/2 - approx_width/2
            ty = start_y - i * line_h
            out.append(dxf_text(tx, ty, 11, line, "TEXT"))

    # Wires + wire labels
    for layer, label, points in WIRES:
        for (x1, y1), (x2, y2) in zip(points[:-1], points[1:]):
            out.append(dxf_line(x1, y1, x2, y2, layer))
        if label:
            (x1, y1), (x2, y2) = points[0], points[1]
            # midpoint of first segment
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            # offset label slightly above horizontal runs, right of vertical runs
            if y1 == y2:
                tx = mx - len(label) * 3
                ty = my + 6
            else:
                tx = mx + 6
                ty = my - 5
            out.append(dxf_text(tx, ty, 9, label, "TEXT"))

    # Title block text (simple)
    out.append(dxf_text(120, 1920, 22, "SLATE 2026 RV - ELECTRICAL ONE-LINE SCHEMATIC", "TEXT"))
    out.append(dxf_text(120, 1890, 11, "One-line schematic. Not a physical installation layout.", "TEXT"))
    out.append(dxf_text(120, 1870, 11, "Layers: ELEC-DC (red), ELEC-AC (blue), ELEC-GND (green), TEXT.", "TEXT"))

    out.append("0\nENDSEC\n")
    out.append("0\nEOF\n")

    Path(path).write_text("".join(out))


# ---------------------------------------------------------------------------
# SVG writer
# ---------------------------------------------------------------------------
def write_svg(path):
    # SVG uses top-left origin and y-down. Flip y by using overall height.
    CANVAS_W, CANVAS_H = 2560, 2000
    MARGIN = 20

    def fy(y):
        return CANVAS_H - y

    out = []
    out.append(f'<?xml version="1.0" encoding="UTF-8"?>\n')
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" '
               f'font-family="Helvetica, Arial, sans-serif" '
               f'font-size="11" stroke-linecap="square">\n')
    out.append('  <rect width="100%" height="100%" fill="white"/>\n')

    # Title
    out.append(f'  <text x="120" y="{fy(1940)}" font-size="22" font-weight="bold" '
               f'fill="#111">SLATE 2026 RV — ELECTRICAL ONE-LINE SCHEMATIC</text>\n')
    out.append(f'  <text x="120" y="{fy(1915)}" font-size="11" fill="#555">'
               f'One-line schematic. Not a physical installation layout.</text>\n')
    out.append(f'  <text x="120" y="{fy(1895)}" font-size="11" fill="#555">'
               f'Layers: ELEC-DC (red)  ELEC-AC (blue)  ELEC-GND (green)  TEXT</text>\n')

    # Wires first (so component rectangles sit above them)
    for layer, label, points in WIRES:
        stroke = SVG_STROKE[layer]
        # polyline
        pts_str = " ".join(f"{x:.1f},{fy(y):.1f}" for x, y in points)
        out.append(f'  <polyline points="{pts_str}" fill="none" stroke="{stroke}" stroke-width="2"/>\n')
        if label:
            (x1, y1), (x2, y2) = points[0], points[1]
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            if y1 == y2:
                tx, ty = mx, my + 12
                anchor = "middle"
            else:
                tx, ty = mx + 6, my
                anchor = "start"
            out.append(f'  <text x="{tx:.1f}" y="{fy(ty):.1f}" '
                       f'text-anchor="{anchor}" fill="#333" font-size="10">{label}</text>\n')

    # Components: rectangles + labels
    for key, (label, x, y, wd, ht, layer) in COMPONENTS.items():
        stroke = SVG_STROKE[layer]
        out.append(f'  <rect x="{x:.1f}" y="{fy(y+ht):.1f}" width="{wd:.1f}" height="{ht:.1f}" '
                   f'fill="white" stroke="{stroke}" stroke-width="2"/>\n')
        lines = label.split("\n")
        line_h = 14
        total_h = len(lines) * line_h
        start_y = y + ht/2 + total_h/2 - line_h
        for i, line in enumerate(lines):
            tx = x + wd/2
            ty = start_y - i * line_h
            out.append(f'  <text x="{tx:.1f}" y="{fy(ty):.1f}" text-anchor="middle" '
                       f'fill="#111">{line}</text>\n')

    out.append('</svg>\n')
    Path(path).write_text("".join(out))


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)
    write_dxf(out_dir / "slate_electrical_schematic.dxf")
    write_svg(out_dir / "slate_electrical_schematic.svg")
    print("Generated:")
    print(f"  {out_dir / 'slate_electrical_schematic.dxf'}")
    print(f"  {out_dir / 'slate_electrical_schematic.svg'}")
