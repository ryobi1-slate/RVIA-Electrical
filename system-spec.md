# Slate 2026 RV - Electrical Schematic Spec

## Goal
Create a clean 2D one-line RV electrical schematic as a DXF file for AutoCAD.

This is a schematic drawing, not a physical installation layout.

## Delivery phases

This schematic is built up **incrementally in phases**. Each phase locks in a
subsystem before the next is layered on top, so the in-repo generator may
intentionally render a subset of the "Required system content" list below.
The full list represents the **end-state scope** after all phases are
complete, not the scope of any single intermediate phase.

| Phase | Scope | Generator output | Status |
|-------|-------|------------------|--------|
| Phase 0 | First-pass full-system one-line drawing (charging + main DC + DC distribution + DC loads + AC + grounds) | Archived under `output/phase0_archive/` | Reference only |
| Phase 1 | Charging subsystem lock: Solar Panel, 25A Solar Breaker, DC-DC + MPPT, 60A Charge Breaker, 80A Alt Breaker, Chassis Battery, House Battery, and all 125°C marine conductors between them | `output/slate_electrical_schematic.dxf` + `.svg` | **Current** |
| Phase 2 | Main DC protection + negative path: 200A battery breaker, 300A shunt, negative bus, chassis/rear OEM grounds | Layered onto Phase 1 output | Planned |
| Phase 3 | DC Distribution Panel + all 12 fused DC branch circuits | Layered onto Phase 2 output | Planned |
| Phase 4 | AC subsystem: Shore Inlet, Inverter/Charger/Transfer Switch, AC Distribution Panel, GFCI 1, GFCI 2, Optional Air Conditioner, AC grounds | Layered onto Phase 3 output | Planned |

Until Phase 4 completes, the live `output/slate_electrical_schematic.dxf`
and `output/slate_electrical_schematic.svg` reflect the current phase's
scope only. The full-system reference drawing is preserved in
`output/phase0_archive/slate_electrical_schematic.svg` along with its
original notes (`output/phase0_archive/slate_electrical_notes.md`) and the
DC demand load calculation (`output/phase0_archive/slate_dc_demand_load.md`).

## Source of truth
Use `source-diagram.pdf` as the source of components, fuse sizes, breaker sizes, wire sizes, and naming.

## Required system content
From the source diagram, include (end-state, across all phases combined):

- 200W Solar Panel
- DC to DC + MPPT
- 60A Surface Mount Breaker
- 12V 200Ah LiFePO4 Battery
- 300A Shunt
- Negative Bus
- 200A Breaker
- Inverter + Charger + Transfer Switch, 2000W pass-through, UL 458
- Shore Inlet 30A
- AC Distribution Panel
- DC Distribution Panel
- Chassis Ground
- Rear OEM Ground

## DC branch circuits to include
- Refrigerator (10A fuse)
- Diesel Heater (15A fuse)
- USB-C 100W (15A fuse)
- USB-A 1 (10A fuse)
- USB-A 2 (10A fuse)
- 12V Power Socket 1 (15A fuse)
- 12V Power Socket 2 (15A fuse)
- Reading Lights (7.5A fuse)
- Ceiling Puck Lights (10A fuse)
- Water Pump (15A fuse)
- Fan 1 (7.5A fuse)
- Fan 2 (7.5A fuse)

## AC branch circuits to include
- GFCI 1 (15A breaker)
- GFCI 2 (15A breaker)
- Optional Air Conditioner (20A breaker)

## Layout rules
Create a clean left-to-right one-line schematic with four horizontal bands:

1. Top band: charging sources
   - Solar Panel
   - DC-DC + MPPT
   - Shore Inlet feeding inverter/charger
2. Middle band: main DC storage and protection
   - Battery
   - 300A shunt
   - Negative bus
   - 200A breaker
   - Main positive path
3. Right band: DC distribution and DC loads
   - DC distribution panel
   - all fused DC loads
4. Bottom band: AC distribution and AC loads
   - Shore Inlet
   - Inverter/charger
   - AC distribution panel
   - AC branch circuits

## Connection logic
- Solar Panel connects to DC-DC + MPPT, then through 60A breaker to battery charging path.
- Battery negative routes through 300A shunt to negative bus.
- Battery positive routes through 200A breaker to main positive distribution path.
- Positive distribution feeds DC distribution panel and inverter/charger.
- Shore inlet feeds inverter/charger AC input.
- Inverter/charger feeds AC distribution panel.
- AC distribution panel feeds GFCI circuits and optional AC.
- DC distribution panel feeds all listed DC circuits.
- Negative bus connects to chassis ground / OEM ground reference.

## Drafting rules
- Use only simple geometry:
  - rectangles for components
  - lines for conductors
  - arrows for power flow
  - text labels for all components and circuits
- Use only straight horizontal and vertical lines
- No diagonal lines
- No overlapping geometry where avoidable
- Keep spacing even and readable
- Put fuse or breaker size directly in the load label where applicable
- Add wire sizes only where clearly shown in the source diagram
- Keep the drawing clean enough that a drafter can refine it later

## Output requirements
Create:
1. `output/slate_electrical_schematic.dxf`
2. `output/slate_electrical_schematic.svg`
3. `output/slate_electrical_notes.md`

## Notes file requirements
The notes file must include:
- assumptions made
- any ambiguous items from the PDF
- any labels or wire sizes that were unclear
- suggested cleanup items for AutoCAD