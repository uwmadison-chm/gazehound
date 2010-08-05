# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

import numpy as np
from scipy.ndimage import maximum_filter1d as max_flt
from scipy.stats import scoreatpercentile

from gazehound.event import Saccade

class AdaptiveDetector(object):
    """ 
    A saccade detector employing an adaptive velocity threshold.
    
    References:
    
    [1] M. Nyström, K. Holmqvist, An adaptive algorithm for fixation, 
    saccade, and glissade detection in eyetracking data. Behavior Research 
    Methods, 2010. doi:10.3758/BRM.42.1.188
    """

    def __init__(self, scanpath, measures=('x', 'y'), 
            clip_speed_percent=99.5, minimum_fixation_ms=117,
            threshold_start_percent=99.5, threshold_sd_scale=6,
            threshold_min_change=0.001, threshold_max_iters=10000):
            
        self.scanpath = scanpath
        self.measures = measures
        self.minimum_fixation_ms = minimum_fixation_ms
        self.clip_speed_percent = clip_speed_percent
        self.threshold_start_percent = threshold_start_percent
        self.threshold_sd_scale = threshold_sd_scale
        self.threshold_min_change = threshold_min_change
        self.threshold_max_iters = threshold_max_iters

        self.__minimum_fixation_width = int(np.round(
            (self.scanpath.samples_per_second/1000.0) * minimum_fixation_ms
        ))
        self.__sg_filter_width = self.__minimum_fixation_width
        # This must be an odd number.
        if (self.__sg_filter_width % 2) == 0:
            self.__sg_filter_width += 1
        
        self._p_arr = scanpath.as_array(measures)
        
        self._compute_saccades()
    

    def _find_threshold(self, speeds, start_percentile, min_change_frac, 
            sd_threshold_scale, max_iters):
        # Find a starting value
        considered = speeds
        thresh = scoreatpercentile(considered, start_percentile)
        current_change_frac = 1
        self._thresh_iters = 0
        while (current_change_frac > min_change_frac and 
                self._thresh_iters < max_iters):
            self._thresh_iters += 1
            considered = considered[considered < thresh]
            new_thresh = (np.mean(considered) + 
                            sd_threshold_scale*np.std(considered))
            current_change_frac = abs((new_thresh-thresh)/thresh)
            thresh = new_thresh
            #print((self._thresh_iters, thresh, current_change_frac))
            
        if self._thresh_iters == max_iters: thresh = None
        
        return thresh


    def _clamp_to_percentile(self, arr, percentiles):
        return arr.clip(
            scoreatpercentile(arr, percentiles[0]), 
            scoreatpercentile(arr, percentiles[1]))
    
    def _compute_saccades(self):
        self._p_diffs = np.apply_along_axis(
            sgolay, 0, self._p_arr, self.__sg_filter_width, 2, 1)
        
        csp = self.clip_speed_percent
        clamped = self._clamp_to_percentile(
            self._p_diffs, (1-csp, csp))

        def normalize(arr):
            return arr / np.max(np.abs(arr))
        self._normed = np.apply_along_axis(normalize, 0, clamped)
        self._speeds = np.sqrt(np.apply_along_axis(np.sum, 1, self._normed**2))
        #pos_speeds = np.abs(normed)
        #averages = np.apply_along_axis(np.mean, 1, pos_speeds)
        # Find the peaks
        max_filtered = max_flt(self._speeds, self.__minimum_fixation_width)
        self._peak_mask = (max_filtered == self._speeds)
        self._peaks = self._speeds*self._peak_mask
        self._threshold = self._find_threshold(self._speeds, 
            self.threshold_start_percent, self.threshold_min_change,
            self.threshold_sd_scale, self.threshold_max_iters)
        self._candidates = self._peaks >= self._threshold


def sgolay(y, window_size, order, deriv=0):
    """
    Implementation of the Savitzky-Golay filter -- taken from:
    http://www.scipy.org/Cookbook/SavitzkyGolay
    
    Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techhniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """

    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError, msg:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv]
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m, y, mode='valid')

