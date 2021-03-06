# -*- coding: utf-8 -*-

import os

from setuptools import find_packages, setup

install_requires = [
    "Click>=7.0",
    "PyYAML>=5.1.2",
    "yamlordereddictloader",
    "jsonschema>=3.0.0",
    "semver>=2.8.1",
    "wings",
    "requests",
]


# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def find_package_data(dirname):
    def find_paths(dirname):
        items = []
        for fname in os.listdir(dirname):
            path = os.path.join(dirname, fname)
            if os.path.isdir(path):
                items += find_paths(path)
            elif not path.endswith(".py") and not path.endswith(".pyc"):
                items.append(path)
        return items

    items = find_paths(dirname)
    return [os.path.relpath(path, dirname) for path in items]


version = {}
with open("src/wcm/__init__.py") as fp:
    exec(fp.read(), version)


setup(
    name="wcm",
    version=version["__version__"],
    author="Rajiv Mayani",
    author_email="mayani@isi.edu",
    description=__doc__,
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    license="Apache-2",
    url="https://github.com/mintproject/wcm",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Science/Research",
        "Operating System :: Unix",
    ],
    entry_points={"console_scripts": ["wcm = wcm.__main__:cli"]},
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=["wcm.tests*"]),
    package_data={"wcm": find_package_data("src/wcm")},
    exclude_package_data={"wcm": ["tests/*"]},
    zip_safe=False,
    install_requires=install_requires,
    python_requires=">=3.5.0",
)
