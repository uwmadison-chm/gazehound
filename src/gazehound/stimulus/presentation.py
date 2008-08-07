# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

""" The generic stimulus presentation, providing start time, end time, and
name.
"""

class Presentation:
    def __init__(self, start=None, end=None, name=None):
        self.start = start
        self.end = end
        self.name = name


""" A picture-type stimulus. Generally also contains filename, type, width,
and height.
"""    
class Picture(Presentation):
    def __init__(self, start=None, end=None, name=None, type=None,
                width=None, height=None):
        Presentation.__init__(self, start, end, name)
        self.type = type
        self.width = width
        self.height = height

""" A 'nothing' type stimulus.
"""
class Blank(Presentation):
    def __init__(self, *args):
        Presentation.__init__(self, *args)