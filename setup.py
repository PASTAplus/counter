#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: setup.py

:Synopsis:

:Author:
    servilla

:Created:
    8/27/2020
"""
from os import path
from setuptools import setup


here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open(path.join(here, "LICENSE"), encoding="utf-8") as f:
    full_license = f.read()

setup(
    name="counter",
    version="2022.02.27",
    description="Reports data package and entity read counts, and more...",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="PASTA+ project",
    url="https://github.com/PASTAplus/counter",
    license=full_license,
    packages=["counter"],
    include_package_data=True,
    exclude_package_data={"": ["settings.py, properties.py, config.py"]},
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "click",
        "daiquiri",
        "lxml",
        "psycopg2",
        "requests",
        "sqlalchemy < 2",
    ],
    entry_points={"console_scripts": ["counter=counter.count:main"]},
    classifiers=["License :: OSI Approved :: Apache Software License"],
)


def main():
    return 0


if __name__ == "__main__":
    main()
