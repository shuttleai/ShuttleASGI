#!/usr/bin/env python3
"""
Build script for ShuttleASGI
Compiles Cython files and builds extensions
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False

def main():
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Check if we're in a virtual environment
    venv_path = project_root / ".venv"
    if os.name == 'nt':
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"
    
    if not python_exe.exists():
        print("❌ Virtual environment not found. Run 'python scripts/setup-dev.py' first.")
        return False
    
    print("🔨 Building ShuttleASGI")
    print("=" * 30)
    
    # Compile Cython files
    cython_files = [
        "shuttleasgi/url.pyx",
        "shuttleasgi/exceptions.pyx",
        "shuttleasgi/headers.pyx", 
        "shuttleasgi/cookies.pyx",
        "shuttleasgi/contents.pyx",
        "shuttleasgi/messages.pyx",
        "shuttleasgi/scribe.pyx",
        "shuttleasgi/baseapp.pyx",
        "shuttleasgi/middlewares/shuttle_headers.pyx"
    ]
    
    for pyx_file in cython_files:
        if Path(pyx_file).exists():
            if not run_command(f"{python_exe} -m cython {pyx_file}", f"Compiling {pyx_file}"):
                print(f"⚠️  Warning: Failed to compile {pyx_file}")
    
    # Build extensions
    if not run_command(f"{python_exe} setup.py build_ext --inplace", "Building C extensions"):
        return False
    
    print("\n🎉 Build complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)