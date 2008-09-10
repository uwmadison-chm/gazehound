# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

from __future__ import with_statement
from presentation import *

class Timeline(object):
    """A representation of a series of presentations."""
    def __init__(self, presentations = None, min_length = 0):
        self.presentations = presentations
        self.min_length = min_length
        
    
    def filled_list(self):
        """Return a list of presentations with a presentation in every
        millisecond. Gaps in self.presentations are filled with Blanks.
        """
        
        if self.presentations is None or len(self.presentations) < 1:
            return []
        
        full_list = []
        time = 0
        cur_pres = Blank()
        i = iter(self.presentations)
        next_pres = i.next()
        
        try:
            while next_pres:
                if time < next_pres.start:
                    cur_pres = Blank(start = time, end = (next_pres.start - 1))
                else:
                    cur_pres = next_pres
                full_list.append(cur_pres)
                if time >= next_pres.start:
                    next_pres = i.next()
                time = cur_pres.end + 1
        except StopIteration:
            # This is the normal way out of the loop
            pass
        if cur_pres.end < self.min_length:
            full_list.append(Blank(
                start = cur_pres.end+1, end = self.min_length))
        return full_list
        