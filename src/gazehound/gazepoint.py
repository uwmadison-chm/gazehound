# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

import copy
import numpy as np


class Point(object):
    """
    A point with x, y, and time coordinates -- one point in a scan path
    """

    interp_attrs = ('x', 'y')

    def __init__(self, x=None, y=None, time=None, duration=1.0):
        self.x = x
        self.y = y
        self.time = time
        self.duration = duration

    def valid(criteria):
        """ Evaluate criteria() for this point. critiera() should return
            True or False.
        """
        return critera(self)

    def standard_valid(self):
        return (self.x > 0 and self.y > 0)

    def within(self, bounds):
        x1, y1, x2, y2 = bounds
        return (
            (self.x >= x1 and self.x <= x2) and
            (self.y >= y1 and self.y <= y2))

    def time_midpoint(self):
        return (self.time + (self.duration / 2))

    @property
    def computed_end(self):
        return (self.time + self.duration)

    @property
    def interp_dict(self):
        vals = {}
        for attr in type(self).interp_attrs:
            vals[attr] = getattr(self, attr)
        return vals

    def merge_dict(self, attr_dict):
        for attr, val in attr_dict.items():
            setattr(self, attr, val)

    def interpolate_from(self, f):
        self.merge_dict(f.interp_dict)

    def __repr__(self):
        return (
        "<gazehound.gazepoint.Point(x: %s, y: %s, time: %s, duration: %s)" %
        (self.x, self.y, self.time, self.duration))


class IViewPoint(Point):
    """ A point from the iView system. """

    # All of the continuous measures that can be interpolated
    interp_attrs = (
        'x', 'y', 'pupil_h', 'pupil_v', 'corneal_reflex_h', 'corneal_reflex_v',
        'diam_h', 'diam_v')

    def __init__(self, x=None, y=None, time=None, duration=(1 / 60.0),
        set="", pupil_h=0, pupil_v=0, corneal_reflex_h=0, corneal_reflex_v=0,
        diam_h=0, diam_v=0):
        super(IViewPoint, self).__init__(x, y, time, duration)
        self.pupil_h = pupil_h
        self.pupil_v = pupil_v
        self.corneal_reflex_h = corneal_reflex_h
        self.corneal_reflex_v = corneal_reflex_v
        self.diam_h = diam_h
        self.diam_v = diam_v


class Scanpath(object):
    """ A set of Points arranged sequentially in time """
    uniformely_sampled = False # Subclass to make this true.

    def __init__(self, points=[], headers = {}):
        self.continuous_measures = ('x', 'y')
        self.time_measures = ('time', 'duration')
        self.measures = self.continuous_measures + self.time_measures
        
        self.points = points
        self.headers = headers

    def __len__(self):
        return self.points.__len__()

    def __iter__(self):
        return self.points.__iter__()

    def __getitem__(self, i):
        return self.points[i]

    def __getslice__(self, i, j):
        return Scanpath(self.points[i:j])

    def extend(self, sp):
        self.points.extend(sp.points)

    def valid_points(self, criterion):
        return Scanpath(
            [point for point in self.points if criterion(point)])

    def mean(self):
        val = np.apply_along_axis(np.mean, 0, self.as_array(('x', 'y')))
        if np.any(np.isnan(val)):
            val = None
        return val
        
    def median(self):
        val = np.apply_along_axis(np.median, 0, self.as_array(('x', 'y')))
        if np.any(np.isnan(val)):
            val = None
        return val

    @property
    def total_duration(self):
        return sum((p.duration for p in self.points))

    def recenter_by(self, x, y):
        points = copy.deepcopy(self.points)
        for point in points:
            point.x += x
            point.y += y
        return Scanpath(points=points)

    def constrain_to(self,
        min_x_const = (0,0),
        min_y_const = (0,0),
        max_x_const = (1000,1000),
        max_y_const = (1000,1000)):
        plist = copy.deepcopy(self)
        for p in plist:
            if p.x < min_x_const[0]: p.x = min_x_const[1]
            if p.x > max_x_const[0]: p.x = max_x_const[1]
            if p.y < min_y_const[0]: p.y = min_y_const[1]
            if p.y > max_y_const[0]: p.y = max_y_const[1]
        return plist

    def points_within(self, shape):
        plist = copy.deepcopy(self.points)
        return Scanpath(points=[p for p in plist if (p.x, p.y) in shape])

    def as_array(self,
            measures=None,
            dtype=np.float32):
        """ Turns our list of points into a numpy ndarray. """
        # Map the desired properties into a list
        # for every point in our path.
        if measures is None: measures = self.measures
        return np.array([
            [getattr(point, m) for m in measures]
                for point in self.points], dtype=dtype)


    def time_index(self, time):
        t1 = self.points[0].time
        for i in xrange(len(self.points)):
            t2 = self.points[i].time
            if (t1 <= time and t2 > time):
                return i - 1
            t1 = t2
        return len(self.points)  # It's the last point!


