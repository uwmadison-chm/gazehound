# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.
import copy


class Viewing(object):
    """Viewings represent a combination of presentations and view data."""
    def __init__(self, presentation = None, viewdata = None):
        self.presentation = presentation
        self.viewdata = viewdata
        
    
class Combiner(object):
    """Combines timelines of presentations with scanpath data"""
    def __init__(self, timeline = None, scanpath = None):
        self.timeline = timeline
        self.scanpath = scanpath
    
    def viewings(self):
        t2 = copy.copy(self.timeline)
        return t2