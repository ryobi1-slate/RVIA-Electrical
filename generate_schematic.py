#!/usr/bin/env python3
"""
Generate the Slate 2026 RV electrical one-line schematic as an
AutoCAD-ready ASCII DXF file and a companion SVG file.
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

SVG_STROKE = {
    "ELEC-DC":  "#c0392b",
    "ELEC-AC":  "#2c5aa0",
    "ELEC-GND": "#1e8449",
    "TEXT":     "#111111",
}

# ---------------------------------------------------------------------------
# Component definitions: key -> (label, x, y, w, h, layer)
# ---------------------------------------------------------------------------
COMPONENTS = {
    "SOLAR":   ("200W SOLAR PANEL",                         120, 1700, 220, 120, "ELEC-DC"),
    "B25A":    ("25A SOLAR INPUT\nPROTECTION",               420, 1720, 180, 80,  "ELEC-DC"),
    "DCDC":    ("DC-DC + MPPT",                              680, 1700, 220, 120, "ELEC-DC"),
    "B60A":    ("60A MAIN CHARGE\nPROTECTION",               980, 1720, 200, 80,  "ELEC-DC"),
    "B80A":    ("80A ALTERNATOR\nPROTECTION",                1260, 1720, 200, 80,  "ELEC-DC"),
    "CHASBAT": ("CHASSIS BATTERY",                          1540, 1700, 220, 120, "ELEC-DC"),
    "BAT":     ("12V 200Ah LiFePO4\nBATTERY (UL1973)",       640, 1300, 220, 160, "ELEC-DC"),
    "B200A":   ("200A BREAKER",                              940, 1400, 160, 60,  "ELEC-DC"),
    "SHUNT":   ("300A SHUNT",                                940, 1280, 160, 60,  "ELEC-DC"),
    "NBUS":    ("NEGATIVE BUS",                             1140, 1280, 180, 60,  "ELEC-DC"),
    "CHGND":   ("CHASSIS GROUND",                           1380, 1290, 180, 50,  "ELEC-GND"),
    "RGND":    ("REAR OEM GROUND",                          1380, 1210, 180, 50,  "ELEC-GND"),
    "DCDIST":  ("DC DISTRIBUTION\nPANEL",                   1640, 1350, 220, 140, "ELEC-DC"),
    "L_REF":   ("REFRIGERATOR (10A FUSE)",                  2200, 1790, 280, 50, "ELEC-DC"),
    "L_DH":    ("DIESEL HEATER (15A FUSE)",                 2200, 1690, 280, 50, "ELEC-DC"),
    "L_USBC":  ("USB-C 100W (15A FUSE)",                    2200, 1590, 280, 50, "ELEC-DC"),
    "L_UA1":   ("USB-A 1 (10A FUSE)",                       2200, 1490, 280, 50, "ELEC-DC"),
    "L_UA2":   ("USB-A 2 (10A FUSE)",                       2200, 1390, 280, 50, "ELEC-DC"),
    "L_S1":    ("12V POWER SOCKET 1 (15A FUSE)",            2200, 1290, 280, 50, "ELEC-DC"),
    "L_S2":    ("12V POWER SOCKET 2 (15A FUSE)",            2200, 1190, 280, 50, "ELEC-DC"),
    "L_RL":    ("READING LIGHTS (7.5A FUSE)",               2200, 1090, 280, 50, "ELEC-DC"),
    "L_PL":    ("CEILING PUCK LIGHTS (10A FUSE)",           2200,  990, 280, 50, "ELEC-DC"),
    "L_WP":    ("WATER PUMP (15A FUSE)",                    2200,  890, 280, 50, "ELEC-DC"),
    "L_F1":    ("FAN 1 (7.5A FUSE)",                        2200,  790, 280, 50, "ELEC-DC"),
    "L_F2":    ("FAN 2 (7.5A FUSE)",                        2200,  690, 280, 50, "ELEC-DC"),
    "SHORE":   ("SHORE INLET 30A",                           120,  400, 220, 100, "ELEC-AC"),
    "INV":     ("INVERTER + CHARGER\n2000W UL 458",          640,  300, 260, 220, "ELEC-AC"),
    "ACDIST":  ("AC DISTRIBUTION\nPANEL",                   1100,  360, 240, 180, "ELEC-AC"),
    "GFCI1":   ("GFCI 1 (15A BREAKER)",                     1500,  520, 240, 60,  "ELEC-AC"),
    "GFCI2":   ("GFCI 2 (15A BREAKER)",                     1500,  430, 240, 60,  "ELEC-AC"),
    "OPTAC":   ("OPT. AIR CONDITIONER",                     1500,  310, 240, 80,  "ELEC-AC"),
}

def edge(key, side):
    _label, x, y, w, h, _layer = COMPONENTS[key]
    if side == "left":   return (x, y + h / 2)
    if side == "right":  return (x + w, y + h / 2)
    if side == "top":    return (x + w/2, y + h)
    if side == "bottom": return (x + w/2, y)
    raise ValueError(side)

# ---------------------------------------------------------------------------
# Wires and Labeling
# ---------------------------------------------------------------------------
WIRES = []
# Use DXF Unicode escape sequence for the degree symbol to avoid encoding artifacts
WIRE_TEMP_RATING = "125\\U+00B0C"

def w(layer, label, *points):
    if label and ("AWG" in label or "/" in label):
        label = f"{label} {WIRE_TEMP_RATING}"
    WIRES.append((layer, label, list(points)))

# Charging chain
w("ELEC-DC", "6 AWG", edge("SOLAR","right"), edge("B25A","left"))
w("ELEC-DC", "6 AWG", edge("B25A","right"),  edge("DCDC","left"))
w("ELEC-DC", "4 AWG", edge("DCDC","right"),  edge("B60A","left"))
w("ELEC-DC", "4 AWG", edge("B60A","bottom"), (edge("B60A","bottom")[0], 1480), (edge("BAT","top")[0] + 70, 1480), (edge("BAT","top")[0] + 70, edge("BAT","top")[1]))
w("ELEC-DC", "4 AWG", edge("CHASBAT","left"), edge("B80A","right"))
w("ELEC-DC", "4 AWG", edge("B80A","top"), (edge("B80A","top")[0], 1870), (edge("DCDC","top")[0], 1870), edge("DCDC","top"))

# Main DC
w("ELEC-DC", "2/0 AWG", edge("BAT","top"), (edge("BAT","top")[0], 1540), (edge("B200A","top")[0], 1540), edge("B200A","top"))
w("ELEC-DC", "2/0 AWG", edge("B200A","right"), (1540, edge("B200A","right")[1]), (1540, 1430))
w("ELEC-DC", "2/0 AWG", (1540, 1430), (edge("DCDIST","left")[0], 1430), edge("DCDIST","left"))
w("ELEC-DC", "2/0 AWG", (1540, 1430), (1540, 560), (edge("INV","top")[0] + 40, 560), (edge("INV","top")[0] + 40, edge("INV","top")[1]))
w("ELEC-DC", "2/0 AWG", edge("BAT","bottom"), (edge("BAT","bottom")[0], 1240), (edge("SHUNT","bottom")[0], 1240), edge("SHUNT","bottom"))
w("ELEC-DC", None, edge("SHUNT","right"), edge("NBUS","left"))
w("ELEC-GND", "4 AWG", edge("NBUS","right"), edge("CHGND","left"))
w("ELEC-GND", "8 AWG", edge("CHGND","bottom"), (edge("CHGND","bottom")[0], edge("RGND","top")[1]), edge("RGND","top"))
w("ELEC-DC", "2/0 AWG", edge("NBUS","bottom"), (edge("NBUS","bottom")[0], 580), (edge("INV","top")[0] - 40, 580), (edge("INV","top")[0] - 40, edge("INV","top")[1]))

# DC Distribution
TRUNK_X = 2160
w("ELEC-DC", "2/0 AWG", edge("DCDIST","right"), (TRUNK_X, edge("DCDIST","right")[1]))
w("ELEC-DC", None, (TRUNK_X, 715), (TRUNK_X, 1815))

LOAD_WIRE = {"L_REF": "8 AWG", "L_DH": "SUPPLIED", "L_USBC": "12/2", "L_UA1": "14/2", "L_UA2": "14/2", "L_S1": "12/2", "L_S2": "12/2", "L_RL": "14/2", "L_PL": "14/2", "L_WP": "12/2", "L_F1": "14/2", "L_F2": "14/2"}
for k, v in LOAD_WIRE.items():
    lx, ly = edge(k, "left")
    w("ELEC-DC", v, (TRUNK_X, ly), (lx, ly))

# AC
w("ELEC-AC", "10/3", edge("SHORE","right"), (edge("INV","left")[0], edge("SHORE","right")[1]), edge("INV","left"))
w("ELEC-AC", "10/3", edge("INV","right"), edge("ACDIST","left"))
ac_trunk_x = edge("ACDIST","right")[0] + 40
w("ELEC-AC", None, edge("ACDIST","right"), (ac_trunk_x, edge("ACDIST","right")[1]))
for key in ("GFCI1", "GFCI2", "OPTAC"):
    lx, ly = edge(key, "left")
    w("ELEC-AC", "12/3", (ac_trunk_x, ly), (lx, ly))
w("ELEC-GND", "8 AWG", edge("RGND","left"), (edge("ACDIST","top")[0], edge("RGND","left")[1]), edge("ACDIST","top"))

# ---------------------------------------------------------------------------
# DXF / SVG Generation
# ---------------------------------------------------------------------------
def dxf_line(x1, y1, x2, y2, layer):
    return f"0\nLINE\n8\n{layer}\n10\n{x1:.3f}\n20\n{y1:.3f}\n30\n0.0\n11\n{x2:.3f}\n21\n{y2:.3f}\n31\n0.0\n"

def dxf_text(x, y, height, text, layer="TEXT"):
    return f"0\nTEXT\n8\n{layer}\n10\n{x:.3f}\n20\n{y:.3f}\n30\n0.0\n40\n{height:.2f}\n1\n{text}\n7\nSTANDARD\n"

def write_dxf(path):
    out = ["999\nSlate 2026 RV Electrical\n0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1009\n0\nENDSEC\n"]
    out.append("0\nSECTION\n2\nTABLES\n0\nTABLE\n2\nSTYLE\n70\n1\n0\nSTYLE\n2\nSTANDARD\n70\n0\n40\n0.0\n41\n1.0\n50\n0.0\n71\n0\n42\n2.5\n3\nArial\n4\n\n0\nENDTAB\n")
    out.append(f"0\nTABLE\n2\nLAYER\n70\n{len(LAYERS)}\n")
    for n, c in LAYERS.items(): out.append(f"0\nLAYER\n2\n{n}\n70\n0\n62\n{c}\n6\nCONTINUOUS\n")
    out.append("0\nENDTAB\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n")

    for k, (lab, x, y, wd, ht, lay) in COMPONENTS.items():
        for p in [(x,y,x+wd,y), (x+wd,y,x+wd,y+ht), (x+wd,y+ht,x,y+ht), (x,y+ht,x,y)]: out.append(dxf_line(p[0],p[1],p[2],p[3],lay))
        lines = lab.split("\n")
        sy = y + ht/2 + (len(lines)*14)/2 - 14
        for i, l in enumerate(lines): out.append(dxf_text(x+wd/2-(len(l)*3.2), sy-i*14, 11, l))

    for lay, lab, pts in WIRES:
        for p1, p2 in zip(pts[:-1], pts[1:]): out.append(dxf_line(p1[0],p1[1],p2[0],p2[1],lay))
        if lab:
            (x1, y1), (x2, y2) = pts[0], pts[1]
            tx, ty = ((x1+x2)/2-len(lab)*3, (y1+y2)/2+6) if y1==y2 else ((x1+x2)/2+6, (y1+y2)/2-5)
            out.append(dxf_text(tx, ty, 9, lab))

    out.append(dxf_text(120, 1920, 22, "SLATE 2026 RV - ELECTRICAL ONE-LINE SCHEMATIC"))
    out.append("0\nENDSEC\n0\nEOF\n")
    Path(path).write_text("".join(out))

def write_svg(path):
    CANVAS_H = 2000
    fy = lambda y: CANVAS_H - y
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2560 2000" font-family="Arial" font-size="11">\n<rect width="100%" height="100%" fill="white"/>\n']
    for lay, lab, pts in WIRES:
        p_str = " ".join(f"{x:.1f},{fy(y):.1f}" for x, y in pts)
        out.append(f'<polyline points="{p_str}" fill="none" stroke="{SVG_STROKE[lay]}" stroke-width="2"/>\n')
    for k, (lab, x, y, wd, ht, lay) in COMPONENTS.items():
        out.append(f'<rect x="{x}" y="{fy(y+ht)}" width="{wd}" height="{ht}" fill="none" stroke="{SVG_STROKE[lay]}" stroke-width="2"/>\n')
    out.append('</svg>')
    Path(path).write_text("".join(out))

if __name__ == "__main__":
    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)
    write_dxf(out_dir / "slate_electrical_schematic.dxf")
    write_svg(out_dir / "slate_electrical_schematic.svg")
    print(f"Generated files in {out_dir}")
