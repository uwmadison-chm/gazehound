# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

# This is really just going to determine that the detector runs,
# not that its behavior is particularly good. Validating testcases
# is hard for this kind of stuff.

from gazehound.filters import saccade

from .. import mock_objects
from nose.tools import *
from ..testutils import *

class TestSaccadeDetector(object):
    def setup(self):
        self.points = mock_objects.iview_scanpath_blinky()

    def test_detector_runs(self):
        sd = saccade.AdaptiveDetector(scanpath=self.points)