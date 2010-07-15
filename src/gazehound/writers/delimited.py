# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

import sys
import csv


class DelimitedWriter(object):
    """Writes iterable things into text files"""

    def __init__(self, mapping, out = sys.stdout, delimiter = "\t"):
        """ Creates a new delimited writer."""
        super(DelimitedWriter, self).__init__()
        self.mapping = mapping
        self.out = out
        self.writer = csv.writer(out, delimiter=delimiter)
        self.delimiter = delimiter

    def write_header(self):
        headers = [elem[0] for elem in self.mapping]
        self.writer.writerow(headers)

    def write(self, data):
        for row in data:
            row_mapped = [elem[1](row) for elem in self.mapping]
            self.writer.writerow(row_mapped)


class GazeStatsWriter(DelimitedWriter):
    """Writes gaze stats items into a delimited file"""

    mapper = [
        ('Presented', lambda s: s.presented),
        ('Area', lambda s: s.area),
        ('Start', lambda s: "%.3f" % (s.start_ms/1000.0)),
        ('End', lambda s: "%.3f" % (s.end_ms/1000.0)),
        ('Total points', lambda s: s.total_points),
        ('Points in', lambda s: s.points_in),
        ('Points out', lambda s: s.points_out),
        ('Valid strict', lambda s: s.valid_strict),
        ('Valid lax', lambda s: s.valid_lax),
        ('% in', lambda s: '%.1f' % (100*dfnz(s.points_in, s.total_points))),
        ('% valid strict',
            lambda s: '%.1f' % (100*dfnz(s.valid_strict, s.total_points))),
        ('% valid lax',
            lambda s: '%.1f' % (100*dfnz(s.valid_lax, s.total_points)))]

    def __init__(self, out = sys.stdout, delimiter = "\t"):
        super(GazeStatsWriter, self).__init__(
            GazeStatsWriter.mapper, out, delimiter)


class FixationStatsWriter(DelimitedWriter):
    """Writes gaze stats items into a delimited file"""

    mapper = [
        ('Presented', lambda s: s.presented),
        ('Area', lambda s: s.area),
        ('Start', lambda s: "%.3f" % (s.start_ms/1000.0)),
        ('End', lambda s: "%.3f" % (s.end_ms/1000.0)),
        ('Total fixations', lambda s: s.total_fixations),
        ('Time fixating', lambda s: (s.time_fixating/1000.0)),
        ('Time in', lambda s: (s.time_in/1000.0)),
        ('Time out', lambda s: (s.time_out/1000.0)),
        ('Fixations/second', lambda s: ("%.3f" % s.fixations_per_second)),
        ('Distance between fixations', lambda s: s.distance_between_fixations),
    ]

    def __init__(self, out = sys.stdout, delimiter = "\t"):
        super(FixationStatsWriter, self).__init__(
            FixationStatsWriter.mapper, out, delimiter)


def dfnz(num1, num2):
    if num2 == 0:
        return 0
    return float(num1)/num2
