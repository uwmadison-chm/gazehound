# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

from gazehound.event import Blink

from copy import deepcopy

class Deblink(object):
    
    def __init__(self, min_duration = 200, max_duration = 1000):
        self.min_duratioin = min_duration
        self.max_duration = max_duration
    
    def blinks(self, pointpath):
        """
        Return a Timeline of Blinks.
        """
        
        
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
