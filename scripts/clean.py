#!/usr/bin/env python3
"""
Clean script for ShuttleASGI
Removes build artifacts, compiled files, and cache directories recursively.
"""

import os
import shutil
import glob
import sys
from pathlib import Path

def main(dry_run=False):
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("🧹 Cleaning ShuttleASGI build artifacts")
    print("=" * 40)
    
    # Top-level and recursive directories to remove (sorted)
    dirs_to_remove = [
        "*.egg-info",
        "**/__pycache__",  # Recursive; covers top-level too
        ".eggs",
        ".pytest_cache",
        "build",
        "dist",
    ]
    
    # Files to remove (sorted; recursive where noted)
    files_to_remove = [
        "**/*.pyc",    # Recursive
        "**/*.pyo",    # Recursive
        "**/*.pyd",
        "shuttleasgi/*.c",
        "shuttleasgi/middlewares/*.c",
        "shuttleasgi/validation/sai/*.c",
        "shuttleasgi/*.html",  # Cython annotation files
        "shuttleasgi/*.so",
    ]
    
    removed_count = 0
    
    # Remove directories
    for pattern in dirs_to_remove:
        for path in glob.glob(pattern, recursive=True):
            if os.path.isdir(path):
                print(f"🗑️  Removing directory: {path}")
                if not dry_run:
                    try:
                        shutil.rmtree(path)
                    except Exception as e:
                        print(f"⚠️  Failed to remove {path}: {e}")
                        continue
                removed_count += 1
    
    # Remove files
    for pattern in files_to_remove:
        for path in glob.glob(pattern, recursive=True):
            if os.path.isfile(path):
                print(f"🗑️  Removing file: {path}")
                if not dry_run:
                    try:
                        os.remove(path)
                    except Exception as e:
                        print(f"⚠️  Failed to remove {path}: {e}")
                        continue
                removed_count += 1
    
    if removed_count == 0:
        print("✨ Already clean!")
    else:
        print(f"\n🎉 Cleaned {removed_count} items (dry-run: {dry_run})")

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    main(dry_run=dry_run)