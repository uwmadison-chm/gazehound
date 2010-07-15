# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
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
        self.pointpath = mock_objects.smi_pointpath_spreadout()
        self.timeline = mock_objects.simple_timeline()
        
    def teardown(self):
        pass
        
    def test_combiner_returns_as_many_viewings_as_events(self):
        combiner = viewing.Combiner(
            timeline = self.timeline,
            pointpath = self.pointpath
        )
        
        viewings = combiner.viewings()
        eq_(len(viewings), len(self.timeline))
        
    def test_combiner_adds_pointpath_to_events(self):
        # This test assures we've got non-None pointpaths in each pres
        combiner = viewing.Combiner(
            timeline = self.timeline,
            pointpath = self.pointpath
        )
        
        viewings = combiner.viewings()
        assert all(p.pointpath is not None for p in viewings)

    def test_combiner_adds_gazepoints_to_events(self):
        combiner = viewing.Combiner(
            timeline = self.timeline,
            pointpath = self.pointpath
        )
        
        viewings = combiner.viewings()
        assert all(len(p.pointpath) > 0 for p in viewings)
        
    def test_combiner_drops_out_of_bounds_points(self):
        # Some gazepoints are outside of the event timeline...
        combiner = viewing.Combiner(
            timeline = self.timeline,
            pointpath = self.pointpath
        )
        viewings = combiner.viewings()
        lt_(
            sum(len(pres.pointpath) for pres in viewings),
            len(self.pointpath)
        )
        
    def test_combiner_contains_all_points_when_in_bounds(self):
        combiner = viewing.Combiner(
            timeline = self.timeline.filled_list(),
            pointpath = self.pointpath
        )
        
        viewings = combiner.viewings()
        eq_(
            sum(len(pres.pointpath) for pres in viewings),
            len(self.pointpath)
        )
        
    def test_viewings_can_recenter(self):
        viewings = viewing.Combiner(
            timeline = self.timeline,
            pointpath = self.pointpath
        ).viewings()
        
        centered = viewings.recenter_on('stim1', 400, 300)
        eq_(len(centered.events), len(viewings.events))
        assert centered[0].pointpath[0].x != viewings[0].pointpath[0].x
        
    def test_viewings_will_recenter_with_bounding_rect(self):
        viewings = viewing.Combiner(
            timeline = self.timeline,
            pointpath = self.pointpath
        ).viewings()
        bounds = shapes.Rectangle(350, 500, 400, 600)
        centered = viewings.recenter_on('stim1', 400, 300, bounds = bounds)
        eq_(centered[0].pointpath[0].x, 400)
        eq_(centered[0].pointpath[0].y, 300)
        

class TestFixatedTimeline(object):
    def setup(self):
        self.fixations = mock_objects.smi_fixation_points()
        self.timeline = mock_objects.standard_timeline()
        self.viewings = viewing.Combiner(
            timeline = self.timeline,
            pointpath = self.fixations
        ).viewings()
    
    def test_timeline_and_fixations_are_not_empty(self):
        gt_(len(self.timeline), 0)
        eq_(len(mock_objects.smi_fixation_ary()), len(self.fixations))
    
    def test_viewings_gets_at_least_some_fixations(self):
        gt_(len(self.viewings), 0, "Viweings should not be empty.")
        gt_(sum(len(pres.pointpath) for pres in self.viewings), 0)
    
    def test_viewings_drops_fixations_outside_stimuli(self):
        lt_(
            sum(len(pres.pointpath) for pres in self.viewings),
            len(self.fixations)
        )
        
    def test_spot_check_hand_computed_fixation_counts(self):
        # First one, the "fixation" should have exactly one fix
        eq_(len(self.viewings[0].pointpath), 1)
        # And this should have 4
        eq_(len(self.viewings[1].pointpath), 4)
        #eq_(self.viewings[1].pointpath[-1], 1)
    
    