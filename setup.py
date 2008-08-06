from setuptools import setup, find_packages
setup(
    name = "gazehound",
    version = "0.0.1",
    packages = find_packages(),

    package_data = {
    },

    # metadata for upload to PyPI
    author = "Nathan Vack",
    author_email = "njvack@wisc.edu",
    description = "Utilities for viewing and analyzing gaze tracking (and eyetracking) data",
    license = "GPL 2.0",
    keywords = "gazetracking eyetracking  world example examples",
    url = "http://code.google.com/p/gazehound",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
)
