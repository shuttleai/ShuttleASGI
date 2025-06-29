#!/usr/bin/env python3
"""
Clean script for ShuttleASGI
Removes build artifacts and compiled files
"""

import os
import shutil
import glob
from pathlib import Path

def main():
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("🧹 Cleaning ShuttleASGI build artifacts")
    print("=" * 40)
    
    # Directories to remove
    dirs_to_remove = [
        "build",
        "dist", 
        "*.egg-info",
        "__pycache__",
        ".pytest_cache"
    ]
    
    # Files to remove
    files_to_remove = [
        "shuttleasgi/*.c",
        "shuttleasgi/*.so",
        "shuttleasgi/*.html",  # Cython annotation files
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo"
    ]
    
    removed_count = 0
    
    # Remove directories
    for pattern in dirs_to_remove:
        for path in glob.glob(pattern):
            if os.path.isdir(path):
                print(f"🗑️  Removing directory: {path}")
                shutil.rmtree(path)
                removed_count += 1
    
    # Remove files
    for pattern in files_to_remove:
        for path in glob.glob(pattern, recursive=True):
            if os.path.isfile(path):
                print(f"🗑️  Removing file: {path}")
                os.remove(path)
                removed_count += 1
    
    if removed_count == 0:
        print("✨ Already clean!")
    else:
        print(f"\n🎉 Cleaned {removed_count} items")

if __name__ == "__main__":
    main()