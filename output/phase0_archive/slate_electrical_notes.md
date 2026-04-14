# Slate 2026 RV – Electrical Schematic Notes

Companion notes for `slate_electrical_schematic.dxf` / `slate_electrical_schematic.svg`.
This is a first-pass one-line schematic drafted from `source-diagram.pdf` and
`system-spec.md`. It is not a physical installation layout.

## Drawing conventions

- **Layers** used in the DXF:
  - `ELEC-DC` – all DC components and conductors (drawn red)
  - `ELEC-AC` – all AC components and conductors (drawn blue)
  - `ELEC-GND` – ground/bonding conductors and ground references (drawn green)
  - `TEXT` – every text label (component labels, wire sizes, title block)
- Geometry is restricted to orthogonal lines, rectangles, and TEXT entities
  for easy editing in AutoCAD.
- Protective device ratings (fuse / breaker sizes) are included inline with
  each load label as required by the spec.
- Wire sizes are labeled on the conductor where the source PDF clearly
  indicated a size.

## Assumptions

1. Battery positive path: Battery → 200A Breaker → virtual main positive
   rail → both DC Distribution Panel and Inverter DC input. The source PDF
   shows the positive trunk branching at a busbar; the schematic represents
   that as an orthogonal tee at a single node.
2. Battery negative path: Battery → 300A Shunt → Negative Bus, with a
   branch down to the Inverter DC negative terminal.
3. Negative Bus → Chassis Ground → Rear OEM Ground is drawn in series as
   the common bonding path called out in the spec.
4. Rear OEM Ground is additionally bonded to the AC Distribution Panel via
   an 8 AWG green conductor, matching the green conductor shown on the PDF.
5. The 60A Surface Mount Breaker sits between the DC-DC + MPPT output and
   the battery positive terminal. This matches the spec wording
   ("through 60A breaker to battery charging path").
6. The DC Distribution Panel is shown as the aggregation point for every
   listed DC branch circuit, including the Refrigerator. The PDF routes the
   refrigerator with an 8 AWG conductor, so that wire size is preserved on
   the tap, but the tap origin is drawn from the DC Distribution Panel to
   match the spec's connection logic.
7. AC input topology: Shore Inlet → Inverter/Charger (acts as transfer
   switch) → AC Distribution Panel → branch breakers. The inverter pass-
   through behavior is implied by the component label; no separate transfer
   switch block is drawn because the inverter/charger integrates it.
8. The vertical "trunk" on the right side of the drawing is a visual
   convenience so each DC branch reads cleanly; electrically each branch
   originates at the DC Distribution Panel output.

## Ambiguities from the source PDF

1. **25A / 60A / 80A breakers** are visible in the PDF but are not called
   out by role in `system-spec.md`. They have been placed in the top band
   with explicit labels assigned per engineering review:
   - **25A Solar Input Protection** – between the 200W Solar Panel and the
     DC-DC + MPPT solar input; matches the 6 AWG conductor callouts.
   - **60A Main Charge Protection** – between the DC-DC + MPPT output and
     the house battery positive terminal; matches the 4 AWG callout and
     the spec wording "through 60A breaker to battery charging path".
   - **80A Alternator Protection** – between the Chassis Battery and the
     DC-DC + MPPT alternator input. The Renogy RBC50D1S-G7-US is a
     dual-input DC-DC charger (solar + alternator), so the 80A breaker
     protects the alternator-side feed. A 4 AWG conductor is shown from
     the Chassis Battery to the 80A breaker, matching the PDF AWG callout.
2. **Refrigerator feed origin** – the PDF shows a short 8 AWG run to the
   refrigerator located physically near the main negative bus. The spec
   requires the refrigerator to be a DC Distribution Panel circuit with a
   10A fuse, so that has been honored. Confirm whether the refrigerator is
   actually on the DC panel or on a direct battery feed through its own
   fused disconnect.
3. **Wire color vs. AWG** – the PDF uses multiple colors (red, black,
   yellow, purple, blue, green) in addition to AWG callouts. Only the AWG
   values were brought onto the schematic; color coding was not transcribed
   because it did not uniquely identify size.
4. **AC Distribution Panel model** – the BOM lists a WFCO WF-8930/50NPB
   (30A). The PDF is labeled "AC DISTRIBUTION PANEL (UL LISTED)" without
   a model. Drawing uses the generic label.
5. **Inverter/charger branch-circuit protection** – the PDF shows a 200A
   breaker between battery and inverter/charger and a 60A breaker on the
   solar charge path. It does not clearly show an AC output breaker on the
   inverter before the AC Distribution Panel; none is drawn.
6. **Rear OEM Ground bonding** – the PDF's green 8 AWG conductor runs from
   Rear OEM Ground to the AC Distribution Panel. Whether that is the sole
   bonding point or also ties into the DC negative bus is not explicit in
   the PDF. The schematic shows the rear OEM / chassis ground series chain
   plus the AC panel bond as two distinct green conductors.

## Labels / wire sizes that were unclear

- The "SUPPLIED WIRE" callout to the Diesel Heater is copied from the PDF
  verbatim; the actual AWG is not specified (factory-supplied harness).
- The conductor between the 300A Shunt and the Negative Bus is unlabeled
  in the PDF and left unlabeled on the schematic.
- Branch circuit AWGs for the AC panel output (GFCIs and Optional AC) are
  labeled "12/3" on the PDF; no separate neutral/hot color distinction
  was transcribed.
- The conductor between the inverter DC input and the main positive rail
  is drawn as 2/0 AWG based on the PDF's #2/0 callouts on the inverter
  side. Confirm lug sizing (2/0 to 3/8" stud vs. 5/16" stud) at
  installation – both lug styles appear on the BOM.

## Suggested cleanup items for AutoCAD

1. Replace the plain rectangles with block references (`INSERT`) for each
   component type so edits and future schematic sheets can reuse symbols.
2. Convert multi-line text labels to `MTEXT` entities. The current export
   uses single-line `TEXT` entities stacked vertically for maximum
   compatibility with older AutoCAD / viewer implementations.
3. Add standard electrical symbols (battery cells, breaker zig-zag, GFCI
   test/reset, shunt resistor) to replace the rectangles-with-label
   placeholders where schematic conventions are desired.
4. Add a proper title block, revision table, and drawing border.
5. Verify wire-size labels against a current conductor schedule and add
   color callouts if the shop drawing convention requires them.
6. Consider splitting onto two sheets: one DC one-line (top, middle, and
   right bands) and one AC one-line (bottom band) if you want to reduce
   sheet density.
7. Snap spacing is 20 drawing units; reset to whatever grid your template
   uses before dimensioning.
8. Confirm the Chassis Battery → 80A Alternator Protection feed sizing
   against the actual alternator output; if the alternator is rated
   above ~60A continuous, verify the 80A breaker (or upgrade to a larger
   device) and the 4 AWG feeder length/voltage-drop budget.
9. Inverter/charger is currently a single large block. If desired, split
   into three sub-blocks (inverter, charger, transfer switch) with
   internal connections to match UL-458 schematic conventions.
10. Add ground-reference triangles at the chassis and rear OEM ground
    terminations instead of labeled rectangles once the symbol library is
    in place.
