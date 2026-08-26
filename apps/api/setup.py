from pathlib import Path

from setuptools import find_packages, setup

setup(
    name="aegis-api",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.30.0",
        "pydantic>=2.7.0",
        "httpx>=0.27.0",
    ],
    python_requires=">=3.11",
)
