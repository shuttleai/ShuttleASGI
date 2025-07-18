"""
This script allows to execute the same performance tests on multiple
versions of ShuttleASGI. It creates a temporary copy of the perf folder
to ensure that the same tests are executed at various points of the
Git history.

python perf/historyrun.py --commits 82ed065 1237b1e

# To use tags:
python perf/historyrun.py --commits v2.0.1 v2.1.0 v2.2.0 v2.3.0

# To skip compilation step (valid only when comparing commits whose Cython code is
# equivalent)
python perf/historyrun.py --commits current --no-memory --no-compile
---
See also the perfhistory.yml GitHub Workflow.
"""

import argparse
import logging
import platform
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

from perf.utils.md5 import md5_cython_files

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def copy_perf_code(temp_dir):
    """
    Copies the 'perf' folder into a temporary directory to ensure the same
    performance code is used across different commits.
    """
    source_dir = os.path.abspath("perf")  # Path to the 'perf' folder
    if not os.path.exists(source_dir):
        logger.error("Source directory '%s' does not exist.", source_dir)
        sys.exit(1)

    dest_dir = os.path.join(temp_dir, "perf")

    # Copy the 'perf' folder recursively
    shutil.copytree(source_dir, dest_dir)

    logger.debug("'perf' folder copied to temporary directory: %s", dest_dir)
    return dest_dir


def restore_perf_code(temp_dir):
    logger.debug("Replacing the local 'perf' folder with the backup...")

    # Path to the local 'perf' folder
    local_perf_dir = os.path.abspath("perf")

    # Delete the local 'perf' folder if it exists
    if os.path.exists(local_perf_dir):
        logger.debug("Deleting the local 'perf' folder: %s", local_perf_dir)
        shutil.rmtree(local_perf_dir)

    # Path to the backup 'perf' folder in the temporary directory
    source_dir = os.path.join(temp_dir, "perf")

    # Copy the backup 'perf' folder to the current directory
    shutil.copytree(source_dir, local_perf_dir)
    logger.debug("Restored 'perf' folder from backup: %s", source_dir)


@contextmanager
def gitcontext():
    branch = subprocess.check_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], universal_newlines=True
    ).strip()
    try:
        yield branch
    except KeyboardInterrupt:
        logger.info("User interrupted")
    except:
        logger.exception("Performance test failed.")
        # go back to the original branch
    logger.info("Returning to the original branch")
    subprocess.check_output(["git", "checkout", "-f", branch], universal_newlines=True)


def make_compile():
    python_implementation = platform.python_implementation()
    if python_implementation != "CPython":
        logger.info(
            "Skipping compilation because the command is not running for CPython. "
            "Implementat: %s",
            python_implementation,
        )
        return
    logger.info("Compiling ShuttleASGI extensions")
    subprocess.check_output(["make", "compile"], universal_newlines=True)


def run_tests(iterations: int, output_dir: str, times: int, memory: bool):
    logger.info("Running performance tests...")
    subprocess.run(
        [
            "python",
            "perf/main.py",
            "--iterations",
            str(iterations),
            "--output-dir",
            output_dir,
            "--times",
            str(times),
            "--memory" if memory else "--no-memory",
        ],
        check=True,
    )


def copy_results(source_dir, dest_dir):
    """
    Copies all files from the source directory to the destination directory.
    If the destination directory does not exist, it is created.
    """
    if not os.path.exists(source_dir):
        logger.error("Source directory '%s' does not exist.", source_dir)
        sys.exit(1)

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        logger.info("Created destination directory: %s", dest_dir)

    # Copy all files and subdirectories
    for item in os.listdir(source_dir):
        source_path = os.path.join(source_dir, item)
        dest_path = os.path.join(dest_dir, item)

        if os.path.isdir(source_path):
            shutil.copytree(source_path, dest_path)
        else:
            shutil.copy2(source_path, dest_path)

    logger.info("Copied all files from '%s' to '%s'", source_dir, dest_dir)


class CythonHash:
    """
    This is to read and store the MD5 hash of the Cython code, from the last
    compilation. This is to save time when repeating history runs, and when Cython code
    is not modified.
    """

    filename = ".cython-hash"

    @staticmethod
    def read_from_file() -> str:
        file = Path(CythonHash.filename)
        if file.exists():
            return file.read_text()
        return ""

    @staticmethod
    def store_in_file(value: str) -> None:
        file = Path(CythonHash.filename)
        file.write_text(value)


def main():
    parser = argparse.ArgumentParser(description="ShuttleASGI Performance Benchmarking")
    parser.add_argument(
        "--iterations", type=int, default=100000, help="Number of iterations"
    )
    parser.add_argument(
        "--times", type=int, default=5, help="How many runs for each commit"
    )
    parser.add_argument(
        "--commits",
        type=str,
        nargs="+",  # Accept one or more commit SHAs
        help="List of Git commit SHAs to benchmark",
    )
    parser.add_argument(
        "--memory",
        default=True,
        action=argparse.BooleanOptionalAction,
        help="Includes or skips memory benchmarks (included by default)",
    )
    parser.add_argument(
        "--compile",
        default=True,
        action=argparse.BooleanOptionalAction,
        help="Includes or skips the compilation step (included by default)",
    )
    args = parser.parse_args()

    if args.commits:
        logger.info(f"Commits to benchmark: {args.commits}")
    else:
        logger.info("No commits provided.")
        sys.exit(1)

    compiled_hash = CythonHash.read_from_file()
    current_hash = md5_cython_files()
    if current_hash == compiled_hash:
        logger.info("Restored the Cython files hash from the last compilation...")
    else:
        # The Cython code was modified since it was compiled for the last history run.
        # Discard it.
        compiled_hash = ""

    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "results"
        copy_perf_code(temp_dir)

        with gitcontext() as current_branch:
            for commit in args.commits:
                if commit.lower() in {"current", "last", "head"}:
                    commit = current_branch
                subprocess.check_output(
                    ["git", "checkout", "-f", commit], universal_newlines=True
                )

                logger.info("Checked out commit: %s", commit)
                if args.compile:
                    current_hash = md5_cython_files()
                    if compiled_hash == current_hash:
                        logger.info(
                            "Compilation is not needed, the Cython code is current. 🏇 ✨"
                        )
                    else:
                        make_compile()
                        compiled_hash = current_hash
                        CythonHash.store_in_file(current_hash)  # Store in file
                else:
                    logger.info(
                        "Compilation skipped. This is OK only to compare commits when "
                        "Cython code is not modified. ⚠️"
                    )
                restore_perf_code(temp_dir)
                run_tests(args.iterations, str(output_dir), args.times, args.memory)

        # Copy the results from output_dir to ./benchmark_results
        copy_results(str(output_dir), "./benchmark_results")
        logger.info("All done! ✨ 🍰 ✨")


if __name__ == "__main__":
    main()
