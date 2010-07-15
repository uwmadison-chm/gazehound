# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

import copy

from gazehound.event import *


class Timeline(object):
    """A reevent of a series of events."""

    def __init__(self, events = None, min_length = 0):
        self.events = events
        self.min_length = min_length

    def __len__(self):
        return len(self.events)

    def __iter__(self):
        return self.events.__iter__()

    def __getitem__(self, i):
        return self.events[i]

    def filled_list(self):
        """Return a list of events with a event in every
        millisecond. Gaps in self.events are filled with Blanks.
        """

        if self.events is None or len(self.events) < 1:
            return []

        full_list = []
        time = 0
        cur_pres = Blank()
        i = iter(self.events)
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

    def recenter_on(self, name, x_center, y_center, bounds=None):
        newtl = copy.deepcopy(self)
        x_offset, y_offset = 0, 0
        for pres in newtl.events:
            if hasattr(pres, 'pointpath'):
                if pres.name == name:
                    x_offset, y_offset = self.__recenter_point(
                        pres, x_offset, y_offset, x_center, y_center, bounds)
                pres.pointpath = pres.pointpath.recenter_by(x_offset, y_offset)
        return newtl

    def __recenter_point(
        self, pres, cur_x_offset, cur_y_offset, cx, cy, bounds=None):
        xoff, yoff = cur_x_offset, cur_y_offset
        sp = pres.pointpath
        if bounds is not None:
            sp = sp.points_within(bounds)
        m = sp.mean()
        if m is not None:
            xoff, yoff = int(cx-m[0]), int(cy-m[1])
        return (xoff, yoff)

    def valid(self):
        """
        Ensure every event is valid, that event start times
        increase monotonically, and that no times overlap.
        """

        def valid_pres(pres):
            pres.valid()

        invalids = filter(valid_pres, self.events)
        if len(invalids) > 0:
            return False

        # Handle the case where we won't be able to compare
        if len(self.events) < 2:
            return True

        prev_end = self.events[0].end
        for p in self.events[1:]:
            if p.start <= prev_end:
                return False
            prev_end = p.end

        # Passed all tests. We're valid!
        return True
