# -*- coding: utf-8 -*-

import pathlib
import re

from setuptools import setup

ROOT = pathlib.Path(__file__).parent


try:
    VERSION = re.findall(
        r'^__version__\s*=\s*"([^"]*)"',
        (ROOT / "steam" / "ext" / "tf2" / "__init__.py").read_text(),
        re.MULTILINE,
    )[0]
except IndexError:
    raise RuntimeError("Version is not set")

if VERSION.endswith(("a", "b")) or "rc" in VERSION:
    # try to find out the commit hash if checked out from git, and append
    # it to __version__ (since we use this value from setup.py, it gets
    # automatically propagated to an installed copy as well)
    try:
        import subprocess

        out = subprocess.getoutput("git rev-list --count HEAD")
        if out:
            version = f"{VERSION}{out.strip()}"
        out = subprocess.getoutput("git rev-parse --short HEAD")
        if out:
            version = f"{VERSION}+g{out.strip()}"
    except Exception:
        pass

README = (ROOT / "README.md").read_text(encoding="utf-8")
REQUIREMENTS = (ROOT / "requirements.txt").read_text().splitlines()


setup(
    name="steam-ext-tf2",
    author="Gobot1234",
    url="https://github.com/Gobot1234/steam-ext-tf2",
    project_urls={
        "Issue tracker": "https://github.com/Gobot1234/steam-ext-tf2/issues",
    },
    version=VERSION,
    packages=["steam.ext.tf2", "steam.ext.tf2.protobufs"],
    license="MIT",
    description="An extension for steam.py to interact with the Team Fortress 2 Game Coordinator",
    long_description=README,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=REQUIREMENTS,
    python_requires=">=3.7.0",
    download_url=f"https://github.com/Gobot1234/steam-ext-tf2/archive/{VERSION}.tar.gz",
    keywords="tf2 team-fortress steam.py steam steamio steam-api",
    classifiers=[
        "Development Status :: 2 - Alpha",
        "Framework :: AsyncIO",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
)
