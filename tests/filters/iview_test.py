# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

from gazehound.filters import iview

from .. import mock_objects
from nose.tools import eq_
from ..testutils import neq_, gt_, lt_, gte_, lte_, includes_

class TestDenoiseWindow(object):
    def __init__(self):
        super(TestDenoiseWindow, self).__init__()
    
    def setup(self):
        self.points = mock_objects.iview_points_noisy()
        self.window = iview.Denoise.Window(self.points)
    
    def test_window_reports_points_to_correct(self):
        pts = self.window.points_to_correct(0)
        eq_(0, len(pts))
        pts = self.window.points_to_correct(2)
        eq_(1, len(pts))
        pts = self.window.points_to_correct(4)
        eq_(2, len(pts))
    
    def test_window_finds_interp_points(self):
        pts = self.window.interp_points(2, 1)
        eq_(pts[0].time, 16)
        eq_(pts[1].time, 50)
        pts = self.window.interp_points(4, 2)
        eq_(pts[0].time, 50)
        eq_(pts[1].time, 100)
    
    def test_window_find_none_for_points_at_boundaries(self):
        pts = self.window.interp_points(0,1)
        assert pts is None
        pts = self.window.interp_points(13,2)
        assert pts is None
    
    def test_windows_finds_none_for_large_gaps(self):
        pts = self.window.interp_points(7,2)
        assert pts is None
    
    def test_window_apply_at_invalid_index_does_nothing(self):
        idx = 0
        prex = self.points[idx].x
        self.window.apply(idx)
        eq_(prex, self.points[idx].x)
        
        idx = 7
        prex = self.points[idx].x
        self.window.apply(idx)
        eq_(prex, self.points[idx].x)
    
    def test_window_apply_at_valid_index_interpolates(self):
        idx = 2
        prex = self.points[idx].x
        self.window.apply(idx)
        neq_(prex, self.points[idx].x)
        