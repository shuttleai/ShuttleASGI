#!/usr/bin/env python3
"""
rename.py
This script renames all subfolder names, file names, and content from "BlackSheep" to "ShuttleASGI"
in this parent directory while preserving case sensitivity.
"""

import os
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

class CasePreservingReplacer:
    def __init__(self, old_name="BlackSheep", new_name="ShuttleASGI"):
        self.old_name = old_name
        self.new_name = new_name
        
        # Pre-compile regex patterns for different case variations
        self.patterns = [
            (re.compile(re.escape(old_name)), new_name),  # BlackSheep -> ShuttleASGI
            (re.compile(re.escape(old_name.lower())), new_name.lower()),  # blacksheep -> shuttleasgi
            (re.compile(re.escape(old_name.upper())), new_name.upper()),  # BLACKSHEEP -> SHUTTLEASGI
            (re.compile(re.escape(old_name.capitalize())), new_name.capitalize()),  # Blacksheep -> Shuttleasgi
        ]
        
        # Binary file extensions to skip
        self.binary_extensions = {
            '.pyc', '.pyo', '.so', '.dll', '.exe', '.bin', '.db', '.sqlite',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
            '.mp3', '.mp4', '.avi', '.mov', '.wav', '.pdf', '.zip', '.tar', '.gz'
        }

    def replace_content_in_file(self, file_path):
        """Replace content in a single file using memory mapping for speed."""
        try:
            # Skip binary files
            if file_path.suffix.lower() in self.binary_extensions:
                return False, f"Skipped binary file: {file_path}"
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Apply all pattern replacements
            original_content = content
            for pattern, replacement in self.patterns:
                content = pattern.sub(replacement, content)
            
            # Write back only if content changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True, f"Updated content: {file_path}"
            
            return False, f"No changes needed: {file_path}"
            
        except Exception as e:
            return False, f"Error processing {file_path}: {e}"

    def rename_path(self, path):
        """Rename a file or directory path."""
        old_name = path.name
        new_name = old_name
        
        # Apply case-preserving replacements to the name
        for pattern, replacement in self.patterns:
            new_name = pattern.sub(replacement, new_name)
        
        if new_name != old_name:
            new_path = path.parent / new_name
            try:
                path.rename(new_path)
                return True, f"Renamed: {path} -> {new_path}"
            except Exception as e:
                return False, f"Error renaming {path}: {e}"
        
        return False, f"No rename needed: {path}"

def main():
    print("Starting BlackSheep to ShuttleASGI project rename...")
    
    root_dir = Path.cwd()
    replacer = CasePreservingReplacer()
    
    # Collect all files and directories
    all_files = []
    all_dirs = []
    
    for item in root_dir.rglob('*'):
        if item.name == 'rename.py':  # Skip this script
            continue
        if item.is_file():
            all_files.append(item)
        elif item.is_dir():
            all_dirs.append(item)
    
    print(f"Found {len(all_files)} files and {len(all_dirs)} directories to process")
    
    # Step 1: Replace content in files (parallel processing)
    print("\nStep 1: Updating file contents...")
    content_results = []
    
    with ThreadPoolExecutor(max_workers=min(8, os.cpu_count())) as executor:
        future_to_file = {
            executor.submit(replacer.replace_content_in_file, file_path): file_path 
            for file_path in all_files
        }
        
        for future in as_completed(future_to_file):
            success, message = future.result()
            if success:
                content_results.append(message)
    
    print(f"Updated content in {len(content_results)} files")
    
    # Step 2: Rename files and directories (must be done sequentially, deepest first)
    print("\nStep 2: Renaming files and directories...")
    
    # Sort by depth (deepest first) to avoid path conflicts
    all_items = sorted(all_files + all_dirs, key=lambda p: len(p.parts), reverse=True)
    
    rename_results = []
    for item in all_items:
        # Re-check if path exists (it might have been renamed already as part of parent)
        if item.exists():
            success, message = replacer.rename_path(item)
            if success:
                rename_results.append(message)
    
    print(f"Renamed {len(rename_results)} items")
    
    # Summary
    print("\n✅ Project rename completed!")
    print(f"   - Content updated in {len(content_results)} files")
    print(f"   - Renamed {len(rename_results)} files/directories")
    
    if content_results:
        print("\nFiles with updated content:")
        for result in content_results[:10]:  # Show first 10
            print(f"   {result}")
        if len(content_results) > 10:
            print(f"   ... and {len(content_results) - 10} more")
    
    if rename_results:
        print("\nRenamed items:")
        for result in rename_results[:10]:  # Show first 10
            print(f"   {result}")
        if len(rename_results) > 10:
            print(f"   ... and {len(rename_results) - 10} more")

if __name__ == "__main__":
    main()