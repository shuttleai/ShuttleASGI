import subprocess
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# List of commands
commands = [
    "cython shuttleasgi/url.pyx",
    "cython shuttleasgi/exceptions.pyx",
    "cython shuttleasgi/headers.pyx",
    "cython shuttleasgi/cookies.pyx",
    "cython shuttleasgi/contents.pyx",
    "cython shuttleasgi/messages.pyx",
    "cython shuttleasgi/scribe.pyx",
    "cython shuttleasgi/baseapp.pyx",
    "python setup.py build_ext --inplace",
    "python setup.py sdist",
    "python setup.py bdist_wheel",
]

# Execute each command
for command in commands:
    process = subprocess.run(command, shell=True, check=True)
    if process.returncode != 0:
        print(f"Command failed: {command}")
    else:
        print(f"Command succeeded: {command}")

pypi_token = os.getenv("PYPI_TOKEN")

# Upload to PyPI
twine = subprocess.run(f"twine upload dist/* -u __token__ -p {pypi_token} --non-interactive", shell=True, check=True)
if twine.returncode != 0:
    print("Twine failed")
else:
    print("Twine succeeded")
