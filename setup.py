from pathlib import Path

from setuptools import find_packages, setup

ROOT = Path(__file__).parent
README = ROOT / "README.md"

setup(
    name="eli-lab-multimedia-framework",
    version="0.2.0.dev0",
    description="Production and asset-management utilities for the ELI LAB multimedia pipeline.",
    long_description=README.read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    python_requires=">=3.10",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "Pillow>=11.3,<13",
        "python-magic>=0.4.27,<0.5",
        "tkcalendar>=1.6.1,<2",
    ],
    include_package_data=True,
)
