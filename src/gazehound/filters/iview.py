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

import numpy as np

class Deblink(object):

    # Literature suggests we're unlikely to se blinks less than 50ms or more
    # than 400ms. Paging through data suggests the same.
    def __init__(self, min_duration=50, max_duration=400, 
        start_dy_threshold=15, end_dy_threshold=5):
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.start_dy_threshold = start_dy_threshold
        self.end_dy_threshold = end_dy_threshold

    def deblink(self, scanpath):
        """
        Interpolates blinks out of scanpath.

        Interpolation is done by taking the point immediately before the blink
        and using its interpolable values for the rest of the points during
        the blink. Not using any averaging -- saccades during blinks are
        common, and averaging-type methods seem wrong to me here.
        """
        blinks = self.blinks(scanpath)
        pc = deepcopy(scanpath)
        for b in blinks:
            # Interpolate from the point before start_index -- no averaging.
            if b.start_index > 0:
                prev_pt = pc[b.start_index-1]
                for point in pc[(b.start_index):(b.end_index+1)]:
                    # +1 needed to get last point of blink
                    point.interpolate_from(prev_pt)
        return pc

    def blinks(self, scanpath):
        """
        Return a Timeline of Blinks. Each blink will have a start_index
        and end_index field, which point to the first and last indices in
        scanpath of a blink event.
        In other words, the point before start_index and the point after
        end_index are guaranteed to have good, interpolable data.
        Currently, the "guaranteed valid data" window is actually one point
        wider -- but that may not remain true in future versions.
        """
        candidates = self.all_blink_candidates(scanpath)
        expanded = self.expand_blinks(candidates, scanpath)
        filtered = self.filter_for_length(expanded)
        deduped = self.deduplicate(filtered)
        return deduped

    def all_blink_candidates(self, scanpath):
        candidates = []
        current = None
        for i in range(len(scanpath)):
            point = scanpath[i]
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

    def expand_blinks(self, blinks, scanpath):
        expanded = [self.expand_blink_bidir(b, scanpath) for b in blinks]
        expanded = [b for b in expanded if b is not None]

        return Timeline(events = expanded)

    def expand_blink_dir(self, blink, scanpath, forward=True):
        """
        Return a new Blink with end time (and indexes) set to
        next area of scanpath with a stable y value.
        If no such area exists, return None
        """
        b = deepcopy(blink)
        if forward:
            idx = b.end_index
        else:
            idx = b.start_index

        next_idx = self.__stable_yval_idx(scanpath, idx, forward)
        if next_idx is None:
            b = None
        elif forward:
            next_idx -= 1
            b.end_index = next_idx
            b.end = scanpath[next_idx].time
        else:
            next_idx += 1
            b.start_index = next_idx
            b.start = scanpath[next_idx].time
            
        return b

    def expand_blink_bidir(self, blink, scanpath):
        bf = self.expand_blink_dir(blink, scanpath, False)
        if bf is not None:
            bf = self.expand_blink_dir(bf, scanpath, True)
        return bf

    def __stable_yval_idx(self, scanpath, start_index, forward=True):
        i1 = start_index
        i2 = i1
        if forward:
            step = 1
            dy_thresh = self.end_dy_threshold
        else:
            step = -1
            dy_thresh = self.start_dy_threshold
        i2 += step
        
        while i2 >= 0 and i2 < len(scanpath):
            p1 = scanpath[i1]
            p2 = scanpath[i2]
            dy = abs(p1.y - p2.y)
            if (dy <= dy_thresh and p1.y != 0 and p2.y != 0):
                # print("%s %s %s %s %s" % (p1.time, p1.y, p2.y, dy, forward))
                return i1 
            i1 = i2
            i2 += step
        # If we're here, we ran off the end of scanpath
        return None

    def filter_for_length(self, timeline):
        """ Does not alter timeline, returns a copy. """
        return Timeline(events = [
            ev for ev in timeline if (
                ev.duration >= self.min_duration and
                ev.duration <= self.max_duration)])


class Denoise(object):
    """
    Interpolates out little noise blips from iview data. Operates on each
    of the measures in scanpath.continuous_measures.
    """

    def __init__(self, max_noise_samples=2):
        self.max_noise_samples = max_noise_samples

    def process(self, scanpath):
        """
        Runs a denoising on the scanpath. Returns a copy of scanpath --
        does not modify it.
        """
        sp = deepcopy(scanpath)
        # We'll work on one at a time
        for i in range(len(sp.continuous_measures)):
            meas = sp.continuous_measures[i]
            arr = sp.as_array((meas,)).T.flatten()
            # This array is 1 everywhere s_arr is zero
            missing_mask = arr == 0
            # Pad both ends with zeroes and take the derivative -- it'll be 1
            # at the start of missing data and -1 at the end
            padded = np.hstack((0, missing_mask, 0))
            edges = np.diff(padded)
            starts = np.where(edges > 0)[0]
            ends = np.where(edges < 0)[0]
            lengths = ends - starts
            # And now, the things to correct are no longer than max_noise
            idxs_to_correct = np.where(lengths <= self.max_noise_samples)[0]
            for c_idx in idxs_to_correct:
                # Find the interp values...
                known_x = [starts[c_idx]-1, ends[c_idx]+1]
                interp_x = range(starts[c_idx], ends[c_idx])
                interp_y = np.interp(interp_x, known_x, arr[known_x])
                # And save the data in the copied scanpath
                for i in range(len(interp_x)):
                    setattr(sp[interp_x[i]], meas, interp_y[i])
            
        return sp
        
