# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

from __future__ import with_statement
from optparse import OptionParser
from .. import readers, timeline, viewing
from ..writers import delimited
import sys

def main(argv = None):
    if argv is None:
        argv = sys.argv
        
    gsr = GazeStatsRunner(argv)
    gsr.print_analysis()
    

class GazeStatisticsOptionParser(object):
    """
    Parses the command line options for the analyzer
    """
    
    def __init__(self, argv, err = sys.stderr):
        old_err = err
        sys.stderr = err
        super(GazeStatisticsOptionParser, self).__init__()
        self.argv = argv
        parser = OptionParser()
        parser.add_option(
            "--stimuli", dest = "stim_file", 
            help = "Read stimulus timings from FILE",
            metavar = "FILE"
        )
        
        self.options, self.args = parser.parse_args(argv[1:])
        if len(self.args) == 0:
            parser.error("No scanpath file specified")
        self.gaze_file = self.args[0]
        sys.stderr = err
        

class GazeStatsRunner(object):
    """docstring for GazeStatsRunner"""
    def __init__(self, argv):
        """ Construct the object graph for GazeStatsAnalyzer """
        super(GazeStatsRunner, self).__init__()
        op = GazeStatisticsOptionParser(argv)
        # Read and parse the gazestream
        
        with open(op.gaze_file) as gf:
            ir = readers.IViewReader(gf.readlines())
            self.file_data = ir
            self.scanpath = ir.scanpath()

        self.timeline = None
        
        if hasattr(op.options, 'stim_file'):
            self.timeline = self.__build_timeline(op.options.stim_file)
            
        # And build the analyzer
        self.analyzer = GazeStatisticsAnalyzer(
            scanpath = self.scanpath
        )
    
    def print_analysis(self):
        gsw = delimited.GazeStatsWriter()
        gsw.write_header()
        gsw.write([self.analyzer.general_stats()])
        
    
    def __build_timeline(self, filename):
        """Build the timeline from a file."""
        timeline = None
        with open(filename) as f:
            lines = [l.strip() for l in f.readlines()]
            tr = readers.TimelineReader(lines)
            ttl = tr.timeline()
            timeline = viewing.Combiner(
                timeline = ttl, scanpath = self.scanpath
            ).viewings()
        return timeline
        

class GazeStatisticsAnalyzer(object):
    
    def __init__(self, 
        scanpath = None,
        strict_valid_fun = None,
        scanpath_meta = None):
        super(GazeStatisticsAnalyzer, self).__init__()
        self.scanpath = scanpath
        
        # TODO: Don't hardcode these.
        MAX_X = 800
        MAX_Y = 600
        
        def default_valid(x_width, y_width, slop_frac, point):
            xslop = x_width*slop_frac
            yslop = y_width*slop_frac
            max_x = x_width+xslop
            min_x = 0-xslop
            max_y = y_width+yslop
            min_y = 0-yslop
            
            return ((point.x >= min_x and point.x < max_x) and
            (point.y >= min_y and point.y < max_y) and not
            (point.x == 0 and point.y == 0
            ))

        def svf(point):
            return default_valid(MAX_X, MAX_Y, 0, point)

        def lvf(point):
            return default_valid(MAX_X, MAX_Y, .1, point)
            
        self.strict_valid_fun = svf
        self.lax_valid_fun = lvf
    

    def general_stats(self):
        """Return a dict containing basic data about the scanpath"""
        
        data = GazeStats(
            presented = 'screen',
            area = 'all',
            total_points = len(self.scanpath),
            start_ms = self.scanpath[0].time,
            end_ms = self.scanpath[-1].time,
            valid_strict = len(self.scanpath.valid_points(
                self.strict_valid_fun
            )),
            valid_lax = len(self.scanpath.valid_points(
                self.lax_valid_fun
            ))
        )
        
        data.points_in = data.valid_strict
        data.points_out = data.total_points - data.valid_strict
        
        return data
        

class GazeStats(object):
    """A data structure containing stats about a scanpath"""
    def __init__(self, 
    presented = None, area = None, start_ms = 0, end_ms = 0, total_points = 0, 
    points_in = 0, points_out = 0, valid_strict = 0, valid_lax = 0
    ):
        super(GazeStats, self).__init__()
        self.presented = presented
        self.area = area
        self.start_ms = start_ms
        self.end_ms = end_ms
        self.total_points = total_points
        self.points_in = points_in
        self.points_out = points_out
        self.valid_strict = valid_strict
        self.valid_lax = valid_lax
        