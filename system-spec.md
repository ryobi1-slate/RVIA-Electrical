# Slate 2026 RV - Electrical Schematic Spec

## Goal
Create a clean 2D one-line RV electrical schematic as a DXF file for AutoCAD.

This is a schematic drawing, not a physical routing layout.

## Source files
- `source-diagram.pdf` = source of connection logic, breaker and fuse labels, wire sizes, and overall system relationships
- `bom-details.txt` = source of actual component names, descriptions, and vendor part numbers

Use both files together.

## Core components to include

### Charging Sources
- Rich Solar MEGA 200 ONYX 200W Solar Panel
  - Part: RS-M200B
- Renogy 50A 12V DC-to-DC On-Board Battery Charger with MPPT
  - Part: RBC50D1S-G7-US

### House Battery System
- Rich Solar ALPHA 2 PRO 12V 200Ah LiFePO4 Battery
  - Part: RS-B122SP
- Renogy Battery Shunt 300A
  - Part: RSHST-B02P300
- Rich Solar NOVA SUPERCHARGER 2K 2000W 12V Pure Sine Wave Inverter Charger
  - Part: RS-V2P12C
- Rich Solar inverter remote controller with LCD
  - Part: RS-RM02
- Renogy monitoring screen for DC-to-DC MPPT battery chargers
  - Part: RMS-DCDC

### AC Input / Distribution
- Conntek 30A Square Housing Shore Power Inlet
  - Part: 80425-A-SQBK
- WFCO WF-8930/50NPB 30A AC Distribution Panel
  - Part: WF-8930/50NPB
- Legrand Tamper Resistant 15A 125V GFCI outlets
  - Part: 1597TRBKCCD4

### DC Protection / Distribution
- Eaton Bussmann 185 Series Surface Mount Circuit Breaker, 60A
  - Part: 185060F-01-1
- Eaton Bussmann 185 Series Surface Mount Circuit Breaker, 80A
  - Part: 185080F-01-1
- Eaton Bussmann 187 Series Surface Mount Circuit Breaker, 200A
  - Part: 187200F-03-1
- Eaton Bussmann 187 Series Surface Mount Circuit Breaker, 25A
  - Part: 187025F-03-1
- 4-Post Power Distribution Bus Bar, 250A
  - Part: TBD
  - Note: mark as "final brand/rating to confirm"

## Main system relationships

### DC Charging Paths
Show these charging paths clearly, but do not invent functions not explicitly confirmed by the source diagram:

- Solar Panel -> 25A Breaker -> DC-DC + MPPT
- DC-DC + MPPT -> 60A Breaker -> Battery charging path
- 80A Breaker shown in charging path area exactly as labeled in the source diagram
- Do not assign a detailed functional description to the 25A breaker or 80A breaker unless explicitly shown in source material

### Main DC Storage / Protection
- Battery positive -> 200A Breaker -> main positive distribution path
- Battery negative -> 300A Shunt -> Negative Bus
- Main positive distribution path feeds:
  - inverter/charger DC input
  - DC distribution panel
- Negative Bus -> Chassis Ground
- Rear OEM Ground shown as separate reference and bonded simply, without added inferred devices

### Main AC Path
- Shore Inlet 30A -> Inverter/Charger / Transfer Switch
- Inverter/Charger -> AC Distribution Panel
- AC Distribution Panel -> branch circuits

## AC Distribution Panel Detail

Show the WFCO AC Distribution Panel as a simplified internal panel representation.

Include:
- 30A Main Breaker
- Branch Breaker: GFCI 1 - 15A
- Branch Breaker: GFCI 2 - 15A
- Branch Breaker: Optional Air Conditioner - 20A

Also include simplified:
- AC Neutral Terminal Bar
- AC Ground Terminal Bar

Do not draw full internal wiring detail inside the panel.
Do not attempt to reproduce every internal conductor bend from the reference image.
Keep it clean and schematic.

## DC Distribution Panel Detail

Show the DC Distribution Panel with explicit fuse positions and circuit assignments.

Do not collapse DC loads into a generic grouped block.

Show these fuse assignments exactly:

