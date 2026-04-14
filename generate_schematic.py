#!/usr/bin/env python3
"""
Slate 2026 RV Electrical - Phase 1: Charging System Lock

Purpose:
- Generate a clean first-pass DXF and SVG for the charging system section
- Keep geometry simple and AutoCAD-friendly
- Run a basic compliance document audit after generation

Outputs:
- output/slate_electrical_schematic.dxf
- output/slate_electrical_schematic.svg

Notes:
- This is a schematic, not a physical installation layout
- Focus is the charging system row plus initial battery tie-in
"""

from pathlib import Path

# -----------------------------------------------------------------------------
# Layer setup
# -----------------------------------------------------------------------------
LAYERS = {
    "ELEC-DC": 1,   # red
    "ELEC-AC": 5,   # blue
    "ELEC-GND": 3,  # green
    "TEXT": 7,      # white
}

SVG_STROKE = {
    "ELEC-DC": "#c0392b",
    "ELEC-AC": "#2c5aa0",
    "ELEC-GND": "#1e8449",
    "TEXT": "#111111",
}

WIRE_TEMP_RATING = "125\\U+00B0C"  # DXF-safe degree symbol escape


# -----------------------------------------------------------------------------
# Component definitions
# key -> (label, x, y, width, height, layer)
# -----------------------------------------------------------------------------
COMPONENTS = {
    # Top charging band
    "SOLAR": (
        "200W SOLAR PANEL",
        120, 1700, 220, 120, "ELEC-DC"
    ),
    "B25A": (
        "25A SOLAR BREAKER",
        440, 1720, 180, 80, "ELEC-DC"
    ),
    "DCDC": (
        "DC-DC + MPPT\n(Solar + Alt Inputs)",
        720, 1700, 240, 120, "ELEC-DC"
    ),
    "B60A": (
        "60A CHARGE BREAKER",
        1060, 1720, 200, 80, "ELEC-DC"
    ),
    "B80A": (
        "80A ALT BREAKER",
        1360, 1720, 180, 80, "ELEC-DC"
    ),
    "CHASBAT": (
        "CHASSIS BATTERY",
        1640, 1700, 220, 120, "ELEC-DC"
    ),

    # Middle band
    "BAT": (
        "12V 200Ah LiFePO4\nBATTERY (UL1973)",
        730, 1300, 220, 160, "ELEC-DC"
    ),

    # Phase 2 — distribution below house battery
    # BAT right edge x=950, BAT left edge x=730
    # B200A: positive side — center x = BAT right edge = 950
    "B200A": (
        "200A MAIN BREAKER",
        850, 1140, 200, 80, "ELEC-DC"
    ),
    # SHUNT: negative side — center x = BAT left edge = 730
    "SHUNT": (
        "300A SHUNT",
        650, 1160, 160, 60, "ELEC-DC"
    ),
    # POSBUS: center x = 950 (aligned with B200A), 60px gap from NEGBUS right
    "POSBUS": (
        "POSITIVE BUS",
        870, 1020, 160, 40, "ELEC-DC"
    ),
    # NEGBUS: center x = 730 (aligned with SHUNT)
    "NEGBUS": (
        "NEGATIVE BUS",
        650, 1020, 160, 40, "ELEC-DC"
    ),
    # CHASGRND: center x = 730 (aligned with NEGBUS)
    "CHASGRND": (
        "CHASSIS GROUND",
        670, 880, 120, 60, "ELEC-GND"
    ),
}


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def edge(key: str, side: str) -> tuple[float, float]:
    """Return a component connection point."""
    _label, x, y, w, h, _layer = COMPONENTS[key]

    if side == "left":
        return (x, y + h / 2)
    if side == "right":
        return (x + w, y + h / 2)
    if side == "top":
        return (x + w / 2, y + h)
    if side == "bottom":
        return (x + w / 2, y)
    raise ValueError(f"Unknown side: {side}")


WIRES: list[tuple[str, str | None, list[tuple[float, float]]]] = []


def add_wire(layer: str, label: str | None, *points: tuple[float, float]) -> None:
    """
    Store a wire path.
    Adds temperature rating to AWG labels automatically.
    """
    final_label = label
    if final_label and ("AWG" in final_label or "/" in final_label):
        final_label = f"{final_label} {WIRE_TEMP_RATING}"
    WIRES.append((layer, final_label, list(points)))


