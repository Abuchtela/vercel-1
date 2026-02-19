"""
Setup script for ClawMode Integration.
"""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="clawmode-integration",
    version="0.1.0",
    description="ClawMode Integration - Economic tracking for nanobot agents",
    author="ClawWork Team",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "clawmode=clawmode_integration.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
