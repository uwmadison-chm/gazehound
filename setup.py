import ez_setup
ez_setup.use_setuptools()


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
    description = ("Utilities for viewing and analyzing gaze tracking (and "+
        "eyetracking) data"),
    license = "GPL 2.0",
    keywords = "gazetracking eyetracking psychology science research",
    url = "http://code.google.com/p/gazehound",
    classifiers = (
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Information Analysis"
    )
)
