import ez_setup
ez_setup.use_setuptools()


from setuptools import setup, find_packages
setup(
    name = "gazehound",
    version = "0.0.2",
    package_dir = {'':'src'},
    packages = find_packages('src'),
    
    entry_points = {
        'console_scripts': [
            'gazehound_test = gazehound.test:main'
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
    url = "http://code.google.com/p/gazehound",
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
