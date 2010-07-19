# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

import sys
import os.path
import math
from optparse import OptionParser
from gazehound import readers, timeline, viewing, shapes
from gazehound.writers import delimited
from gazehound.readers import iview


def main(argv = None):
    if argv is None:
        argv = sys.argv

    gsr = FixationStatsRunner(argv)
    gsr.print_analysis()


class FixationStatisticsOptionParser(object):
    """
    Parses the command line options for the analyzer
    """

    def __init__(self, argv, err=sys.stderr):
        old_err = err
        sys.stderr = err
        super(FixationStatisticsOptionParser, self).__init__()
        self.argv = argv
        parser = OptionParser()

        parser.add_option(
            "--stimuli", dest="stim_file",
            help="Read stimulus timings from FILE",
            metavar="FILE")

        parser.add_option(
            "--obt-dir", dest="object_dir",
            help="Find .OBT files in PATH. Requires --stimuli",
            metavar="PATH")

        parser.add_option(
            "--recenter-on", dest="recenter_on",
            help="Recenter when stimuli named NAME are shown",
            metavar="NAME")

        self.options, self.args = parser.parse_args(argv[1:])

        if len(self.args) == 0:
            parser.error("No fixation file specified")

        if (self.options.recenter_on is not None and
                self.options.stim_file is None):
            parser.error("You must use --stimuli with --recenter-on")

        if self.options.object_dir is not None:
            if not os.path.isdir(self.options.object_dir):
                parser.error(self.options.object_dir+" is not a directory")
            if self.options.stim_file is None:
                parser.error("You must use --stimuli with --obt-dir")

        self.fix_file = self.args[0]
        sys.stderr = err


class FixationStatsRunner(object):
    """docstring for FixationStatsRunner"""

    def __init__(self, argv):
        """ Construct the object graph for FixationStatsAnalyzer """
        super(FixationStatsRunner, self).__init__()
        op = FixationStatisticsOptionParser(argv)
        # Read and parse the gazestream

        ir = readers.iview.IViewFixationReader(filename=op.fix_file)
        self.file_data = ir
        self.pointpath = ir.pointpath()

        self.timeline = None

        if op.options.stim_file is not None:
            self.timeline = self.__build_timeline(op.options.stim_file)
            if op.options.object_dir is not None:
                r = shapes.ShapeReader(path=op.options.object_dir)
                dec = shapes.TimelineDecorator(r)
                self.timeline = dec.find_shape_files_and_add_to_timeline(
                    self.timeline)

            if op.options.recenter_on is not None:
                #TODO: Make these sepeficiable on the command line
                rx = 400
                ry = 300
                limiter = shapes.Rectangle(300, 200, 500, 400)
                self.timeline = self.timeline.recenter_on(
                    op.options.recenter_on, rx, ry, limiter)

        # And build the analyzer
        self.analyzer = FixationStatisticsAnalyzer(
            pointpath=self.pointpath,
            timeline=self.timeline)

    def print_analysis(self):
        gsw = delimited.FixationStatsWriter()
        gsw.write_header()
        gsw.write([self.analyzer.general_stats()])
        if self.timeline is not None:
            gsw.write(self.analyzer.timeline_stats())

    def __build_timeline(self, filename):
        """Build the timeline from a file."""
        reader = readers.timeline.TimelineReader(filename=filename)
        timeline_with_points = viewing.Combiner(
            timeline=reader.timeline, pointpath=self.pointpath).viewings()
        return timeline_with_points


