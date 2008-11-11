# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

from __future__ import with_statement
from os import path
from gazehound import viewing, gazepoint, shapes
import mock_objects
from nose.tools import ok_, eq_
from testutils import lt_, gt_

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
        # This test assures we've got non-None scanpaths in each pres
        combiner = viewing.Combiner(
            timeline = self.timeline,
            scanpath = self.scanpath
        )
        
        viewings = combiner.viewings()
        assert all(p.scanpath is not None for p in viewings)

    def test_combiner_adds_gazepoints_to_presentations(self):
        combiner = viewing.Combiner(
            timeline = self.timeline,
            scanpath = self.scanpath
        )
        
        viewings = combiner.viewings()
        assert all(len(p.scanpath) > 0 for p in viewings)
        
    def test_combiner_drops_out_of_bounds_points(self):
        # Some gazepoints are outside of the presentation timeline...
        combiner = viewing.Combiner(
            timeline = self.timeline,
            scanpath = self.scanpath
        )
        viewings = combiner.viewings()
        lt_(
            sum(len(pres.scanpath) for pres in viewings),
            len(self.scanpath)
        )
        
    def test_combiner_contains_all_points_when_in_bounds(self):
        combiner = viewing.Combiner(
            timeline = self.timeline.filled_list(),
            scanpath = self.scanpath
        )
        
        viewings = combiner.viewings()
        eq_(
            sum(len(pres.scanpath) for pres in viewings),
            len(self.scanpath)
        )
        
    def test_viewings_can_recenter(self):
        viewings = viewing.Combiner(
            timeline = self.timeline,
            scanpath = self.scanpath
        ).viewings()
        
        centered = viewings.recenter_on('stim1', 400, 300)
        eq_(len(centered.presentations), len(viewings.presentations))
        assert centered[0].scanpath[0].x != viewings[0].scanpath[0].x
        
    def test_viewings_will_recenter_with_bounding_rect(self):
        viewings = viewing.Combiner(
            timeline = self.timeline,
            scanpath = self.scanpath
        ).viewings()
        bounds = shapes.Rectangle(350, 500, 400, 600)
        centered = viewings.recenter_on('stim1', 400, 300, bounds = bounds)
        eq_(centered[0].scanpath[0].x, 400)
        eq_(centered[0].scanpath[0].y, 300)