import os
import shutil
from pathlib import Path

# Define the production hierarchy
STRUCTURE = [
    "technical/engineering/archive_phase0",
    "technical/datasheets",
    "technical/manuals",
    "technical/certs"
]

# Files to move into archive (Stale Phase 0)
STALE_FILES = [
    "output/slate_electrical_schematic.svg",
    "output/slate_electrical_notes.md",
    "output/slate_dc_demand_load.md"
]

def clean_and_organize():
    # 1. Create directory structure
    for folder in STRUCTURE:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f"Created: {folder}")

    # 2. Archive Phase 0 artifacts
    archive_dir = Path("technical/engineering/archive_phase0")
    for file_path in STALE_FILES:
        src = Path(file_path)
        if src.exists():
            shutil.move(str(src), str(archive_dir / src.name))
            print(f"Archived: {src.name}")

    # 3. Maintain current foundation
    script = Path("generate_schematic.py")
    if script.exists():
        shutil.copy(str(script), "technical/engineering/generate_schematic.py")
        print("Foundation script synchronized to technical/engineering/")

if __name__ == "__main__":
    clean_and_organize()
    print("\nRepo structure updated for Phase 1 Lock.")