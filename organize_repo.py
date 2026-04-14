"""
organize_repo.py

Classifies and moves PDFs from:
  - repo root
  - technical/ root (files not yet sorted into a subfolder)

Routing rules (first match wins, case-insensitive):
  certs       : cert, certificate, coc, cofc, ul, etl, csa,
                listing, security, compliance
  datasheets  : datasheet, spec, specification, cutsheet
  manuals     : manual, install, installation, owner, guide
  (no match)  : technical/engineering/archive_phase0

Collision handling at destination:
  - Same name, identical content  -> delete the incoming duplicate
  - Same name, different content  -> move with a UTC timestamp suffix
"""

import shutil
import hashlib
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Directory structure
# ---------------------------------------------------------------------------

STRUCTURE = [
    "technical/engineering/archive_phase0",
    "technical/datasheets",
    "technical/manuals",
    "technical/certs",
]

FALLBACK_DIR = Path("technical/engineering/archive_phase0")

# ---------------------------------------------------------------------------
# Files that must never be moved or deleted by this script.
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

def get_file_hash(path: Path) -> str:
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def classify(filename: str) -> Path:
    """Return the correct destination folder for a PDF based on its filename."""
    lower = filename.lower()
    for keywords, folder in ROUTING_RULES:
        if any(kw in lower for kw in keywords):
            return folder
    return FALLBACK_DIR


def safe_move(src: Path, dest_dir: Path, timestamp: str) -> None:
    """
    Move src into dest_dir, handling name collisions safely.

    - No collision          : move directly.
    - Same name, same hash  : delete src (exact duplicate).
    - Same name, diff hash  : move src with a timestamp suffix.
    """
    dest = dest_dir / src.name

    if not dest.exists():
        shutil.move(str(src), str(dest))
        print(f"    Moved      -> {dest}")
        return

    if get_file_hash(src) == get_file_hash(dest):
        src.unlink()
        print(f"    Duplicate  -> deleted {src.name} (identical copy already in {dest_dir.name})")
    else:
        stamped = dest_dir / f"{src.stem}_{timestamp}{src.suffix}"
        shutil.move(str(src), str(stamped))
        print(f"    Conflict   -> moved as {stamped.name} (differs from existing)")


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

    # 3. Collect PDFs to classify.
    #    Scan repo root and technical/ root (one level only, not recursive).
    #    This catches files that were never sorted AND newly dropped root PDFs.
    scan_dirs = [Path("."), Path("technical")]
    pdfs: list[Path] = []

    for scan_dir in scan_dirs:
        for f in scan_dir.glob("*.pdf"):
            if f.name in PROTECTED_FILES:
                continue
            pdfs.append(f)

    if not pdfs:
        print("\n=== No PDFs to classify ===\n")
        return

    print(f"\n=== Classifying {len(pdfs)} PDF(s) ===")
    for pdf in sorted(pdfs):
        dest_dir = classify(pdf.name)
        print(f"  {pdf.name!r}")
        print(f"    Rule match -> {dest_dir}")
        safe_move(pdf, dest_dir, timestamp)

    print("\n=== Done ===\n")


if __name__ == "__main__":
    organize_and_deduplicate()
