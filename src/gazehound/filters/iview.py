# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

from gazehound.event import Blink
from gazehound.timeline import Timeline

from copy import deepcopy

class Deblink(object):

    # Literature suggests we're unlikely to se blinks less than 50ms or more
    # than 400ms. Paging through data suggests the same.
    def __init__(self, min_duration=50, max_duration=400, 
        start_dy_threshold=15, end_dy_threshold=5):
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.start_dy_threshold = start_dy_threshold
        self.end_dy_threshold = end_dy_threshold

    def deblink(self, pointpath):
        """
        Interpolates blinks out of pointpath.

        Interpolation is done by taking the point immediately before the blink
        and using its interpolable values for the rest of the points during
        the blink. Not using any averaging -- saccades during blinks are
        common, and averaging-type methods seem wrong to me here.
        """
        blinks = self.blinks(pointpath)
        pc = deepcopy(pointpath)
        for b in blinks:
            # Interpolate from the point before start_index -- no averaging.
            if b.start_index > 0:
                prev_pt = pc[b.start_index-1]
                for point in pc[(b.start_index):(b.end_index+1)]:
                    # +1 needed to get last point of blink
                    point.interpolate_from(prev_pt)
        return pc

    def blinks(self, pointpath):
        """
        Return a Timeline of Blinks. Each blink will have a start_index
        and end_index field, which point to the first and last indices in
        pointpath of a blink event.
        In other words, the point before start_index and the point after
        end_index are guaranteed to have good, interpolable data.
        Currently, the "guaranteed valid data" window is actually one point
        wider -- but that may not remain true in future versions.
        """
        candidates = self.all_blink_candidates(pointpath)
        expanded = self.expand_blinks(candidates, pointpath)
        filtered = self.filter_for_length(expanded)
        deduped = self.deduplicate(filtered)
        return deduped

    def all_blink_candidates(self, pointpath):
        candidates = []
        current = None
        for i in range(len(pointpath)):
            point = pointpath[i]
            if point.x == 0 and point.y == 0:
                # It's blank!
                if current is None:
                    current = Blink(
                        start=point.time, end=point.computed_end,
                        name = "blink_%s" % (point.time))
                    current.start_index = i
                    current.end_index = i
                else:
                    # Add to the current blink
                    current.end = point.computed_end
                    current.end_index = i
            else:
                if current is not None:
                    candidates.append(current)
                    current = None
        return Timeline(events=candidates)

    def deduplicate(self, timeline):
        new_blinks = []
        for blink in timeline:
            if len(new_blinks) == 0:
                new_blinks.append(blink)
            else:
                if new_blinks[-1].start != blink.start:
                    new_blinks.append(blink)
        return Timeline(events=new_blinks)

    def expand_blinks(self, blinks, pointpath):
        expanded = [self.expand_blink_bidir(b, pointpath) for b in blinks]
        expanded = [b for b in expanded if b is not None]

        return Timeline(events = expanded)

    def expand_blink_dir(self, blink, pointpath, forward=True):
        """
        Return a new Blink with end time (and indexes) set to
        next area of pointpath with a stable y value.
        If no such area exists, return None
        """
        b = deepcopy(blink)
        if forward:
            idx = b.end_index
        else:
            idx = b.start_index

        next_idx = self.__stable_yval_idx(pointpath, idx, forward)
        if next_idx is None:
            b = None
        elif forward:
            next_idx -= 1
            b.end_index = next_idx
            b.end = pointpath[next_idx].time
        else:
            next_idx += 1
            b.start_index = next_idx
            b.start = pointpath[next_idx].time
            
        return b

    def expand_blink_bidir(self, blink, pointpath):
        bf = self.expand_blink_dir(blink, pointpath, False)
        if bf is not None:
            bf = self.expand_blink_dir(bf, pointpath, True)
        return bf

    def __stable_yval_idx(self, pointpath, start_index, forward=True):
        i1 = start_index
        i2 = i1
        if forward:
            step = 1
            dy_thresh = self.end_dy_threshold
        else:
            step = -1
            dy_thresh = self.start_dy_threshold
        i2 += step
        
        while i2 >= 0 and i2 < len(pointpath):
            p1 = pointpath[i1]
            p2 = pointpath[i2]
            dy = abs(p1.y - p2.y)
            if (dy <= dy_thresh and p1.y != 0 and p2.y != 0):
                # print("%s %s %s %s %s" % (p1.time, p1.y, p2.y, dy, forward))
                return i1 
            i1 = i2
            i2 += step
        # If we're here, we ran off the end of pointpath
        return None

    def filter_for_length(self, timeline):
        """ Does not alter timeline, returns a copy. """
        return Timeline(events = [
            ev for ev in timeline if (
                ev.duration >= self.min_duration and
                ev.duration <= self.max_duration)])


class Denoise(object):
    """
    Interpolates out little noise blips from iview data. Not nearly as
    sophisticated as Deblink. Should be run before Deblink.
    """

    def __init__(self, max_noise_samples=2):
        self.max_noise_samples = max_noise_samples

    def process(self, pointpath):
        """
        Runs a deblinking on the pointpath. Returns a copy of pointpath --
        does not modify it.
        """
        pp = deepcopy(pointpath)
        win = self.Window(pp, self.max_noise_samples)
        for i in range(len(pp)):
            win.apply(i)
        return pp

    class Window(object):
        """ The thing that's going to slid along and correct noise """

        def __init__(self, pointpath, max_noise_len = 2):
            self.pointpath = pointpath
            self.max_noise_len = max_noise_len

        def points_to_correct(self, pos):
            points = []
            for i in range(self.max_noise_len):
                point = self.pointpath[pos+i]
                if not point.standard_valid():
                    points.append(point)
                else:
                    break # Don't allow gaps
            return points

        def interp_points(self, pos, width):
            vals = None
            try:
                if pos > 0 and width > 0:
                    vals = (self.pointpath[pos-1], self.pointpath[pos+width])
                    if not (vals[0].standard_valid() and
                            vals[1].standard_valid()):
                        vals = None
            except IndexError:
                vals = None
            return vals

        def apply(self, pos):
            """
            Modifies self.pointpath, either interpolating at potision
            pos or doing nothing.
            Return the next position
            """
            needs_fixin = self.points_to_correct(pos)
            interps = self.interp_points(pos, len(needs_fixin))
            if interps is not None:
                for p in needs_fixin:
                    for a in p.interp_attrs:
                        # Compute an interpolated value and set it.
                        val = 0.5*(
                            getattr(interps[0], a) + getattr(interps[0], a))
                        setattr(p, a, val)
