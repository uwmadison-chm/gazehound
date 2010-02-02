# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

from __future__ import with_statement
from gazehound.runners import fixation_statistics
from gazehound import viewing
from ..testutils import includes_
from nose.tools import *
from .. import mock_objects
import os
import StringIO

class TestFixationStatsOptionParser(object):
    def __init__(self):
        pass
        
    def setup(self):
        # Gather error messages to clean test output
        self.err_dump = StringIO.StringIO() 
        
        self.path_base = p = os.path.abspath(os.path.dirname(__file__)+"/..")
        self.example_path = self.path_base+'/examples/'
        self.normal_file = os.path.join(self.example_path, 'fixations.txt')
        self.presentations_file = os.path.join(
            self.example_path, 'presentation_tabs'
        )
        
    def teardown(self):
        self.err_dump.close()
        
    def test_analyzer_parses_filename(self):
        args = [__file__, self.normal_file]
        
        analyzer = fixation_statistics.FixationStatisticsOptionParser(args)
        includes_(analyzer.args, self.normal_file)
        eq_(analyzer.fix_file, self.normal_file)
    
    @raises(SystemExit)
    def test_analyzer_fails_with_no_filename(self):
        args = [__file__]
        analyzer = fixation_statistics.FixationStatisticsOptionParser(args, 
            err = self.err_dump
        )
    
    @raises(SystemExit)
    def test_analyzer_fails_with_bogus_option(self):
        args = [__file__, '--bogus', 'bar']
        analyzer = fixation_statistics.FixationStatisticsOptionParser(args, 
            err = self.err_dump
        )
    
    @raises(SystemExit)
    def test_analyzer_fails_with_recenter_but_no_stimuli(self):
        args = [__file__, '--recenter-on=foo', 'bar']
        analyzer = fixation_statistics.FixationStatisticsOptionParser(args,
            err = self.err_dump
        )        
    
    def test_analyzer_parses_recenter_on(self):
        args = [__file__, '--stimuli=corge', '--recenter-on=foo', 'bar']
        analyzer = fixation_statistics.FixationStatisticsOptionParser(args)
        eq_(analyzer.options.recenter_on, 'foo')        
    
    def test_analyzer_parses_stimlui(self):
        args = [__file__, '--stimuli=foo', 'bar']
        analyzer = fixation_statistics.FixationStatisticsOptionParser(args)
        eq_(analyzer.options.stim_file, 'foo')
    
    def test_analyzer_parses_obt_dir(self):
        args = [__file__, '--stimuli=foo', '--obt-dir=.', 'bar']
        analyzer = fixation_statistics.FixationStatisticsOptionParser(args)
        assert analyzer.options.object_dir is not None
    
    @raises(SystemExit)
    def test_analyzer_errors_with_bogus_obt_dir(self):
        args = [__file__, '--stimuli=foo', '--obt-dir=bogus', 'bar']
        analyzer = fixation_statistics.FixationStatisticsOptionParser(args,
            err = self.err_dump
        )
    
    @raises(SystemExit)
    def test_analyzer_errors_when_obt_dir_specd_without_stimuli(self):
        args = [__file__, '--obt-dir=.', 'bar']
        analyzer = fixation_statistics.FixationStatisticsOptionParser(args,
            err = self.err_dump
        )
        
class TestFixationStatisticsRunner(object):
    
    def setup(self):
        self.path_base = p = os.path.abspath(os.path.dirname(__file__)+"/..")
        self.example_path = self.path_base+'/examples/'
        self.scan_file = os.path.join(self.example_path, 'fixations.txt')
        self.stim_file = os.path.join(self.example_path, 'presentation_tabs.txt')

    def test_runner_builds_timeline(self):
        args = [__file__, "--stimuli="+self.stim_file, self.scan_file]
        gsr = fixation_statistics.FixationStatsRunner(args)
        assert gsr.timeline is not None, "Timeline shouldn't be None"
        eq_(len(gsr.timeline), 6)
    
    def test_runner_timeline_has_pointpaths(self):
        args = [__file__, "--stimuli="+self.stim_file, self.scan_file]
        gsr = fixation_statistics.FixationStatsRunner(args)
        assert all(pres.pointpath is not None for pres in gsr.timeline), \
            "All presentations should have gaze data"


class TestFixationStatisticsAnalyzer(object):

    def setup(self):
        self.pointpath = mock_objects.smi_fixation_points()
        self.timeline = viewing.Combiner(
            timeline = mock_objects.standard_timeline(), 
            pointpath = self.pointpath
        ).viewings()
        
        self.gsa = fixation_statistics.FixationStatisticsAnalyzer(
            pointpath = self.pointpath,
            timeline = self.timeline
        )
        
    def test_gaze_stats_checker_returns_general_stats(self):
        stats = self.gsa.general_stats()
        assert stats is not None
    
    def test_gen_stats_counts_total_points(self):
        stats = self.gsa.general_stats()
        eq_(stats.total_fixations, len(self.pointpath))
        
    def test_gen_stats_knows_start_and_end_times(self):
        stats = self.gsa.general_stats()
        eq_(stats.start_ms, 18750)
        eq_(stats.end_ms, 34717)
        
