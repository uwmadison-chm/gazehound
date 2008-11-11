# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

import copy

class Point(object):
    """ 
    A point with x, y, and time coordinates -- one point in a scan path 
    """
    
    def __init__(self, x = None, y = None, time = None):
        self.x = x
        self.y = y
        self.time = time
        
    
    def valid(criteria):
        """ Evaluate criteria() for this point. critiera() should return
            True or False.
        """
        return critera(self)
        
    def within(self, bounds):
        x1, y1, x2, y2 = bounds
        return (
            (self.x >= x1 and self.x <= x2) and
            (self.y >= y1 and self.y <= y2)
        )

class ScanPath(object):
    """ A set of Points arranged sequentially in time """
    def __init__(self, points = []):
        self.points = points
        
    def __len__(self):
        return self.points.__len__()
        
    def __iter__(self):
        return self.points.__iter__()
    
    def __getitem__(self, i):
        return self.points[i]
        
    def __getslice__(self, i, j):
        return ScanPath(self.points[i:j])
        
    def extend(self, sp):
        self.points.extend(sp.points)
    
    def valid_points(self, criterion):
        return ScanPath(
            [point for point in self.points if criterion(point)]
        )
    
    def mean(self):
        if len(self.points) == 0:
            return None
        xtotal = float(sum((p.x for p in self.points), 0))
        ytotal = float(sum((p.y for p in self.points), 0))
        return (xtotal/len(self.points), ytotal/len(self.points))

    def recenter_by(self, x, y):
        points = copy.deepcopy(self.points)
        for point in points:
            point.x += x
            point.y += y
        return ScanPath(points = points)
    

class PointFactory(object):
    """ Maps a list of gaze point data to a list of Points """

    def __init__(self, type_to_produce = Point):
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
            
            for i in range(len(attribute_list)):
                attr_name = attribute_list[i][0]
                attr_type = attribute_list[i][1]
                if attr_type is not None:
                    setattr(point, attr_name, attr_type(point_data[i]))

            points.append(point)
        return points


class IViewPointFactory(PointFactory):
    """
    Maps a list of gaze point data to a list of Points, using SMI's iView
    data scheme.
    """

        
    def __init__(self, type_to_produce = Point):
        super(IViewPointFactory, self).__init__(type_to_produce)
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
            ('diam_v', int)
        ]
        
    def from_component_list(self, components):
        return super(IViewPointFactory, self).from_component_list(
            components, self.data_map
        )