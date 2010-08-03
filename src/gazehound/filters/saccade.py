# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

import numpy as np
from scipy import ndimage
from scipy import stats

class AdaptiveDetector(object):
    """ 
    A saccade detector employing an adaptive velocity threshold.
    
    References:
    
    [1] M. Nyström, K. Holmqvist, An adaptive algorithm for fixation, 
    saccade, and glissade detection in eyetracking data. Behavior Research 
    Methods, 2010. doi:10.3758/BRM.42.1.188
    """

    def __init__(self, pointpath, use_attrs):
        self.pointpath = pointpath
        self.use_attrs = use_attrs
        
        self.p_arr = np.array(
            [[getattr(p, at) for at in use_attrs] for p in pointpath],
            dtype=np.float32)
    


    def find_threshold(self, velocities, start_percentile=99.5, 
        stop_change_percent=0.01, max_iters=1000):
        # Find a starting value
        considered = np.abs(velocities)
        thresh = stats.scoreatpercentile(velocities, start_percentile)
        current_change_pct = 1
        i = 0
        while current_change_pct > stop_change_percent and i < max_iters:
            i += 1
            considered = considered[considered < thresh]
            new_thresh = np.mean(considered) + 6*np.std(considered)
            current_change_pct = abs((new_thresh-thresh)/thresh)
            thresh = new_thresh
            
        if i == max_iters: thresh = None
        
        return thresh


    def clamp_to_percentile(self, arr, percentiles):
        from scipy.stats import scoreatpercentile as sap
        return arr.clip(sap(arr, percentiles[0]), sap(arr, percentiles[1]))
        
    def saccades(self,
        start_thresh_pct = 99.5, min_fix_dur = 5, filter_width=7):
        from scipy.ndimage import maximum_filter1d as max_flt
                        
        p_diffs = np.apply_along_axis(
            sgolay, 0, self.p_arr, filter_width, 2, 1)
            
        clamped = self.clamp_to_percentile(
            p_diffs, (1-start_thresh_pct, start_thresh_pct))

        def normalize(arr):
            return arr / np.max(np.abs(arr))
        normed = np.apply_along_axis(normalize, 0, clamped)
        pos_speeds = np.abs(normed)
        averages = np.apply_along_axis(np.mean, 1, pos_speeds)
        # Find the peaks
        max_filtered = max_flt(averages, min_fix_dur)
        peak_mask = (max_filtered == averages)
        peaks = averages*peak_mask
        threshold = self.find_threshold(averages)
        candidates = peaks >= threshold
        return {
            'raw' : self.p_arr,
            'diffs' : p_diffs,
            'clamped' : clamped,
            'normed' : normed,
            'pos_speeds' : pos_speeds,
            'averages' : averages,
            'max_filtered' : max_filtered,
            'peak_mask': peak_mask,
            'peaks' : peaks,
            'threshold' : threshold,
            'candidates' : candidates
        }


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

