import os
import shutil
import hashlib
from pathlib import Path

# Define production hierarchy
STRUCTURE = [
    "technical/engineering/archive_phase0",
    "technical/datasheets",
    "technical/manuals",
    "technical/certs"
]

def get_file_hash(path):
    """Check if two files are actually the same content."""
    hasher = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def organize_and_deduplicate():
    # 1. Create folders
    for folder in STRUCTURE:
        Path(folder).mkdir(parents=True, exist_ok=True)

    # 2. Move known Phase 0 files to archive
    stale_files = ["output/slate_electrical_schematic.svg", "output/slate_electrical_notes.md"]
    archive_dir = Path("technical/engineering/archive_phase0")
    for f in stale_files:
        if Path(f).exists():
            shutil.move(f, archive_dir / os.path.basename(f))

    # 3. Basic De-duplication
    # Scans the root for PDFs and moves them to 'manuals' if not already there
    seen_hashes = {}
    for file in Path(".").glob("*.pdf"):
        f_hash = get_file_hash(file)
        if f_hash in seen_hashes:
            print(f"Deleting duplicate: {file.name} (Same as {seen_hashes[f_hash]})")
            file.unlink() # Deletes the duplicate
        else:
            seen_hashes[f_hash] = file.name
            # Move to manuals as a default bucket for now
            shutil.move(str(file), f"technical/manuals/{file.name}")
            print(f"Organized: {file.name}")

if __name__ == "__main__":
    organize_and_deduplicate()
