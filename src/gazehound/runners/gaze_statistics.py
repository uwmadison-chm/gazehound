# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

import sys
import os.path
from optparse import OptionParser
from gazehound import timeline, viewing, shapes
from gazehound.writers import delimited
from gazehound.readers.auto_scanpath import AutoScanpathReader
from gazehound.readers.timeline import TimelineReader

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
        
        parser.add_option(
            "--obt-dir", dest = "object_dir",
            help = "Find .OBT files in PATH. Requires --stimuli",
            metavar = "PATH"
        )
        
        parser.add_option(
            "--recenter-on", dest = "recenter_on",
            help = "Recenter when stimuli named NAME are shown",
            metavar = "NAME"
        )
        
        self.options, self.args = parser.parse_args(argv[1:])
            
        if len(self.args) == 0:
            parser.error("No scanpath file specified")

        if (self.options.recenter_on is not None and 
                self.options.stim_file is None):
            parser.error("You must use --stimuli with --recenter-on")
            
        if self.options.object_dir is not None:
            if not os.path.isdir(self.options.object_dir):
                parser.error(self.options.object_dir+" is not a directory")
            if self.options.stim_file is None:
                parser.error("You must use --stimuli with --obt_dir")  
                
        self.gaze_file = self.args[0]
        sys.stderr = err
        

class GazeStatsRunner(object):
    """docstring for GazeStatsRunner"""
    def __init__(self, argv):
        """ Construct the object graph for GazeStatsAnalyzer """
        super(GazeStatsRunner, self).__init__()
        op = GazeStatisticsOptionParser(argv)
        # Read and parse the gazestream

        ar = AutoScanpathReader()
        self.scanpath = ar.read_scanpath(filename=op.gaze_file)

        self.timeline = None
        
        if op.options.stim_file is not None:
            self.timeline = self.__build_timeline(op.options.stim_file)
            if op.options.object_dir is not None:
                r = shapes.ShapeReader(path = op.options.object_dir)
                dec = shapes.TimelineDecorator(r)
                self.timeline = dec.find_shape_files_and_add_to_timeline(
                    self.timeline
                )
            if op.options.recenter_on is not None:
                #TODO: Make these sepeficiable on the command line
                rx = 400
                ry = 300
                limiter = shapes.Rectangle(300, 200, 500, 400)
                self.timeline = self.timeline.recenter_on(
                    op.options.recenter_on, rx, ry, limiter
                )
            
        # And build the analyzer
        self.analyzer = GazeStatisticsAnalyzer(
            scanpath = self.scanpath,
            timeline = self.timeline
        )
    
    def print_analysis(self):
        gsw = delimited.GazeStatsWriter()
        gsw.write_header()
        gsw.write([self.analyzer.general_stats()])
        if self.timeline is not None:
            gsw.write(self.analyzer.timeline_stats())
        
    
    def __build_timeline(self, filename):
        """Build the timeline from a file."""
        reader = TimelineReader(filename=filename)
        timeline_with_points = viewing.Combiner(
            timeline = reader.timeline, scanpath = self.scanpath
        ).viewings()
        return timeline_with_points
        
class GazeStatisticsAnalyzer(object):
    
    def __init__(self, 
        scanpath,
        strict_valid_fun = None,
        scanpath_meta = None,
        timeline = []):
        super(GazeStatisticsAnalyzer, self).__init__()
        self.scanpath = scanpath
        self.timeline = timeline
        
        # TODO: Don't hardcode these.
        MAX_X = self.scanpath.headers['calibration_size'][0]
        MAX_Y = self.scanpath.headers['calibration_size'][1]

        SLOP_FRAC = 0.1
        X_SLOP = MAX_X*SLOP_FRAC
        Y_SLOP = MAX_Y*SLOP_FRAC
        strict_rect = shapes.Rectangle(0, 0, MAX_X, MAX_Y)
        lax_rect = shapes.Rectangle(
            -X_SLOP, -Y_SLOP, MAX_X+X_SLOP, MAX_Y+Y_SLOP)
        
        def default_valid(shape, point):
            return (point in shape) and (tuple(point) <> (0,0))

        def svf(point):
            return default_valid(strict_rect, point)

        def lvf(point):
            return default_valid(lax_rect, point)
            
        self.strict_valid_fun = svf
        self.lax_valid_fun = lvf
                        
    def general_stats(self):
        """Return a GazeStats containing basic data about the scanpath"""
        time_idx = self.scanpath.measures.index('time')
        data = GazeStats(
            presented = 'screen',
            area = 'all',
            total_points = len(self.scanpath),
            start_ms = self.scanpath[0][time_idx],
            end_ms = self.scanpath[-1][time_idx],
            valid_strict = len(self.scanpath.points_matching(
                self.strict_valid_fun
            )),
            valid_lax = len(self.scanpath.points_matching(
                self.lax_valid_fun
            ))
        )
        
        data.points_in = data.valid_strict
        data.points_out = data.total_points - data.valid_strict
        
        return data
        
    def timeline_stats(self):
        """ 
        Return a list of GazeStats containing data about all the events
        in the timeline.
        """
        
        data = []
        doshapes = hasattr(self.timeline, 'has_shapes')
        for pres in self.timeline:
            stats = GazeStats(
                presented = pres.name,
                area = 'all',
                total_points = len(pres.scanpath),
                start_ms = pres.start,
                end_ms = pres.end,
                valid_strict = len(pres.scanpath.points_matching(
                    self.strict_valid_fun
                )),
                valid_lax = len(pres.scanpath.points_matching(
                    self.lax_valid_fun
                ))
            )
            stats.points_in = stats.valid_strict
            stats.points_out = stats.total_points - stats.valid_strict
            data.append(stats)
            if doshapes:
                for ss in self.shape_stats(pres):
                    data.append(ss)
                    pass
        return data
    
    def shape_stats(self, pres):
        stats_list = []
        if pres.shapes is None:
            return[GazeStats(
                presented = pres.name, 
                area = "Can't read shape file")
            ]
        for s in pres.shapes:
            stats = GazeStats(
                presented = pres.name,
                area = s.name,
                total_points = len(pres.scanpath),
                start_ms = pres.start,
                end_ms = pres.end,
                valid_strict = len(pres.scanpath.points_matching(
                    self.strict_valid_fun
                )),
                valid_lax = len(pres.scanpath.points_matching(
                    self.lax_valid_fun
                ))
            )
                            
            stats.points_in = len(pres.scanpath.points_within(s))
            stats.points_out = stats.total_points - stats.points_in
            stats_list.append(stats)
            
        return stats_list

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
        