"""
Packaging instructions
"""

from setuptools import find_packages, setup
from validator.version import __version__

with open("README.md") as f:
    README = f.read()

with open("LICENSE") as f:
    LICENSE = f.read()

with open("requirements.txt") as f:
    ALL_REQS = f.read().split("\n")

setup(
    name="IMBIE3 Validator",
    version=__version__,
    description="IMBIE3 input data validation tool",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Mark Pattle for isardSAT",
    author_email="mark.pattle@isardsat.co.uk",
    # url="https://github.com/isardsat/template-python-library",
    license=LICENSE,
    # keywords="sample climate era5 climatology",
    packages=find_packages(exclude=("tests", "usage-example")),
    # package_dir={"samplepackage": "samplepackage"}, # to uncomment if data to add to the package
    # package_data={"samplepackage": ["data/*.json"]},# to uncomment if data to add to the package
    install_requires=ALL_REQS,
    entry_points={"console_scripts": ["imbie-validate = validator.cli:main"]},
    include_package_data=True,
)
