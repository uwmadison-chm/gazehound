#!/usr/bin/env python
import ez_setup
ez_setup.use_setuptools()

from gazehound import version
from setuptools import setup, find_packages
setup(
    name = "gazehound",
    version = version.version_str(),
    package_dir = {'':'src'},
    packages = find_packages('src'),
    install_requires = [
        "numpy",
        "scipy"
    ],
    
    entry_points = {
        'console_scripts': [
            'scanpath_stats = gazehound.runners.gaze_statistics:main',
            'fixation_stats = gazehound.runners.fixation_statistics:main'
        ]
    },

    package_data = {
    },

    # metadata for upload to PyPI
    author = "Nathan Vack",
    author_email = "njvack@wisc.edu",
    description = ("Utilities for viewing and analyzing gaze tracking (and "+
        "eyetracking) data"),
    license = "GPL 2.0",
    keywords = "gazetracking eyetracking psychology science research",
    url = "http://github.com/njvack/gazehound",
    classifiers = (
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Information Analysis"
    ),
    test_suite = 'nose.collector'
)
