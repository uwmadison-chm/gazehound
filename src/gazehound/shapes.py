# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

import os.path
import copy
import array
from ConfigParser import SafeConfigParser


class Shape(object):
    """docstring for Shape"""

    def __init__(self, name='', description=''):
        super(Shape, self).__init__()
        self.name = name
        self.description = description

    def __contains__(self, point):
        raise NotImplementedError(
            "__contains__ must be overridden by subclass")


class Rectangle(Shape):

    def __init__(self, x1=None, y1=None, x2=None, y2=None,
    name='', description = ''):
        super(Rectangle, self).__init__(
            name = name, description = description)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def __contains__(self, point):
        """
        Return true if and only if the (x,y) tuple in point lies inside
        this rectangle or on its border.
        """
        x, y = point
        return (
            (x >= self.x1 and x <= self.x2) and
            (y >= self.y1 and y <= self.y2))

    def to_matrix(self, type_str='f', fill_value=1.0, bkg_value=0.0):
        """
        Return a list of array.array objects, sized with this rectangle's
        width and height, composed of elements of type_str and filled
        with fill_value.

        bkg_value is ignored here, but included for API compatibility with
        other Shape#to_matrix methods.
        """
        w = abs(self.x2 - self.x1)
        h = abs(self.y2 - self.y1)
        matrix = [
            array.array(type_str, [fill_value]*h)
            for c in range(0, w)]
        return matrix

    def __repr__(self):
        return "Rectangle"+str((self.x1, self.y1, self.x2, self.y2))


class Ellipse(Shape):
    """An ellipse-shaped area of interest"""

    def __init__(self, cx=None, cy=None, semix=None, semiy=None, name='',
            description=''):
        super(Ellipse, self).__init__(
            name=name, description=description)
        self.cx = cx
        self.cy = cy
        self.semix = semix
        self.semiy = semiy

    def __contains__(self, point):
        """
        Return true if and only if the (x,y) tuple in point lies inside
        this ellipse or on the border.
        """
        x, y = point
        # Definition of ellipse:
        # 1 = ((x - cx)^2/semix^2) + ((y - cy)^2/semiy^2)
        # We want to return true of the answer is <= 1.
        return (
        ((x - self.cx)**2/float(self.semix**2) +
        (y - self.cy)**2/float(self.semiy**2))
        <= 1)

    def height(self):
        return self.semiy*2

    def width(self):
        return self.semix*2

    def to_matrix(self, type_str='f', fill_value=1.0, bkg_value=0.0):
        h = self.height()
        w = self.width()
        matrix = [
            array.array(type_str, [bkg_value]*h)
            for c in range(0, w)]

        for i in range(0, w):
            for j in range(0, h):
                x = i+self.cx-self.semix
                y = j+self.cy-self.semiy
                point = (x, y)
                if point in self:
                    matrix[i][j] = fill_value
        return matrix

    def __repr__(self):
        return "Ellipse"+str((self.cx, self.cy, self.semix, self.semiy))


class ShapeParser(object):
    """Creates shapes out strings"""

    def __init__(self):
        super(ShapeParser, self).__init__()
        self.OBT_MAP = {
            '1': self.__parse_rectangle,
            '2': self.__parse_ellipse}

    def parse_obt_str(self, str, name=None):
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
            return subparser(params, name)
        except:
            return None

    def __parse_rectangle(self, str, name):
        """ str should not contain the leading 1"""
        x1, y1, x2, rest = str.split(", ", 3)
        y2, description = rest.split(" ", 1)
        x1, y1, x2, y2 = [int(e) for e in [x1, y1, x2, y2]]
        return Rectangle(x1, y1, x2, y2,
                            description = description, name = name)

    def __parse_ellipse(self, str, name):
        """ str should not contain the leading 2"""
        x, y, semi_x, rest = str.split(", ", 3)
        semi_y, description = rest.split(" ", 1)
        x, y, semi_x, semi_y = [int(e) for e in [x, y, semi_x, semi_y]]
        return Ellipse(x, y, semi_x, semi_y,
                            description = description, name = name)


class ShapeReader(object):
    """
    Reads shape (.OBT) files and turns them into a collection of
    Shape objects.
    """

    def __init__(self, path='.'):
        super(ShapeReader, self).__init__()
        self.path = path

    def shapes_from_config_section(self, shape_tuples):
        parser = ShapeParser()
        return [
            parser.parse_obt_str(st[1], name = st[0]) for st in shape_tuples]

    def shapes_from_obt_file(self, filename):
        cp = SafeConfigParser()
        cp.read(filename)
        tuples = [tup for tup in cp.items('Objects') if tup[1] != '0']
        tuples.sort()
        return self.shapes_from_config_section(tuples)

    def find_file_and_create_shapes(self, filename_part):
        sf = ShapeFilename(filename_part, self.path)
        fname = sf.first_valid()
        if fname is None:
            return None

        return self.shapes_from_obt_file(os.path.join(self.path, fname))


class ShapeFilename(object):
    """
    Represents the various permutations to try for a shape's filename, and
    computes the first valid possible match.
    """

    def __init__(self, name, path='.'):
        super(ShapeFilename, self).__init__()
        self.name = name
        self.path = path

    def permutations(self):
        perms = []
        for suffix in ['', '.obt', '.OBT']:
            for prefix in [self.name, self.name.upper()]:
                perms.append(prefix+suffix)

        return perms

    def first_valid(self):
        """
        Return the first thing from self.path/[self.permutations()] that's
        a readable file, or None if there isn't one.
        """
        for filename in self.permutations():
            tryfile = os.path.join(self.path, filename)
            if os.path.isfile(tryfile):
                return filename

        return None


class TimelineDecorator(object):
    """
    Adds shape data to a timeline.
    """

    def __init__(self, reader = ShapeReader()):
        super(TimelineDecorator, self).__init__()
        self.shape_reader = reader

    def add_shapes_to_timeline(self, timeline, shape_hash):
        my_tl = copy.deepcopy(timeline)
        for pres in my_tl:
            pres.shapes = shape_hash.get(pres.name)
        return my_tl

    def find_shape_files_and_add_to_timeline(self, timeline):
        my_tl = copy.deepcopy(timeline)
        for pres in my_tl:
            self.find_file_and_add_shapes_to_presentation(pres)
        my_tl.has_shapes = True
        return my_tl

    def find_file_and_add_shapes_to_presentation(self, presentation):
        presentation.shapes = self.shape_reader.find_file_and_create_shapes(
            presentation.name)
        return presentation
