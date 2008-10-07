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
        


class Rectangle(Shape):
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
        

class Ellipse(Shape):
    """An ellipse-shaped area of interest"""
    def __init__(self, cx = None, cy = None, semix = None, semiy = None):
        super(Ellipse, self).__init__()
        self.cx = cx
        self.cy = cy
        self.semix = semix
        self.semiy = semiy
        
    def __contains__(self, point):
        """ 
        Return true if and only if the (x,y) tuple in point would lie inside 
        this ellipse or on the border.
        """
        x,y = point
        # Definition of ellipse: 
        # 1 = ((x - cx)^2/semix^2) + ((y - cy)^2/semiy^2)
        # We want to return true of the answer is <= 1.
        return (
        ((x - self.cx)**2/float(self.semix**2) +
        (y - self.cy)**2/float(self.semiy**2))
        <= 1 ) 
        
    def __repr__(self):
        return "Ellipse"+str((self.cx, self.cy, self.semix, self.semiy))
        