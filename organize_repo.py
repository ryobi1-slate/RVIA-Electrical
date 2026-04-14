"""
organize_repo.py  —  safe intake script

Scope: repo root PDFs only.
This script does NOT scan, move, or delete anything inside technical/,
regulatory/, or output/. It is an intake gate, not a cleanup tool.

Routing rules (first match wins, case-insensitive):
  certs      : cert, certificate, coc, cofc, ul, etl, csa,
               listing, security, compliance
  datasheets : datasheet, spec, specification, cutsheet
  manuals    : manual, install, installation, owner, guide
  (no match) : technical/engineering/archive_phase0

Collision policy:
  If the destination file already exists, the source is LEFT IN PLACE
  and a conflict message is printed. Nothing is deleted or overwritten.
"""

import shutil
import hashlib
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Directory structure to ensure exists
# ---------------------------------------------------------------------------

STRUCTURE = [
    "technical/engineering/archive_phase0",
    "technical/datasheets",
    "technical/manuals",
    "technical/certs",
]

FALLBACK_DIR = Path("technical/engineering/archive_phase0")

# ---------------------------------------------------------------------------
# Files that must never be moved by this script.
# ---------------------------------------------------------------------------

PROTECTED_FILES = {
    "source-diagram.pdf",
    "generate_schematic.py",
    "organize_repo.py",
    "CLAUDE.md",
    "README.txt",
    "bom-details.txt",
    "system-spec.md",
    "prompt.md",
}

# ---------------------------------------------------------------------------
# Classification rules  (order matters — first match wins)
# ---------------------------------------------------------------------------

ROUTING_RULES = [
    (
        {"cert", "certificate", "coc", "cofc", "ul", "etl", "csa",
         "listing", "security", "compliance"},
        Path("technical/certs"),
    ),
    (
        {"datasheet", "spec", "specification", "cutsheet"},
        Path("technical/datasheets"),
    ),
    (
        {"manual", "install", "installation", "owner", "guide"},
        Path("technical/manuals"),
    ),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def classify(filename: str) -> Path:
    """Return the correct destination folder for a PDF based on its filename."""
    lower = filename.lower()
    for keywords, folder in ROUTING_RULES:
        if any(kw in lower for kw in keywords):
            return folder
    return FALLBACK_DIR


def safe_move(src: Path, dest_dir: Path) -> None:
    """
    Move src into dest_dir only if the destination does not already exist.
    If the destination exists, print a conflict message and leave src in place.
    Nothing is ever deleted.
    """
    dest = dest_dir / src.name

    if dest.exists():
        print(f"    CONFLICT: {dest} already exists — leaving {src.name} in place")
        return

    shutil.move(str(src), str(dest))
    print(f"    Moved -> {dest}")


# ---------------------------------------------------------------------------
# Archive current output files before the generator rewrites them
# ---------------------------------------------------------------------------

def archive_outputs(timestamp: str) -> None:
    stale = [
        Path("output/slate_electrical_schematic.dxf"),
        Path("output/slate_electrical_schematic.svg"),
        Path("output/slate_electrical_notes.md"),
    ]
    archived = False
    for src in stale:
        if src.exists():
            dest = FALLBACK_DIR / f"{src.stem}_{timestamp}{src.suffix}"
            shutil.move(str(src), str(dest))
            print(f"    Archived   {src} -> {dest.name}")
            archived = True
    if not archived:
        print("    (no prior outputs to archive)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def organize_and_deduplicate() -> None:
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")

    # 1. Ensure folder structure exists
    for folder in STRUCTURE:
        Path(folder).mkdir(parents=True, exist_ok=True)

    # 2. Archive prior outputs before regeneration
    print("\n=== Archiving prior outputs ===")
    archive_outputs(timestamp)

    # 3. Scan repo root only — no recursion, no technical/ scanning.
    pdfs = [
        f for f in Path(".").glob("*.pdf")
        if f.name not in PROTECTED_FILES
    ]

    if not pdfs:
        print("\n=== No new root-level PDFs to intake ===\n")
        return

    print(f"\n=== Intake: {len(pdfs)} root-level PDF(s) ===")
    for pdf in sorted(pdfs):
        dest_dir = classify(pdf.name)
        print(f"  {pdf.name!r}")
        print(f"    Rule match -> {dest_dir}")
        safe_move(pdf, dest_dir)

    print("\n=== Done ===\n")


if __name__ == "__main__":
    organize_and_deduplicate()
