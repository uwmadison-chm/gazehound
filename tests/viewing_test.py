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
import numpy as np

class TestTimelineScanpathCombiner(object):
    def setup(self):
        self.scanpath = mock_objects.iview_scanpath_blinky()
        self.timeline = mock_objects.simple_timeline_for_blinky()
        
    def test_combiner_returns_as_many_viewings_as_events(self):
        combiner = viewing.Combiner(
            timeline = self.timeline,
            scanpath = self.scanpath
        )
        
        viewings = combiner.viewings()
        eq_(len(viewings), len(self.timeline))
        
    def test_combiner_adds_scanpath_to_events(self):
        # This test assures we've got non-None scanpaths in each pres
        combiner = viewing.Combiner(
            timeline = self.timeline,
            scanpath = self.scanpath
        )
        
        viewings = combiner.viewings()
        assert all(p.scanpath is not None for p in viewings)
        assert all(len(p.scanpath) > 0 for p in viewings)
    
    def test_combiner_adds_gazepoints_to_events(self):
        combiner = viewing.Combiner(
            timeline = self.timeline,
            scanpath = self.scanpath
        )
        
        viewings = combiner.viewings()
        assert all(len(p.scanpath) > 0 for p in viewings)
        
    def test_combiner_drops_out_of_bounds_points(self):
        # Some gazepoints are outside of the event timeline...
        combiner = viewing.Combiner(
            timeline = self.timeline,
            scanpath = self.scanpath
        )
        viewings = combiner.viewings()
        lt_(
            sum(len(pres.scanpath) for pres in viewings),
            len(self.scanpath)
        )
                
    def test_viewings_can_recenter(self):
        viewings = viewing.Combiner(
            timeline = self.timeline,
            scanpath = self.scanpath
        ).viewings()
        
        centered = viewings.recenter_on('stim1', 400, 300)
        eq_(len(centered.events), len(viewings.events))
        x_i = self.scanpath.measure_index('x')
        assert centered[0].scanpath[0][x_i] != viewings[0].scanpath[0][x_i]
        
    def test_viewings_will_recenter_with_bounding_rect(self):
        viewings = viewing.Combiner(
            timeline = self.timeline,
            scanpath = self.scanpath
        ).viewings()
        
        bounds = shapes.Rectangle(100, 100, 600, 600)
        centered = viewings.recenter_on('stim1', 400, 300, 
            bounds=bounds, method="median")
        
        pre_xy = viewings[0].scanpath.as_array(('x', 'y'))
        post_xy = centered[0].scanpath.as_array(('x', 'y'))
        eq_(pre_xy.shape, post_xy.shape)
        eq_(0, np.sum(pre_xy == post_xy))
        

class TestFixatedTimeline(object):
    def setup(self):
        self.fixations = mock_objects.smi_fixation_points()
        self.timeline = mock_objects.standard_timeline()
        self.viewings = viewing.Combiner(
            timeline = self.timeline,
            scanpath = self.fixations
        ).viewings()
    
    def test_timeline_and_fixations_are_not_empty(self):
        gt_(len(self.timeline), 0)
        eq_(len(mock_objects.smi_fixation_ary()), len(self.fixations))
    
    def test_viewings_gets_at_least_some_fixations(self):
        gt_(len(self.viewings), 0, "Viweings should not be empty.")
        gt_(sum(len(pres.scanpath) for pres in self.viewings), 0)
    
    def test_viewings_drops_fixations_outside_stimuli(self):
        lt_(
            sum(len(pres.scanpath) for pres in self.viewings),
            len(self.fixations)
        )
        
    def test_spot_check_hand_computed_fixation_counts(self):
        # First one, the "fixation" should have exactly one fix
        eq_(len(self.viewings[0].scanpath), 1)
        # And this should have 4
        eq_(len(self.viewings[1].scanpath), 4)
        #eq_(self.viewings[1].scanpath[-1], 1)
    
    