# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

class Shape(object):
    """docstring for Shape"""
    def __init__(self, name = '', description = ''):
        super(Shape, self).__init__()
        self.name = name
        self.description = description
        
    def __contains__(self, point):
        raise NotImplementedError(
            "__contains__ must be overridden by subclass"
        )
        

class Rectangle(Shape):
    def __init__(self, x1 = None, y1 = None, x2 = None, y2 = None, 
    name = '', description = ''):
        super(Rectangle, self).__init__(
            name = name, description = description
        )
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        
    def __contains__(self, point):
        """
        Return true if and only if the (x,y) tuple in point lies inside
        this rectangle or on its border.
        """
        x,y = point
        return (
            (x >= self.x1 and x <= self.x2) and
            (y >= self.y1 and y <= self.y2)
        )
        
    def __repr__(self):
        return "Rectangle"+str((self.x1, self.y1, self.x2, self.y2))

class Ellipse(Shape):
    """An ellipse-shaped area of interest"""
    def __init__(self, cx = None, cy = None, semix = None, semiy = None, 
    name='', description = ''):
        super(Ellipse, self).__init__(
            name = name, description = description
        )
        self.cx = cx
        self.cy = cy
        self.semix = semix
        self.semiy = semiy
        
    def __contains__(self, point):
        """ 
        Return true if and only if the (x,y) tuple in point lies inside 
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

class ShapeParser(object):
    """Creates shapes out strings"""
    def __init__(self):
        super(ShapeParser, self).__init__()
        self.OBT_MAP = {
            '1': self.__parse_rectangle
        }
        
        
    def parse_obt_str(self, str):
        """
        Parse an object string into an Ellipse or a Rectangle, or None if
        neither option is reasonaoble.
        
        Object strings are of the format created by SMI's iView analysis
        package, and look like:
        type, p1, p2, p3, p4 description
        
        Type is 1 or 2; 1 indicates rectangle, 2 indicates ellipse.
        
        For rectangles, the four parameters are the four lines defining the
        perimeter of the rectangle, in the order x1, y1, x2, y2.
        
        For ellipses, the four parameters are the center point and semimajor
        x and y axes of the ellipse, in the order x, y, semi_x, semi_y.
        """
        
        try:
            shape_type, params = str.split(", ", 1)
            subparser = self.OBT_MAP[shape_type]
            return subparser(params)
        except:
            return None
        
        
    def __parse_rectangle(self, str):
        """ str should not contain the leading 1"""
        x1, y1, x2, rest = str.split(", ", 3)
        y2, description = rest.split(" ", 1)
        x1, y1, x2, y2 = [ int(e) for e in [x1, y1, x2, y2]]
        return Rectangle(x1, y1, x2, y2, description = description)
    
    def __parse_trash(self, str):
        return None