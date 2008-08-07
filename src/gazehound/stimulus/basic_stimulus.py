# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

class BasicStimulus:
    def __init__(self, start=None, end=None, name=None):
        self.start = start
        self.end = end
        self.name = name
    
