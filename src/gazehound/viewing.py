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
        if self.scanpath.uniformely_sampled:
            return self.__viewings_uniform()
        else:
            return self.__viewings_nonuniform()
    
    def __viewings_uniform(self):
        """ Extract viewings (fast) for uniformly-sampled scanpaths """
        t2 = copy.copy(self.timeline)
        for pres in t2:
            sp = copy.copy(self.scanpath)
            # Event times are in msec, scanpaths know samples_per_second
            start_idx = int(sp.samples_per_second*pres.start/1000.0)
            end_idx = int(sp.samples_per_second*pres.end/1000.0)
            sp.points = sp.points[start_idx:end_idx]
            pres.scanpath = sp
            
        return timeline.Timeline(t2)
    
    def __viewings_nonuniform(self):
        """ General case: extract viewings for nonuniform paths """
        t2 = copy.copy(self.timeline)
        for pres in t2:
            sp = copy.copy(self.scanpath)
            points = [p for p in self.scanpath
                if (p.time_midpoint() >= pres.start
                    and p.time_midpoint() < pres.end)]
            sp.points = points
            pres.scanpath = sp
        return timeline.Timeline(t2)
        