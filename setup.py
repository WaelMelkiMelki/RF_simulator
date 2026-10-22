from setuptools import setup, find_packages

setup(
    name="rf-simulator",
    version="0.1",
    python_requires=">=3.11",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
