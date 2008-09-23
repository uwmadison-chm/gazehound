# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

from __future__ import with_statement
from os import path
from gazehound import viewing, gazepoint
import mock_objects
from nose.tools import ok_, eq_

class TestTimelineScanpathCombiner(object):
    def setup(self):
        self.scanpath = mock_objects.smi_scanpath_spreadout()
        self.timeline = mock_objects.simple_timeline()
        
    def teardown(self):
        pass
        
    def test_combiner_returns_as_many_viewings_as_presentations(self):
        
        combiner = viewing.Combiner(
            timeline = self.timeline,
            scanpath = self.scanpath
        )
        
        viewings = combiner.viewings()
        eq_(len(viewings), len(self.timeline))
        
    def test_combiner_adds_scanpath_to_presentations(self):
        pass