class UniformelySampledScanpath(Scanpath):
    uniformely_sampled = True

    def __init__(self, samples_per_second, points, measures, headers={}):
        super(UniformelySampledScanpath, self).__init__(headers=headers)
        self.samples_per_second = samples_per_second
        self.points = points
        self.measures = measures
        self.headers = headers
        self.time_measures = ('time', 'duration')
    
    def as_array(self, measures=None):
        if measures is None:
            measures = self.measures
        return self.points[:,self.measure_indexes(measures)]
    
    def measure_index(self, name):
        return self.measures.index(name)
    
    def measure_indexes(self, names):
        return [self.measures.index(n) for n in names]

    @property
    def interpolable_measures(self):
        return [m for m in self.measures if m not in self.time_measures]
    
    def __len__(self):
        return self.points.__len__()

    def __iter__(self):
        return self.points.__iter__()

    def __getitem__(self, i):
        return self.points[i]

    def __getslice__(self, i, j):
        sc = copy.copy(self)
        sc.points = self.points[i:j]
        return sc
    
    def copy_measures(self, from_pt, to_pt):
        indexes_to_copy = self.measure_indexes(self.interpolable_measures)
        for i in indexes_to_copy:
            to_pt[i] = from_pt[i]

    def recenter_by(self, x, y):
        out = copy.deepcopy(self)
        indexes = self.measure_indexes(('x', 'y'))
        out.points[:,[indexes]] += [x,y]
        return out

    def constrain_to(self,
        min_x_const = (0,0),
        min_y_const = (0,0),
        max_x_const = (1000,1000),
        max_y_const = (1000,1000)):
        
        out = copy.deepcopy(self)
        x_i = self.measure_index('x')
        y_i = self.measure_index('y')
        ar = out.points
        ar[:,x_i][ar:,x_i < min_x_const[0]] = min_x_const[1]
        ar[:,x_i][ar:,x_i > max_x_const[0]] = max_x_const[1]
        ar[:,y_i][ar:,y_i < min_y_const[0]] = min_y_const[1]
        ar[:,y_i][ar:,y_i > max_y_const[0]] = max_y_const[1]
        return out


    def points_matching(self, fx, measures=('x', 'y')):
        sc = copy.copy(self)
        p_arr = self.as_array(measures)
        matches = self.points[np.apply_along_axis(fx, 1, p_arr)]
        sc.points = matches
        return sc

    def points_within(self, shape):
        sc = copy.copy(self)
        def in_fx(p):
            return p in shape
        if shape is not None:
            sc = self.points_matching(in_fx, ('x', 'y'))
        return sc

class IViewScanpath(UniformelySampledScanpath):

    def __init__(self, samples_per_second, points, measures, headers={}):
        super(IViewScanpath, self).__init__(samples_per_second, points, 
            measures, headers)

        self.time_measures = ('time', 'duration',)


