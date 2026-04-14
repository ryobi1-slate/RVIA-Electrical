import os
import shutil
import hashlib
from datetime import datetime
from pathlib import Path

# Define production hierarchy
STRUCTURE = [
    "technical/engineering/archive_phase0",
    "technical/datasheets",
    "technical/manuals",
    "technical/certs"
]

# Root files that must never be moved or deleted by this script.
# Add any source diagram or input file here to protect it.
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


def get_file_hash(path):
    """Return MD5 hash of file contents for deduplication."""
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def archive_outputs():
    """
    Archive existing output files before regeneration.
    Uses a UTC timestamp suffix so each prior output is preserved distinctly.
    Covers both DXF and SVG.
    """
    archive_dir = Path("technical/engineering/archive_phase0")
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")

    stale_files = [
        "output/slate_electrical_schematic.dxf",
        "output/slate_electrical_schematic.svg",
        "output/slate_electrical_notes.md",
    ]

    for f in stale_files:
        src = Path(f)
        if src.exists():
            dest = archive_dir / f"{src.stem}_{timestamp}{src.suffix}"
            shutil.move(str(src), str(dest))
            print(f"Archived: {f} -> {dest.name}")


def organize_and_deduplicate():
    # 1. Create folder structure
    for folder in STRUCTURE:
        Path(folder).mkdir(parents=True, exist_ok=True)

    # 2. Archive stale outputs before the generator regenerates them
    archive_outputs()

    # 3. Reorganize root-level PDFs only.
    #    Protected files are never touched.
    #    Duplicates (by content) are deleted; unique files move to technical/manuals/.
    seen_hashes = {}
    for file in Path(".").glob("*.pdf"):
        if file.name in PROTECTED_FILES:
            print(f"Skipping protected file: {file.name}")
            continue

        f_hash = get_file_hash(file)
        if f_hash in seen_hashes:
            print(f"Deleting duplicate: {file.name} (same as {seen_hashes[f_hash]})")
            file.unlink()
        else:
            seen_hashes[f_hash] = file.name
            shutil.move(str(file), f"technical/manuals/{file.name}")
            print(f"Organized: {file.name}")


if __name__ == "__main__":
    organize_and_deduplicate()
