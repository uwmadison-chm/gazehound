# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.
import copy
from gazehound import timeline, gazepoint


class Combiner(object):
    """Combines timelines of eventss with scanpath data"""

    def __init__(self, timeline=None, scanpath=None):
        self.timeline = timeline
        self.scanpath = scanpath

    def viewings(self):
        t2 = copy.copy(self.timeline)
        for pres in t2:
            points = [p for p in self.scanpath
                if (p.time_midpoint() >= pres.start
                    and p.time_midpoint() < pres.end)]
            pres.scanpath = gazepoint.Scanpath(points)
        return timeline.Timeline(t2)
