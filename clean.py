"""
This module will mimic what
clean:
	rm -rf dist/
	rm -rf build/
	rm -f shuttleasgi/*.c
	rm -f shuttleasgi/*.so
    rm -f shuttleasgi/*.pyd

does in a Makefile.
"""

import os
import shutil

def clean():
    # Remove dist/ directory
    if os.path.exists("dist/"):
        shutil.rmtree("dist/")

    # Remove build/ directory
    if os.path.exists("build/"):
        shutil.rmtree("build/")

    # Remove shuttleasgi/*.c
    for file in os.listdir("shuttleasgi/"):
        if file.endswith(".c"):
            os.remove(f"shuttleasgi/{file}")

    # Remove shuttleasgi/*.so
    for file in os.listdir("shuttleasgi/"):
        if file.endswith(".so"):
            os.remove(f"shuttleasgi/{file}")

    # Remove shuttleasgi/*.pyd
    for file in os.listdir("shuttleasgi/"):
        if file.endswith(".pyd"):
            os.remove(f"shuttleasgi/{file}")

if __name__ == "__main__":
    clean()