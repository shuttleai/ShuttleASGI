"""
This file is used to specify Python extensions, which are used when using Cython.
Extensions are used only if the current runtime is CPython and only if there is not an
environment variable: `SHUTTLEASGI_NO_EXTENSIONS=1`.
The logic is to support PyPy. See:
https://github.com/Neoteroi/ShuttleASGI/issues/539#issuecomment-2888631226
"""

import os
from setuptools import Extension, setup
import platform

COMPILE_ARGS = ["-O2"]

# Check for environment variable to skip extensions
skip_ext = os.environ.get("SHUTTLEASGI_NO_EXTENSIONS", "0") == "1"


if platform.python_implementation() == "CPython" and not skip_ext:
    ext_modules = [
        Extension(
            "shuttleasgi.url",
            ["shuttleasgi/url.c"],
            extra_compile_args=COMPILE_ARGS,
        ),
        Extension(
            "shuttleasgi.exceptions",
            ["shuttleasgi/exceptions.c"],
            extra_compile_args=COMPILE_ARGS,
        ),
        Extension(
            "shuttleasgi.headers",
            ["shuttleasgi/headers.c"],
            extra_compile_args=COMPILE_ARGS,
        ),
        Extension(
            "shuttleasgi.cookies",
            ["shuttleasgi/cookies.c"],
            extra_compile_args=COMPILE_ARGS,
        ),
        Extension(
            "shuttleasgi.contents",
            ["shuttleasgi/contents.c"],
            extra_compile_args=COMPILE_ARGS,
        ),
        Extension(
            "shuttleasgi.messages",
            ["shuttleasgi/messages.c"],
            extra_compile_args=COMPILE_ARGS,
        ),
        Extension(
            "shuttleasgi.scribe",
            ["shuttleasgi/scribe.c"],
            extra_compile_args=COMPILE_ARGS,
        ),
        Extension(
            "shuttleasgi.baseapp",
            ["shuttleasgi/baseapp.c"],
            extra_compile_args=COMPILE_ARGS,
        ),
    ]
else:
    ext_modules = []

setup(ext_modules=ext_modules)
