#!/usr/bin/env python

from distutils.core import setup

setup(
    name="scoreNormalization",
    version="1.0.0",
    description="Generic ETL pipeline for use by torque-site competitions",
    author="Lever for Change",
    author_email="intentionally@left.blank.com",
    url="https://github.com/LeverForChange/scoreNormalization",
    packages=["scoreNormalization"],
    install_requires=["torqueclient", "pandas", "numpy", "seaborn", "matplotlib"],
)
