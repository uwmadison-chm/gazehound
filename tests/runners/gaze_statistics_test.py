# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

from __future__ import with_statement
from gazehound.runners import gaze_statistics
from ..testutils import includes_
from nose.tools import *
from .. import mock_objects
import os
import StringIO

class TestGazeStatsOptionParser(object):
    def __init__(self):
        super(TestGazeStatsOptionParser, self).__init__()
        
    def setup(self):
        # Gather error messages to clean test output
        self.err_dump = StringIO.StringIO() 
        
        self.path_base = p = os.path.abspath(os.path.dirname(__file__)+"/..")
        self.example_path = self.path_base+'/examples/'
        self.normal_file = os.path.join(self.example_path, 'iview_normal.txt')
        self.presentations_file = os.path.join(
            self.example_path, 'presentation_tabs'
        )
        
    def teardown(self):
        self.err_dump.close()
        
    def test_analyzer_parses_filename(self):
        args = [__file__, self.normal_file]
        
        analyzer = gaze_statistics.GazeStatisticsOptionParser(args)
        includes_(analyzer.args, self.normal_file)
    
    @raises(SystemExit)
    def test_analyzer_fails_with_no_filename(self):
        args = [__file__]
        analyzer = gaze_statistics.GazeStatisticsOptionParser(args, 
            err = self.err_dump
        )
    
    @raises(SystemExit)
    def test_analyzer_fails_with_bogus_option(self):
        args = [__file__, '--bogus', 'bar']
        analyzer = gaze_statistics.GazeStatisticsOptionParser(args, 
            err = self.err_dump
        )
    
    def test_analyzer_parses_stimlui(self):
        args = [__file__, '--stimuli=foo', 'bar']
        analyzer = gaze_statistics.GazeStatisticsOptionParser(args)
        eq_(analyzer.options.stim_file, 'foo')

    @raises(SystemExit)
    def test_analyzer_fails_with_recenter_but_no_stimuli(self):
        args = [__file__, '--recenter-on=foo', 'bar']
        analyzer = gaze_statistics.GazeStatisticsOptionParser(args,
            err = self.err_dump
        )        

    def test_analyzer_parses_recenter_on(self):
        args = [__file__, '--stimuli=corge', '--recenter-on=foo', 'bar']
        analyzer = gaze_statistics.GazeStatisticsOptionParser(args)
        eq_(analyzer.options.recenter_on, 'foo')        
    
    def test_analyzer_parses_obt_dir(self):
        args = [__file__, '--stimuli=foo', '--obt-dir=.', 'bar']
        analyzer = gaze_statistics.GazeStatisticsOptionParser(args)
        assert analyzer.options.object_dir is not None
    
    @raises(SystemExit)
    def test_analyzer_errors_with_bogus_obt_dir(self):
        args = [__file__, '--stimuli=foo', '--obt-dir=bogus', 'bar']
        analyzer = gaze_statistics.GazeStatisticsOptionParser(args,
            err = self.err_dump
        )
    
    @raises(SystemExit)
    def test_analyzer_errors_when_obt_dir_specd_without_stimuli(self):
        args = [__file__, '--obt-dir=.', 'bar']
        analyzer = gaze_statistics.GazeStatisticsOptionParser(args,
            err = self.err_dump
        )
        
class TestGazeStatisticsRunner(object):
    def __init__(self):
        super(TestGazeStatisticsRunner, self).__init__()
    
    def setup(self):
        self.path_base = p = os.path.abspath(os.path.dirname(__file__)+"/..")
        self.example_path = self.path_base+'/examples/'
        self.scan_file = os.path.join(self.example_path, 'iview_normal.txt')
        self.stim_file = os.path.join(self.example_path, 'pres_tiny.txt')
        self.iv3_file = os.path.join(self.example_path, 'iview_3_small.txt')

    def test_runner_builds_timeline(self):
        args = [__file__, "--stimuli="+self.stim_file, self.scan_file]
        gsr = gaze_statistics.GazeStatsRunner(args)
        assert gsr.timeline is not None, "Timeline shouldn't be None"
        eq_(len(gsr.timeline), 2)
    
    def test_runner_timeline_has_pointpaths(self):
        args = [__file__, "--stimuli="+self.stim_file, self.scan_file]
        gsr = gaze_statistics.GazeStatsRunner(args)
        assert all(pres.pointpath is not None for pres in gsr.timeline), \
            "All presentations should have gaze data"
        assert all(len(pres.pointpath) > 0 for pres in gsr.timeline)
    
    def test_runner_reads_iview_3_files(self):
        args = [__file__, self.iv3_file]
        gsr = gaze_statistics.GazeStatsRunner(args)
        assert gsr.pointpath is not None
    
    def test_runner_combines_iview_3_files(self):
        args = [__file__, "--stimuli="+self.stim_file, self.iv3_file]
        gsr = gaze_statistics.GazeStatsRunner(args)
        assert all(pres.pointpath is not None for pres in gsr.timeline), \
            "All presentations should have gaze data"


class TestGazeStatisticsAnalyzer(object):
    def __init__(self):
        super(TestGazeStatisticsAnalyzer, self).__init__()
        
    
    def setup(self):
        self.pointpath = mock_objects.smi_pointpath_normal()
        self.timeline = mock_objects.tiny_viewings()
        self.gsa = gaze_statistics.GazeStatisticsAnalyzer(
            pointpath = self.pointpath,
            timeline = self.timeline
        )
        
    def test_gaze_stats_checker_returns_general_stats(self):
        stats = self.gsa.general_stats()
        assert stats is not None
    
    def test_gen_stats_counts_total_points(self):
        stats = self.gsa.general_stats()
        eq_(stats.total_points, len(self.pointpath))
        
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
        