- F1 Heater - 15A
- F2 Water Pump - 15A
- F3 Refrigerator - 10A
- F4 Fan 1 - 7.5A
- F5 Fan 2 - 7.5A
- F6 Ceiling Lights - 10A
- F7 Reading Lights - 7.5A
- F8 USB A 1 - 10A
- F9 USB A 2 - 10A
- F10 12V Socket 1 - 15A
- F11 12V Socket 2 - 15A
- F12 USB C 100W - 15A
- F13 Spare
- F14 Spare
- F15 Spare

Represent the panel as a clean fuse panel block with labeled fuse positions.
Show positive and negative input to the DC panel.
Do not draw all internal hardware detail unless needed for clarity.

## Subsystems

### Lighting Control Subsystem
There is a separate lighting control detail using:
- Shelly Plus 1
- momentary switches
- 22 AWG control wiring
- 14 AWG lighting load wiring
- puck lights

This lighting control system should NOT be fully expanded inside the main one-line electrical schematic.

In the main schematic, represent it as:
- "Lighting System (see detail drawing)"

Do not draw the full internal control wiring for the Shelly or switch network in the one-line schematic.

## Branch loads to show in the main schematic

### DC Branch Loads
These should appear through the DC Distribution Panel detail:
- Heater
- Water Pump
- Refrigerator
- Fan 1
- Fan 2
- Ceiling Lights
- Reading Lights
- USB A 1
- USB A 2
- 12V Socket 1
- 12V Socket 2
- USB C 100W

### AC Branch Loads
These should appear from the AC Distribution Panel:
- GFCI 1
- GFCI 2
- Optional Air Conditioner

## Wiring information to show where clearly indicated in source material
Show wire sizes only where clearly supported by the source diagram or detail drawings.

Allowable wire labels to use when shown:
- 10/3
- 12/3
- 12/2
- 14/2
- 22/3
- 2/0
- 4 AWG
- 6 AWG
- 8 AWG
- 14 AWG
- 22 AWG

Do not guess wire sizes where unclear.

## Layout rules

Create a clean left-to-right one-line schematic with horizontal bands:

1. Top band: charging sources
   - solar panel
   - charge breaker devices
   - DC-DC + MPPT charger

2. Middle band: battery and main DC protection
   - battery
   - 200A breaker
   - 300A shunt
   - negative bus
   - positive distribution path
   - inverter/charger DC connection

3. Right-middle band: DC distribution panel
   - DC fuse panel with F1-F15 layout

4. Bottom band: AC system
   - shore inlet
   - inverter/charger / transfer switch
   - AC distribution panel
   - GFCI circuits
   - optional AC

5. Grounding references
   - negative bus
   - chassis ground
   - rear OEM ground

## Drafting rules
- Use only simple geometry:
  - rectangles for components
  - lines for conductors
  - arrows for direction of power flow
  - text labels for all components and circuits
- Use only horizontal and vertical lines
- No diagonal lines
- Avoid conductor crossings where possible
- Keep spacing even and readable
- Favor drafting clarity over realism
- Use a clean AutoCAD-ready schematic style
- Include part numbers in smaller text under major component labels for:
  - inverter/charger
  - battery
  - DC-DC + MPPT
  - shunt
  - AC panel
  - shore inlet
  - major breakers
- Mark bus bar as:
  - "250A Bus Bar - final brand/rating to confirm"

## Output requirements
Create:
1. `output/slate_electrical_schematic.dxf`
2. `output/slate_electrical_schematic.svg`
3. `output/slate_electrical_notes.md`

## Notes file requirements
The notes file must include:
- assumptions made
- any ambiguity between BOM and source diagram
- any labels or wire sizes that were unclear
- any source-confirmed connections vs assumed routing decisions
- any items marked TBD
- suggested AutoCAD cleanup items

## Important limitations
- Do not redesign the electrical system
- Do not invent hidden devices or inferred protection components
- Do not assign detailed function to the 25A breaker or 80A breaker unless explicitly supported by source material
- Do not expand the lighting control subsystem into the one-line schematic
- Keep the refrigerator routed through the DC distribution panel for schematic clarity unless source material explicitly requires otherwise