class FixationStatisticsAnalyzer(object):

    def __init__(self,
        pointpath=None,
        strict_valid_fun=None,
        pointpath_meta=None,
        timeline=[]):
        super(FixationStatisticsAnalyzer, self).__init__()
        self.pointpath = pointpath
        self.timeline = timeline

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
            (point.x == 0 and point.y == 0))

        def svf(point):
            return default_valid(MAX_X, MAX_Y, 0, point)

        def lvf(point):
            return default_valid(MAX_X, MAX_Y, .1, point)

        self.strict_valid_fun = svf
        self.lax_valid_fun = lvf

        def in_fun(shape, point):
            return (point.x, point.y) in shape

        self.in_fun = in_fun

    def general_stats(self):
        """Return a FixationStats containing basic data about the pointpath"""

        data = FixationStats(
            presented='screen',
            area='all',
            start_ms=self.pointpath[0].time,
            end_ms=self.pointpath[-1].time+self.pointpath[-1].duration,
            total_fixations=len(self.pointpath),
            time_fixating=self.__time_fixating(self.pointpath),
            fixations_per_second=self.__fixations_per_second(self.pointpath),
            distance_between_fixations=self.__distance_between_fixations(
                self.pointpath))

        data.time_in = data.time_fixating
        data.time_out = (data.end_ms - data.start_ms) - data.time_fixating

        return data

    def timeline_stats(self):
        """
        Return a list of FixationStats containing data about all the events
        in the timeline.
        """

        data = []
        doshapes = hasattr(self.timeline, 'has_shapes')
        for pres in self.timeline:
            if len(pres.pointpath) == 0:
                stats = FixationStats(
                    presented=pres.name,
                    area='all')
            else:
                stats = FixationStats(
                    presented=pres.name,
                    area='all',
                    start_ms=pres.pointpath[0].time,
                    end_ms=pres.pointpath[-1].time+pres.pointpath[-1].duration,
                    total_fixations=len(pres.pointpath),
                    time_fixating=self.__time_fixating(pres.pointpath),
                    fixations_per_second=self.__fixations_per_second(
                        pres.pointpath),
                    distance_between_fixations=self.__distance_between_fixations(
                        pres.pointpath))

                stats.time_in = stats.time_fixating
                stats.time_out = ((stats.end_ms - stats.start_ms) -
                                    stats.time_fixating)
            data.append(stats)
            if doshapes:
                for ss in self.shape_stats(pres):
                    data.append(ss)
                    pass
        return data

    def shape_stats(self, pres):
        stats_list = []
        if pres.shapes is None:
            return[FixationStats(
                presented=pres.name,
                area="Can't read shape file")]
        for s in pres.shapes:
            if len(pres.pointpath) == 0:
                stats = FixationStats(
                    presented=pres.name,
                    area=s.name)
            else:
                stats = FixationStats(
                    presented=pres.name,
                    area=s.name,
                    start_ms=pres.pointpath[0].time,
                    end_ms=pres.pointpath[-1].time+pres.pointpath[-1].duration,
                    total_fixations=len(pres.pointpath),
                    time_fixating=self.__time_fixating(pres.pointpath),
                    fixations_per_second=self.__fixations_per_second(
                        pres.pointpath),
                    distance_between_fixations=self.__distance_between_fixations(
                        pres.pointpath))

                def f(point):
                    return self.in_fun(s, point)

                stats.time_in = sum(p.duration
                                    for p in pres.pointpath.valid_points(f))
                stats.time_out =(stats.end_ms - stats.start_ms) - stats.time_in
            stats_list.append(stats)

        return stats_list

    def __total_fixations(self, pointpath):
        """The total number of fixations in a point path"""
        return len(pointpath)

    def __time_fixating(self, pointpath):
        """Time spent fixating during a point path"""
        return sum(p.duration for p in pointpath)

    def __pp_duration(self, pointpath):
        if len(pointpath) == 0:
            return 0
        start = pointpath[0].time
        end = pointpath[-1].time+pointpath[-1].duration
        return end-start

    def __fixations_per_second(self, pointpath):
        """ Number of fixations divided by seconds fixating """
        tf = self.__time_fixating(pointpath)*1000.0
        if tf == 0:
            return 0
        return (
            float(self.__total_fixations(pointpath)) /
            (self.__pp_duration(pointpath)/1000.0))

    def __distance_between_fixations(self, pointpath):
        if len(pointpath) < 2:
            return 0

        def dist(p1, p2):
            return math.sqrt((p1.x-p2.x)**2 + (p1.y-p2.y)**2)

        dsum = 0
        for i in range(1, len(pointpath)):
            dsum += dist(pointpath[i-1], pointpath[i])
        return float(dsum) / (len(pointpath)-1)


class FixationStats(object):
    """A data structure containing stats about a pointpath"""

    def __init__(self,
    presented=None, area=None, start_ms=0, end_ms=0,
    total_fixations=0, time_fixating=0, time_in=0, time_out=0,
    fixations_per_second=0, distance_between_fixations=0):
        super(FixationStats, self).__init__()
        self.presented = presented
        self.area = area
        self.start_ms = start_ms
        self.end_ms = end_ms
        self.total_fixations = total_fixations
        self.time_fixating = time_fixating
        self.time_in = time_in
        self.time_out = time_out
        self.fixations_per_second = fixations_per_second
        self.distance_between_fixations = distance_between_fixations
