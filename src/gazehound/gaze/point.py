# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

class Point(object):
    """ 
    A point with x, y, and time coordinates -- one point in a scan path 
    """
    
    def __init__(self, x = None, y = None, time = None):
        self.x = x
        self.y = y
        self.time = time

class ScanPath(object):
    """ A set of Points arranged sequentially in time """
    def __init__(self, points = None):
        self.points = points
        
        

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
                setattr(point, attr_name, attr_type(point_data[i]))

            points.append(point)
        return points
            