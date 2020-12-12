#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "dill",
    "micro-toolkit",
    "tqdm",
    "tensorflow>=1.15.0,<2.0.0",
    "seq2annotation",
    "tensorflow-serving-api>=1.15.0,<2.0.0"
]

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest>=3", "pytest-datadir"]

setup(
    author="Xiaoquan Kong",
    author_email="u1mail2me@gmail.com",
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="A cross framework machine leaning format and API specific for deploying.",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="deliverable_model",
    name="deliverable_model",
    packages=find_packages(include=["deliverable_model", "deliverable_model.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/howl-anderson/deliverable_model",
    version="0.6.3",
    zip_safe=False,
)
