from pathlib import Path

from setuptools import setup

ROOT = Path(__file__).resolve().parents[2]

setup(
    name="aegis-rubric",
    version="0.1.0",
    packages=["rubric"],
    package_dir={"rubric": str(Path(__file__).parent)},
)
