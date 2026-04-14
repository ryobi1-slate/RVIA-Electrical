#!/usr/bin/env python3
"""
Slate 2026 RV Electrical - Phase 1: Charging System Lock
Focus: Clean charging paths, alternator side-tap, and tightened naming.
"""

from pathlib import Path

LAYERS = {"ELEC-DC": 1, "ELEC-AC": 5, "ELEC-GND": 3, "TEXT": 7}

# ---------------------------------------------------------------------------
# Component definitions: key -> (label, x, y, w, h, layer)
# ---------------------------------------------------------------------------
COMPONENTS = {
    # Charging band (top) - Centered and spaced for "Engineered" look
    "SOLAR":   ("200W SOLAR PANEL",                120, 1700, 220, 120, "ELEC-DC"),
    "B25A":    ("25A SOLAR BREAKER",               440, 1720, 180, 80,  "ELEC-DC"),
    "DCDC":    ("DC-DC + MPPT\n(Solar + Alt Inputs)", 720, 1700, 240, 120, "ELEC-DC"),
    "B60A":    ("60A CHARGE BREAKER",              1060, 1720, 200, 80,  "ELEC-DC"),
    "B80A":    ("80A ALT BREAKER",                 1360, 1720, 180, 80,  "ELEC-DC"),
    "CHASBAT": ("CHASSIS BATTERY",                 1640, 1700, 220, 120, "ELEC-DC"),

    # Middle band - Initial Battery Placement
    "BAT":     ("12V 200Ah LiFePO4\nBATTERY (UL1973)", 730, 1300, 220, 160, "ELEC-DC"),
}

def edge(key, side):
    _l, x, y, w, h, _lay = COMPONENTS[key]
    if side == "left":   return (x, y + h / 2)
    if side == "right":  return (x + w, y + h / 2)
    if side == "top":    return (x + w/2, y + h)
    if side == "bottom": return (x + w/2, y)
    raise ValueError(side)

# ---------------------------------------------------------------------------
# Wires and Labeling
# ---------------------------------------------------------------------------
WIRES = []
WIRE_TEMP_RATING = "125\\U+00B0C"

def w(layer, label, *points):
    if label and ("AWG" in label or "/" in label):
        label = f"{label} {WIRE_TEMP_RATING}"
    WIRES.append((layer, label, list(points)))

# --- Charging Path logic ---------------------------------------------------

# Solar Inline Path
w("ELEC-DC", "6 AWG", edge("SOLAR","right"), edge("B25A","left"))
w("ELEC-DC", "6 AWG", edge("B25A","right"),  edge("DCDC","left"))

# Alternator Side-Tap (Non-Inline)
# Routes from Chassis Battery through 80A Breaker into TOP of DC-DC
w("ELEC-DC", "4 AWG", edge("CHASBAT","left"), edge("B80A","right"))
w("ELEC-DC", "4 AWG",
  edge("B80A","top"),
  (edge("B80A","top")[0], 1850),
  (edge("DCDC","top")[0], 1850),
  edge("DCDC","top"))

# Main Charge Output Path
w("ELEC-DC", "4 AWG", edge("DCDC","right"), edge("B60A","left"))

# Clear Vertical Drop to Battery
# Ties the charging system to the storage system definitively
w("ELEC-DC", "4 AWG",
  edge("B60A","bottom"),
  (edge("B60A","bottom")[0], 1550),
  (edge("BAT","top")[0] + 50, 1550),
  (edge("BAT","top")[0] + 50, edge("BAT","top")[1]))

# ---------------------------------------------------------------------------
# DXF Generation Logic
# ---------------------------------------------------------------------------
def dxf_line(x1, y1, x2, y2, layer):
    return f"0\nLINE\n8\n{layer}\n10\n{x1:.3f}\n20\n{y1:.3f}\n30\n0.0\n11\n{x2:.3f}\n21\n{y2:.3f}\n31\n0.0\n"

def dxf_text(x, y, height, text, layer="TEXT"):
    return f"0\nTEXT\n8\n{layer}\n10\n{x:.3f}\n20\n{y:.3f}\n30\n0.0\n40\n{height:.2f}\n1\n{text}\n7\nSTANDARD\n"