class IView3Scanpath(IViewScanpath):

    def __init__(self, samples_per_second, points, measures, 
                headers={}):
        super(IView3Scanpath, self).__init__(samples_per_second, points, measures)
        self.headers = headers
        self.time_measures = ('time', 'timestamp', 'duration')

    def correct_times(self):
        # Frustratingly, times are in microseconds since epoch in v3
        timestamp_i = self.measures.index('timestamp')
        time_i = self.measures.index('time')
        self.points[:][time_i] = (
            self.points[:][timestamp_i] - self.points[:][timestamp_i][0])/1000
    

class PointFactory(object):
    """ Maps a list of gaze point data to a list of Points """

    def __init__(self, type_to_produce=Point):
        self.type_to_produce = type_to_produce

    def from_component_list(self, components, attribute_list):
        """
        Produces and returns a list of points from a list of component parts
        and an attribute mapping.

        Arguments:
        components: A list of lists -- each item of the outer list
            containing one gaze point's data

        attribute_list: A list of tuples containing (attribute_name, type)

        This method will happily raise an IndexException if you have
        more elements in attribute_list than in any of the elements in
        component_list.
        """

        points = []
        for point_data in components:
            point = self.type_to_produce()

            try:
                for i in range(len(attribute_list)):
                    attr_name = attribute_list[i][0]
                    attr_type = attribute_list[i][1]
                    if attr_type is not None:
                        try:
                            setattr(point, attr_name, attr_type(point_data[i]))
                        except AttributeError:
                            err_str = "Could not set %s" % attribute_list
                            raise AttributeError(err_str)
            except ValueError:
                err_str = ("Could not parse %s with %s" %
                    (point_data, attribute_list))
                raise ValueError(err_str)

            points.append(point)
        return points


class IView2PointFactory(PointFactory):
    """
    Maps a list of gaze point data to a list of Points, using SMI's iView
    data scheme.
    """

    def __init__(self, type_to_produce=IViewPoint):
        super(IView2PointFactory, self).__init__(type_to_produce)
        self.data_map = [
            ('time', int),
            ('set', str),
            ('pupil_h', int),
            ('pupil_v', int),
            ('corneal_reflex_h', int),
            ('corneal_reflex_v', int),
            ('x', int),
            ('y', int),
            ('diam_h', int),
            ('diam_v', int)]

    def from_component_list(self, components):
        indexes_to_extract = [
            i for i in range(len(self.data_map)) if self.data_map[i][1] == int]
        return np.array([
                [line[i] for i in indexes_to_extract]
            for line in components], dtype=float
        )
    
    @property
    def numeric_measures(self):
        return [m[0] for m in self.data_map if m[1] == int]
    

class IView3PointFactory(PointFactory):
    """
    I know this is not general enough, but it'll do for us, for now.

    Time        Type    Trial   R Raw X [px]    R Raw Y [px]    R Dia X [px]
    R Dia Y [px]        R CR1 X [px]    R CR1 Y [px]    R CR2 X [px]
    R CR2 Y [px]        R POR X [px]    R POR Y [px]    Frame

    """

    def __init__(self, measure_map, type_to_produce=IViewPoint):
        super(IView3PointFactory, self).__init__(type_to_produce)
        self.measure_map = measure_map

    def from_component_list(self, components):
        indexes = [p[0] for p in self.measure_map.values()]
        return np.array(
            [
                [float(line[i]) for i in  indexes]
            for line in components], dtype=float
        )
    
    @property
    def numeric_measures(self):
        return [measure_name for measure_name, mapper 
            in self.measure_map.iteritems() if mapper[1] in [int, float]]


class IViewFixationFactory(PointFactory):
    """
    Maps a list of fixations into a list of Points.
    """

    def __init__(self, type_to_produce=Point):
        super(IViewFixationFactory, self).__init__(type_to_produce)
        self.data_map = [
            ('start_num', int),
            ('end_num', int),
            ('time', int),
            ('end_time', int),
            ('x', int),
            ('y', int),
            ('object', str),
            ('duration', int)]

    def from_component_list(self, components):
        return super(IViewFixationFactory, self).from_component_list(
            components, self.data_map)
