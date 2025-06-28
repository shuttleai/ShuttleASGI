#!/usr/bin/env python3
"""
Test runner script for ShuttleASGI
"""

import os
import subprocess
import sys
from pathlib import Path

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
    
    print("🧪 Running ShuttleASGI tests")
    print("=" * 30)
    
    # Install pytest if not available
    try:
        subprocess.run([str(python_exe), "-c", "import pytest"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("📦 Installing pytest...")
        subprocess.run([str(python_exe), "-m", "pip", "install", "pytest"], check=True)
    
    # Run tests
    try:
        subprocess.run([str(python_exe), "-m", "pytest", "tests/", "-v"], check=True)
        print("\n🎉 All tests passed!")
        return True
    except subprocess.CalledProcessError:
        print("\n❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)