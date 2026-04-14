# CLAUDE.md — Operating Policy for RVIA-Electrical

This file defines the operating policy for all AI-assisted work in this repo.
Read it before making any change. These rules are not suggestions.

---

## Purpose

This repo is a drafting automation workflow for Slate's RVIA electrical and
plumbing documentation. Its job is to turn internal build knowledge into a
structured system that:

1. Organizes source documents and technical files
2. Generates clean first-pass schematic drawings (DXF, SVG)
3. Preserves assumptions and ambiguities in notes
4. Supports future automation for RVIA and compliance documentation
5. Reduces repetitive drafting work without redesigning the system itself

---

## What this repo is not

- Not a finished drawing set
- Not a compliance submission
- Not a live BOM system
- Not a design tool

Outputs are first-pass drafts a human can open in AutoCAD and refine.
They are not final stamped engineering drawings.

---

## Core operating rules

### Do not invent design

Do not add components, wire paths, breaker sizes, or system topology that
are not present in the source drawings or BOM. If something is missing from
the source, flag it — do not fill it in.

### Do not silently fix engineering decisions

If a schematic shows something that looks wrong, preserve it as drawn and
flag it. Engineering judgment belongs to the human reviewer.

### Do not guess when source material is unclear

When something is ambiguous, write `[ASSUMPTION - needs review]` in the
notes output. Do not make the assumption look final.

---

## Conflict policy

**If source files conflict, do not silently reconcile them.**

- Preserve the source drawing as drawn
- Preserve the BOM as listed
- Write the conflict into the notes output as `[CONFLICT - needs review]`
- Do not pick one source over the other without a human decision

This applies to any disagreement between:
- Drawing geometry and BOM part specs
- BOM entries and datasheet values
- Two versions of the same document
- Any other pairing of source files

---

## Versioning policy for generated outputs

**Generated drawings and outputs are versionable artifacts.**

Do not overwrite a prior output without either:
1. Archiving the previous version first (with a timestamp), or
2. Replacing it through a clearly documented repo workflow step

Acceptable patterns:
- `organize_repo.py` archives with timestamp before `generate_schematic.py`
  regenerates → explicit two-step replacement
- `output/` tracked in git → git history is the version record

Unacceptable:
- Silent overwrite of DXF or SVG with no prior archival
- Archive step that uses a fixed filename (archive overwrites itself)
- Output files invisible to git with no other versioning mechanism

---

## Drawing standards

- Schematic clarity over physical installation detail
- AutoCAD-friendly output (DXF AC1009, named layers, standard text style)
- Layer convention: `ELEC-DC` (red), `ELEC-AC` (blue), `ELEC-GND` (green), `TEXT` (white)
- Readability matters more than visual complexity
- Labels should reflect the BOM description, not an invented name

---

## Repo automation rules

- `organize_repo.py` runs before the generator — it archives old outputs and
  creates the folder structure
- `generate_schematic.py` runs after — it writes fresh outputs into `output/`
- The workflow commits only when files actually changed
- The bot (`Slate-Bot`) must not trigger itself (bot-loop guard in workflow)
- No duplicate workflow files; one canonical workflow in `.github/workflows/`

---

## Scope limits

- Do not redesign the repo structure beyond what is stated in a task
- Do not change filenames unless explicitly asked
- Do not add new workflow files
- Do not create alternative versions of scripts unless necessary
- Do not add speculative abstractions, helpers, or features for hypothetical
  future requirements

---

## Future scope (not yet active)

This repo will eventually support both electrical and plumbing.
When plumbing is added, it should follow the same pattern:
- Same layer/output/audit structure as electrical
- Same conflict and versioning policies
- Separate generator script, not merged into the electrical script
