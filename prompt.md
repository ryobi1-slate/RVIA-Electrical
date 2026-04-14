You are building a clean AutoCAD-ready RV electrical schematic from the project files in this folder.

Read these files first:
- `system-spec.md`
- `source-diagram.pdf`
- `bom-details.txt`

Your task:
Generate a first-pass 2D one-line electrical schematic as both DXF and SVG.

Use these rules:
- Do not redesign the system
- Use the source diagram for connection logic, breaker and fuse labels, and wire sizes
- Use the BOM details for actual component names and part numbers
- Use `system-spec.md` as the controlling document for layout, hierarchy, subsystem handling, and output rules
- Keep the drawing simple, clean, and readable
- Favor drafting clarity over visual complexity

Output files required:
- `output/slate_electrical_schematic.dxf`
- `output/slate_electrical_schematic.svg`
- `output/slate_electrical_notes.md`

DXF requirements:
- ASCII DXF
- AutoCAD-compatible
- Use simple entities where possible
- Use these layers:
  - ELEC-DC
  - ELEC-AC
  - ELEC-GND
  - TEXT
- Use rectangles, straight lines, arrows, and text
- Use only horizontal and vertical linework
- Avoid overlapping geometry where possible
- Keep spacing consistent
- Make the file open cleanly in AutoCAD

Drawing content requirements:
- Show the charging system, battery system, inverter/charger, AC panel, DC panel, grounding references, and branch circuits
- Use the DC panel fuse assignments exactly as defined in `system-spec.md`
- Do not collapse DC loads into a generic block
- Show the AC panel in simplified form with:
  - 30A main breaker
  - 15A GFCI 1 breaker
  - 15A GFCI 2 breaker
  - 20A optional AC breaker
  - neutral bar
  - ground bar
- Do not expand full internal AC panel wiring detail
- Do not expand lighting control wiring into the main one-line schematic
- Treat the lighting control system as a subsystem and represent it as:
  - "Lighting System (see detail drawing)"

Important interpretation rules:
- Include the 25A breaker and 80A breaker exactly as labeled if shown in the source diagram
- Do not assign invented functional descriptions to the 25A breaker or 80A breaker unless explicitly supported by source material
- Keep grounding simple:
  - Negative Bus
  - Chassis Ground
  - Rear OEM Ground
- Do not add inferred bonding devices or extra grounding hardware
- Mark the 250A bus bar as:
  - "250A Bus Bar - final brand/rating to confirm"
- Route the refrigerator as a DC distribution panel load for schematic clarity unless source material explicitly requires otherwise
- Separate source-confirmed connections from assumed routing decisions in the notes file

Before writing output files:
1. Summarize the interpreted system in plain English
2. List ambiguities or conflicts between source files
3. Then generate the output files

If useful, create a Python script in the project folder to generate the DXF and SVG programmatically, then run it.

Do not invent missing technical details.
If something is unclear, note it clearly in `output/slate_electrical_notes.md`.
