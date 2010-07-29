# coding: utf8
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
        self.points = mock_objects.iview_scanpath_blinky()
        self.deblink = iview.Deblink(
            min_duration=50, max_duration=400,
            start_dy_threshold=20, end_dy_threshold=20)

    def test_find_all_candidates_does_so(self):
        all_candidates = self.deblink.all_blink_candidates(self.points)
        eq_(4, len(all_candidates)) # For now...

    def test_filter_for_length_does_so(self):
        all_candidates = self.deblink.all_blink_candidates(self.points)
        filtered = self.deblink.filter_for_length(all_candidates)
        eq_(1, len(filtered)) # For now!

    def test_expand_blink_bidir_works(self):
        blinks = self.deblink.all_blink_candidates(self.points)
        b = blinks[3]
        expanded = self.deblink.expand_blink_bidir(b, self.points)
        eq_(233, expanded.start)
        eq_(350, expanded.end)

    def test_expand_blinks_works(self):
        blinks = self.deblink.all_blink_candidates(self.points)
        exp = self.deblink.expand_blinks(blinks, self.points)
        eq_(1, len(exp))

    def test_blinks_works(self):
        blinks = self.deblink.blinks(self.points)
        eq_(1, len(blinks))
        b = blinks[0]
        eq_(233, b.start)
        eq_(350, b.end)

    def test_deblink_interpolates(self):
        deblinked = self.deblink.deblink(self.points)
        t_idx = self.points.measure_index('time')
        x_idx = self.points.measure_index('x')
        pt = deblinked[13]
        eq_(216, pt[t_idx]) # For reference
        eq_(pt[x_idx], deblinked[14][x_idx])
        eq_(pt[x_idx], deblinked[19][x_idx])
        neq_(pt[x_idx], deblinked[22][x_idx]) # After the blink!

    def test_problem_candidates(self):
        pp = mock_objects.iview_problem_blink()
        all_candidates = self.deblink.all_blink_candidates(pp)
        eq_(1, len(all_candidates))
        b = all_candidates[0]
        eq_(6450, all_candidates[0].start)
        b_exp = self.deblink.expand_blink_bidir(b, pp)
        eq_(6434, b_exp.start)

    def test_problem_deblink(self):
        pp = mock_objects.iview_problem_blink()
        deblinked = self.deblink.deblink(pp)
        blinks = self.deblink.blinks(pp)
        x_idx = pp.measure_index('x')
        eq_(1, len(blinks))
        eq_(6434, blinks[0].start)
        tr = deblinked[4] # Target reference
        eq_(tr[x_idx], deblinked[5][x_idx])

    def test_asymmetric_thresholds(self):
        pp = mock_objects.iview_problem_blink()
        blinks = self.deblink.blinks(pp)
        eq_(6584, blinks[0].end)
        # Lower the end threshold; the blink should get longer
        self.deblink.end_dy_threshold = 5
        blinks = self.deblink.blinks(pp)
        eq_(6600, blinks[0].end)


class TestDenoiseFilter(object):
    def setup(self):
        self.points = mock_objects.iview_points_noisy()
        self.flt = iview.Denoise(max_noise_samples = 2)
        self.filtered = self.flt.process(self.points)

    def test_denoise_denoises(self):
        x_idx = self.points.measure_index('x')
        eq_(self.points[0][x_idx], self.filtered[0][x_idx])
        neq_(self.points[2][x_idx], self.filtered[2][x_idx])

    def test_denoise_doesnt_change_time(self):
        t_idx = self.points.measure_index('time')
        eq_(self.points[0][t_idx], self.filtered[0][t_idx])
        eq_(self.points[2][t_idx], self.filtered[2][t_idx])
