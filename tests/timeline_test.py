# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

# Hooray for with / as blocks! I miss ruby though :(
from __future__ import with_statement
from os import path
from gazehound.stimulus import presentation, timeline

class TestTimeline(object):
    def setup(self):
        p = path.abspath(path.dirname(__file__))
        # All of these should generate the same number of lines...
        with open(path.join(p, "examples/presentation_tabs.txt")) as f:
            self.lines = f.readlines()

        self.reader = presentation.DelimitedReader(self.lines)
        self.reader.lines_to_skip = 1
        self.presentations = self.reader.make_presentations()
    
    def test_timeline_full_returns_list_with_blanks(self):
        t = timeline.Timeline(presentations = self.presentations)
        list = t.filled_list()
        assert len(list) == 12
        
    def test_timeline_full_adds_blank_if_min_length_requires(self):
        t = timeline.Timeline(
            presentations = self.presentations,
            min_length = 75000)
            
        list = t.filled_list()
        assert len(list) == 13