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

class TestDeblink(object):
    def setup(self):
        self.points = mock_objects.iview_points_blinky()
        self.deblink = iview.Deblink(min_duration=50, max_duration=400)
    
    def test_find_all_candidates_does_so(self):
        all_candidates = self.deblink.all_blink_candidates(self.points)
        eq_(4, len(all_candidates)) # For now...

    def test_filter_for_length_does_so(self):
        all_candidates = self.deblink.all_blink_candidates(self.points)
        filtered = self.deblink.filter_for_length(all_candidates)
        eq_(1, len(filtered)) # For now!
        
    def test_expand_blink_forward(self):
        blinks = self.deblink.all_blink_candidates(self.points)
        b1 = blinks[0]
        expanded = self.deblink.expand_blink_dir(b1, self.points, True)
        eq_(150, expanded.end)
        
    def test_expand_blink_backward(self):
        blinks = self.deblink.all_blink_candidates(self.points)
        b = blinks[3]
        expanded = self.deblink.expand_blink_dir(b, self.points, False)
        eq_(233, expanded.start)
    
    def test_expand_blink_will_return_none(self):
        blinks = self.deblink.all_blink_candidates(self.points)
        b = blinks[0]
        expanded = self.deblink.expand_blink_dir(b, self.points, False)
        assert expanded is None
    
    def test_expand_blinks_works(self):
        blinks = self.deblink.all_blink_candidates(self.points)
        exp = self.deblink.expand_blinks(blinks, self.points)
        eq_(1, len(exp))
        
class TestDenoiseWindow(object):
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
    
    def test_window_apply_at_valid_indexes_interpolates(self):
        idx = 2
        prex = self.points[idx].x
        self.window.apply(idx)
        neq_(prex, self.points[idx].x)
        
        idx = 4
        prex1 = self.points[idx].x
        prex2 = self.points[idx+1].x
        prex3 = self.points[idx+2].x
        self.window.apply(idx)
        neq_(prex1, self.points[idx].x)
        neq_(prex2, self.points[idx+1].x)
        eq_(prex3, self.points[idx+2].x)

class TestDenoiseFilter(object):
    def setup(self):
        self.points = mock_objects.iview_points_noisy()
        self.flt = iview.Denoise(max_noise_samples = 2)
        self.filtered = self.flt.process(self.points)
    
    def test_denoise_denoises(self):
        eq_(self.points[0].x, self.filtered[0].x)
        neq_(self.points[2].x, self.filtered[2].x)
    
    def test_denoise_doesnt_change_time(self):
        eq_(self.points[0].time, self.filtered[0].time)
        eq_(self.points[2].time, self.filtered[2].time)
        