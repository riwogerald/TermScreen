#!/usr/bin/env python3
"""
Setup script for Terminal Screen Renderer
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements if they exist
def read_requirements():
    """Read requirements from requirements.txt if it exists"""
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="terminal-screen-renderer",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A robust terminal screen renderer that processes binary command streams",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/terminal-screen-renderer",
    py_modules=["renderer", "demo", "utils"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics",
        "Topic :: System :: Shells",
        "Topic :: Terminals",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires=">=3.6",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800"
        ]
    },
    entry_points={
        "console_scripts": [
            "termscreen=renderer:main",
            "termscreen-demo=demo:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="terminal renderer binary graphics curses ascii-art",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/terminal-screen-renderer/issues",
        "Source": "https://github.com/yourusername/terminal-screen-renderer",
        "Documentation": "https://github.com/yourusername/terminal-screen-renderer/blob/main/README.md"
    }
)
