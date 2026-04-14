# RVIA Electrical – DXF Generator

This project generates a clean AutoCAD electrical schematic using Claude Code.

## Files
- system-spec.md → system rules + layout
- prompt.md → execution instructions
- source-diagram.pdf → wiring reference
- bom-details.txt → components and part numbers

## Output
Generated files go in /output:
- slate_electrical_schematic.dxf
- slate_electrical_schematic.svg
- slate_electrical_notes.md

## Run
Open Claude Code in this repo and run:

Read prompt.md and execute the workflow