def write_dxf(path):
    out = ["999\nSlate 2026 RV Electrical\n0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1009\n0\nENDSEC\n"]
    # Table defines Standard Style as Arial with 0 height to prevent the "Giant Block" font issue
    out.append("0\nSECTION\n2\nTABLES\n0\nTABLE\n2\nSTYLE\n70\n1\n0\nSTYLE\n2\nSTANDARD\n70\n0\n40\n0.0\n41\n1.0\n50\n0.0\n71\n0\n42\n2.5\n3\nArial\n4\n\n0\nENDTAB\n")
    out.append(f"0\nTABLE\n2\nLAYER\n70\n{len(LAYERS)}\n")
    for n, c in LAYERS.items():
        out.append(f"0\nLAYER\n2\n{n}\n70\n0\n62\n{c}\n6\nCONTINUOUS\n")
    out.append("0\nENDTAB\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n")

    for k, (lab, x, y, wd, ht, lay) in COMPONENTS.items():
        # Draw Box
        for p in [(x, y, x + wd, y), (x + wd, y, x + wd, y + ht), (x + wd, y + ht, x, y + ht), (x, y + ht, x, y)]:
            out.append(dxf_line(p[0], p[1], p[2], p[3], lay))
        # Draw Centered Text
        lines = lab.split("\n")
        sy = y + ht/2 + (len(lines)*14)/2 - 14
        for i, l in enumerate(lines):
            # Approximate centering; consider DXF group codes 72/73 for true alignment
            tx = x + wd / 2 - (len(l) * 3.2)
            ty = sy - i * 14
            out.append(dxf_text(tx, ty, 11, l))

    for lay, lab, pts in WIRES:
        for p1, p2 in zip(pts[:-1], pts[1:]):
            out.append(dxf_line(p1[0], p1[1], p2[0], p2[1], lay))
        if lab:
            (x1, y1), (x2, y2) = pts[0], pts[1]
            if y1 == y2:
                tx = (x1 + x2) / 2 - len(lab) * 3.2
                ty = (y1 + y2) / 2 + 6
            else:
                tx = (x1 + x2) / 2 + 6
                ty = (y1 + y2) / 2 - 5
            out.append(dxf_text(tx, ty, 9, lab))

    out.append(dxf_text(120, 1950, 22, "SLATE 2026 RV - CHARGING SYSTEM (PHASE 1 LOCK)"))
    out.append("0\nENDSEC\n0\nEOF\n")
    Path(path).write_text("".join(out))

# ---------------------------------------------------------------------------
# SVG Generation Logic - kept in lockstep with the DXF for quick visual review
# ---------------------------------------------------------------------------
SVG_STROKE = {"ELEC-DC": "#c0392b", "ELEC-AC": "#2c5aa0", "ELEC-GND": "#1e8449", "TEXT": "#111111"}

def _svg_label(lab):
    # AutoCAD's \U+00B0 escape is for the DXF; convert back to a literal
    # degree glyph for the SVG so it renders directly in a browser.
    return lab.replace("\\U+00B0", "\u00b0") if lab else lab

def write_svg(path):
    CANVAS_W, CANVAS_H = 2560, 2000
    fy = lambda y: CANVAS_H - y
    out = ['<?xml version="1.0" encoding="UTF-8"?>\n']
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS_W} {CANVAS_H}" '
               f'font-family="Arial, Helvetica, sans-serif" font-size="11" stroke-linecap="square">\n')
    out.append('  <rect width="100%" height="100%" fill="white"/>\n')
    out.append(f'  <text x="120" y="{fy(1960)}" font-size="22" font-weight="bold" fill="#111">'
               f'SLATE 2026 RV &#8212; CHARGING SYSTEM (PHASE 1 LOCK)</text>\n')

    # Wires first so component rectangles sit on top
    for lay, lab, pts in WIRES:
        stroke = SVG_STROKE[lay]
        pts_str = " ".join(f"{x:.1f},{fy(y):.1f}" for x, y in pts)
        out.append(f'  <polyline points="{pts_str}" fill="none" stroke="{stroke}" stroke-width="2"/>\n')
        if lab:
            (x1, y1), (x2, y2) = pts[0], pts[1]
            mx, my = (x1+x2)/2, (y1+y2)/2
            tx, ty, anchor = (mx, my+12, "middle") if y1 == y2 else (mx+6, my, "start")
            out.append(f'  <text x="{tx:.1f}" y="{fy(ty):.1f}" text-anchor="{anchor}" '
                       f'fill="#333" font-size="10">{_svg_label(lab)}</text>\n')

    # Components
    for k, (lab, x, y, wd, ht, lay) in COMPONENTS.items():
        stroke = SVG_STROKE[lay]
        out.append(f'  <rect x="{x:.1f}" y="{fy(y+ht):.1f}" width="{wd:.1f}" height="{ht:.1f}" '
                   f'fill="white" stroke="{stroke}" stroke-width="2"/>\n')
        lines = lab.split("\n")
        sy = y + ht/2 + (len(lines)*14)/2 - 14
        for i, l in enumerate(lines):
            out.append(f'  <text x="{x+wd/2:.1f}" y="{fy(sy-i*14):.1f}" text-anchor="middle" '
                       f'fill="#111">{l}</text>\n')

    out.append('</svg>\n')
    Path(path).write_text("".join(out))

if __name__ == "__main__":
    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)
    write_dxf(out_dir / "slate_electrical_schematic.dxf")
    write_svg(out_dir / "slate_electrical_schematic.svg")
    print(f"Phase 1 Schematic Generated in {out_dir}")