def build_wires() -> None:
    """Populate the charging system wire geometry."""
    WIRES.clear()

    # Solar inline path
    add_wire("ELEC-DC", "6 AWG", edge("SOLAR", "right"), edge("B25A", "left"))
    add_wire("ELEC-DC", "6 AWG", edge("B25A", "right"), edge("DCDC", "left"))

    # Alternator side input path
    # Chassis Battery -> 80A Breaker -> top entry into DC-DC
    add_wire("ELEC-DC", "4 AWG", edge("CHASBAT", "left"), edge("B80A", "right"))
    add_wire(
        "ELEC-DC",
        "4 AWG",
        edge("B80A", "top"),
        (edge("B80A", "top")[0], 1850),
        (edge("DCDC", "top")[0], 1850),
        edge("DCDC", "top"),
    )

    # Main charge output path
    add_wire("ELEC-DC", "4 AWG", edge("DCDC", "right"), edge("B60A", "left"))

    # Vertical drop from charge breaker to house battery
    bat_top = edge("BAT", "top")
    b60_bottom = edge("B60A", "bottom")
    add_wire(
        "ELEC-DC",
        "4 AWG",
        b60_bottom,
        (b60_bottom[0], 1550),
        (bat_top[0] + 50, 1550),
        (bat_top[0] + 50, bat_top[1]),
    )

    # Phase 2 — distribution wiring below house battery
    # BAT right → 200A main breaker (positive side), center x = 1270
    add_wire("ELEC-DC", "2/0 AWG", edge("BAT", "right"), edge("B200A", "top"))
    # BAT left → 300A shunt (negative side), center x = 1050
    add_wire("ELEC-DC", "2/0 AWG", edge("BAT", "left"), edge("SHUNT", "top"))
    # 200A breaker → positive bus
    add_wire("ELEC-DC", "2/0 AWG", edge("B200A", "bottom"), edge("POSBUS", "top"))
    # Shunt → negative bus
    add_wire("ELEC-DC", "2/0 AWG", edge("SHUNT", "bottom"), edge("NEGBUS", "top"))
    # Negative bus → chassis ground
    add_wire("ELEC-GND", "2/0 AWG", edge("NEGBUS", "bottom"), edge("CHASGRND", "top"))


# -----------------------------------------------------------------------------
# DXF generation
# -----------------------------------------------------------------------------
def dxf_line(x1: float, y1: float, x2: float, y2: float, layer: str) -> str:
    return (
        f"0\nLINE\n8\n{layer}\n"
        f"10\n{x1:.3f}\n20\n{y1:.3f}\n30\n0.0\n"
        f"11\n{x2:.3f}\n21\n{y2:.3f}\n31\n0.0\n"
    )


def dxf_text(x: float, y: float, height: float, text: str, layer: str = "TEXT") -> str:
    safe_text = text.replace("&", "+")
    return (
        f"0\nTEXT\n8\n{layer}\n"
        f"10\n{x:.3f}\n20\n{y:.3f}\n30\n0.0\n"
        f"40\n{height:.2f}\n1\n{safe_text}\n7\nSTANDARD\n"
    )


def write_dxf(path: Path) -> None:
    out: list[str] = []

    # Header
    out.append("999\nSlate 2026 RV Electrical\n")
    out.append("0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1009\n0\nENDSEC\n")

    # Tables: text style + layers
    out.append("0\nSECTION\n2\nTABLES\n")
    out.append(
        "0\nTABLE\n2\nSTYLE\n70\n1\n"
        "0\nSTYLE\n2\nSTANDARD\n70\n0\n40\n0.0\n41\n1.0\n50\n0.0\n"
        "71\n0\n42\n2.5\n3\nArial\n4\n\n0\nENDTAB\n"
    )
    out.append(f"0\nTABLE\n2\nLAYER\n70\n{len(LAYERS)}\n")
    for name, color in LAYERS.items():
        out.append(f"0\nLAYER\n2\n{name}\n70\n0\n62\n{color}\n6\nCONTINUOUS\n")
    out.append("0\nENDTAB\n0\nENDSEC\n")

    # Entities
    out.append("0\nSECTION\n2\nENTITIES\n")

    # Draw components
    for _key, (label, x, y, w, h, layer) in COMPONENTS.items():
        # rectangle
        out.append(dxf_line(x, y, x + w, y, layer))
        out.append(dxf_line(x + w, y, x + w, y + h, layer))
        out.append(dxf_line(x + w, y + h, x, y + h, layer))
        out.append(dxf_line(x, y + h, x, y, layer))

        # centered text (approximate)
        lines = label.split("\n")
        start_y = y + h / 2 + (len(lines) * 14) / 2 - 14
        for i, line in enumerate(lines):
            tx = x + w / 2 - (len(line) * 3.2)
            ty = start_y - i * 14
            out.append(dxf_text(tx, ty, 11, line))

    # Draw wires and labels
    for layer, label, pts in WIRES:
        for p1, p2 in zip(pts[:-1], pts[1:]):
            out.append(dxf_line(p1[0], p1[1], p2[0], p2[1], layer))

        if label and len(pts) >= 2:
            (x1, y1), (x2, y2) = pts[0], pts[1]
            if y1 == y2:
                tx = (x1 + x2) / 2 - len(label) * 3.2
                ty = y1 + 10
            else:
                tx = x1 + 6
                ty = (y1 + y2) / 2
            out.append(dxf_text(tx, ty, 9, label))

    # Title + notes
    out.append(dxf_text(120, 1950, 22, "SLATE 2026 RV - CHARGING SYSTEM (PHASE 1 LOCK)"))
    out.append(dxf_text(120, 1915, 12, "One-line schematic. Not a physical installation layout."))
    out.append(dxf_text(120, 1890, 12, "Layers: ELEC-DC (red), ELEC-AC (blue), ELEC-GND (green), TEXT."))

    out.append("0\nENDSEC\n0\nEOF\n")
    path.write_text("".join(out), encoding="utf-8")


