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
        # Basic algo is much like denoising:
        # 1: Find areas in which our measure is zero
        # 2: Take the derivative to find edges of those areas
        # 3: Starts and ends of the blink candidates are the indexes of
        #    the path in which dy > 0 and dy < 0, respectively.
        candidates = []
        measures = ('x', 'y')
        arr = scanpath.as_array(measures).T # Transposing makes it all easier
        self.__arr = arr
        zeroed_data = arr == 0
        candidate_times = np.hstack((0, zeroed_data[0]*zeroed_data[1], 0))
        
        # All this is just used to make expanding blinks easier later
        # Stack with inf to keep the start dy arbitrarily high
        nonzero_ys = arr[1] <> 0
        self.__dy = np.hstack((np.inf,np.diff(arr[1])))
        dy_a = np.abs(self.__dy)
        below_start_thresh = dy_a <= self.start_dy_threshold
        below_start_thresh *= nonzero_ys
        self.__below_start_dy_thresh_idx = np.where(below_start_thresh)[0]
        below_end_thresh = dy_a <= self.end_dy_threshold
        below_end_thresh *= nonzero_ys
        self.__below_end_dy_thresh_idx = np.where(below_end_thresh)[0]

        edges = np.diff(candidate_times)
        starts = np.where(edges > 0)[0]
        ends = np.where(edges < 0)[0]
        for i in range(len(starts)):
            si = starts[i]
            ei = ends[i]-1
            b = Blink(start=scanpath[si].time, end=scanpath[ei].time)
            b.start_index = si
            b.end_index = ei
            candidates.append(b)
        
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
        return Timeline(events = [b for b in expanded if b is not None])

    def expand_blink_bidir(self, blink, scanpath):
        try:
            b = deepcopy(blink)
            # A little tricky double-dereferencing here: we're looking for the
            # index of the point
            idx_before_blink = np.where(self.__below_start_dy_thresh_idx < b.start_index)[0]
            pre_idx_idx = np.where(
                self.__below_start_dy_thresh_idx < b.start_index)[0][-1]
            # Add one -- this will the first point of "bad" data
            b.start_index = self.__below_start_dy_thresh_idx[pre_idx_idx]+1
            post_idx_idx = np.where(
                self.__below_end_dy_thresh_idx > b.end_index)[0][0]
            # Subtract two -- this will be the last point of bad data
            b.end_index = self.__below_end_dy_thresh_idx[post_idx_idx]-2
            b.start = scanpath[b.start_index].time
            b.end = scanpath[b.end_index].time
            return b
        except IndexError:
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
                known_x = [starts[c_idx]-1, ends[c_idx]]
                interp_x = range(starts[c_idx], ends[c_idx])
                interp_y = np.interp(interp_x, known_x, arr[known_x])
                # And save the data in the copied scanpath
                for i in range(len(interp_x)):
                    setattr(sp[interp_x[i]], meas, interp_y[i])
            
        return sp
        
