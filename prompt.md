You are building a clean AutoCAD-ready RV electrical schematic from the project files in this folder.

Read:
- `system-spec.md`
- `source-diagram.pdf`

Task:
Generate a first-pass 2D one-line electrical schematic as both DXF and SVG.

Important:
- Do not redesign the system.
- Use the source diagram as the source of components and ratings.
- Use `system-spec.md` for layout, hierarchy, and drawing rules.
- Keep the result simple, clean, and readable.
- Favor drafting clarity over visual complexity.

Deliverables:
- `output/slate_electrical_schematic.dxf`
- `output/slate_electrical_schematic.svg`
- `output/slate_electrical_notes.md`

DXF requirements:
- ASCII DXF
- Simple entities only if possible
- Layers:
  - ELEC-DC
  - ELEC-AC
  - ELEC-GND
  - TEXT
- Use rectangles, lines, and text
- Keep coordinates consistent and spaced out
- Avoid overlaps
- Make the file open cleanly in AutoCAD

Before writing files:
1. Summarize the interpreted system in plain English
2. List ambiguities
3. Then generate the files

If needed, create a small Python script in the project folder to generate the DXF and SVG programmatically, then run it.