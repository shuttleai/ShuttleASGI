from setuptools import Extension, setup

COMPILE_ARGS = ["-O2"]


setup(
    ext_modules=[
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
)
