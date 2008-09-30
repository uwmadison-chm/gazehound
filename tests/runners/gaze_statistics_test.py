# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

from __future__ import with_statement
from gazehound.runners import gaze_statistics
from ..testutils import includes_
from nose.tools import eq_
from .. import mock_objects
import os

class TestGazeStatsOptionParser(object):
    def __init__(self):
        super(TestGazeStatsOptionParser, self).__init__()
        
    def setup(self):
        self.path_base = p = os.path.abspath(os.path.dirname(__file__)+"/..")
        self.example_path = self.path_base+'/examples/'
        self.normal_file = os.path.join(self.example_path, 'iview_normal.txt')
        
    def teardown(self):
        pass
        
    def test_analyzer_parses_filename(self):
        args = [__file__, self.normal_file]
        
        analyzer = gaze_statistics.GazeStatisticsOptionParser(args)
        includes_(analyzer.args, self.normal_file)
        

class TestGazeStatisticsAnalyzer(object):
    def __init__(self):
        super(TestGazeStatisticsAnalyzer, self).__init__()
        
    
    def setup(self):
        self.scanpath = mock_objects.smi_scanpath_normal()
        self.gsa = gaze_statistics.GazeStatisticsAnalyzer(
            scanpath = self.scanpath
        )
        
    def test_gaze_stats_checker_returns_general_stats(self):
        stats = self.gsa.general_stats()
        assert stats is not None
    
    def test_gen_stats_counts_total_points(self):
        stats = self.gsa.general_stats()
        eq_(stats.total_points, len(self.scanpath))
        
    def test_gen_stats_knows_start_and_end_times(self):
        stats = self.gsa.general_stats()
        eq_(stats.start_ms, 0)
        eq_(stats.end_ms, 200)
        
    def test_gen_stats_detects_strict_invalid_points(self):
        stats = self.gsa.general_stats()
        # I know this from looking at the file.
        invalid_count = 8
        eq_(stats.valid_strict, stats.total_points - invalid_count)

    def test_gen_stats_detects_lax_invalid_points(self):
        stats = self.gsa.general_stats()
        # I know this from looking at the file.
        invalid_count = 7
        eq_(stats.valid_lax, stats.total_points - invalid_count)
        