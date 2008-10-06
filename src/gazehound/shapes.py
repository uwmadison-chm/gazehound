# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

class Shape(object):
    """docstring for Shape"""
    def __init__(self):
        super(Shape, self).__init__()
        
    def __contains__(self, point):
        raise NotImplementedError(
            "__contains__ must be overridden by subclass"
        )
        


class Rectangle(object):
    def __init__(self, x1 = None, y1 = None, x2 = None, y2 = None):
        super(Rectangle, self).__init__()
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        
    def __contains__(self, point):
        x,y = point
        return (
            (x >= self.x1 and x <= self.x2) and
            (y >= self.y1 and y <= self.y2)
        )