# -----------------------------------------------------------------------------
# SVG generation
# -----------------------------------------------------------------------------
def _svg_label(label: str | None) -> str:
    if not label:
        return ""
    return label.replace("\\U+00B0", "\u00b0")


def write_svg(path: Path) -> None:
    canvas_w, canvas_h = 2560, 2000

    def flip_y(y: float) -> float:
        return canvas_h - y

    out: list[str] = []
    out.append('<?xml version="1.0" encoding="UTF-8"?>\n')
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas_w} {canvas_h}" '
        f'font-family="Arial, Helvetica, sans-serif" font-size="11" stroke-linecap="square">\n'
    )
    out.append('  <rect width="100%" height="100%" fill="white"/>\n')
    out.append(
        f'  <text x="120" y="{flip_y(1960):.1f}" font-size="22" font-weight="bold" fill="#111">'
        f'SLATE 2026 RV &#8212; CHARGING SYSTEM (PHASE 1 LOCK)</text>\n'
    )
    out.append(
        f'  <text x="120" y="{flip_y(1915):.1f}" font-size="12" fill="#333">'
        f'One-line schematic. Not a physical installation layout.</text>\n'
    )
    out.append(
        f'  <text x="120" y="{flip_y(1890):.1f}" font-size="12" fill="#333">'
        f'Layers: ELEC-DC (red), ELEC-AC (blue), ELEC-GND (green), TEXT.</text>\n'
    )

    # wires first
    for layer, label, pts in WIRES:
        stroke = SVG_STROKE[layer]
        points = " ".join(f"{x:.1f},{flip_y(y):.1f}" for x, y in pts)
        out.append(
            f'  <polyline points="{points}" fill="none" stroke="{stroke}" stroke-width="2"/>\n'
        )

        if label and len(pts) >= 2:
            (x1, y1), (x2, y2) = pts[0], pts[1]
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            if y1 == y2:
                tx, ty, anchor = mx, my + 12, "middle"
            else:
                tx, ty, anchor = x1 + 8, my, "start"

            out.append(
                f'  <text x="{tx:.1f}" y="{flip_y(ty):.1f}" text-anchor="{anchor}" '
                f'fill="#333" font-size="10">{_svg_label(label)}</text>\n'
            )

    # components
    for _key, (label, x, y, w, h, layer) in COMPONENTS.items():
        stroke = SVG_STROKE[layer]
        out.append(
            f'  <rect x="{x:.1f}" y="{flip_y(y + h):.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="white" stroke="{stroke}" stroke-width="2"/>\n'
        )

        lines = label.split("\n")
        start_y = y + h / 2 + (len(lines) * 14) / 2 - 14
        for i, line in enumerate(lines):
            out.append(
                f'  <text x="{x + w/2:.1f}" y="{flip_y(start_y - i * 14):.1f}" '
                f'text-anchor="middle" fill="#111">{line}</text>\n'
            )

    out.append("</svg>\n")
    path.write_text("".join(out), encoding="utf-8")


# -----------------------------------------------------------------------------
# Document audit
# -----------------------------------------------------------------------------
def document_audit() -> int:
    """
    Basic file audit for expected compliance / reference docs.
    Returns the count of missing files.
    """
    required = [
        "technical/certs/RichSolar-Alpha2Pro-UL1973.pdf",
        "technical/certs/RichSolar-Alpha2Pro-UN383.pdf",
        "technical/certs/Renogy-DCC30-Listing.pdf",
        "technical/datasheets/Wire-125C-Spec.pdf",
        "technical/manuals/Mercedes-2026-AWD-Alternator-Guide.pdf",
    ]

    print("\n--- SLATE TECHNICAL FILE AUDIT ---")
    missing_count = 0

    for doc in required:
        if Path(doc).exists():
            print(f"[PASS] {doc}")
        else:
            print(f"[FAIL] MISSING: {doc}")
            missing_count += 1

    print("----------------------------------")
    print(f"Audit Complete: {missing_count} file(s) missing.\n")
    return missing_count


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main() -> None:
    build_wires()

    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    dxf_path = out_dir / "slate_electrical_schematic.dxf"
    svg_path = out_dir / "slate_electrical_schematic.svg"

    write_dxf(dxf_path)
    write_svg(svg_path)

    print(f"Generated DXF: {dxf_path}")
    print(f"Generated SVG: {svg_path}")

    document_audit()


if __name__ == "__main__":
    main()
