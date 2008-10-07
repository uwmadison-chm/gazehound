# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

from __future__ import with_statement
from nose.tools import *
from testutils import includes_, not_includes_
from gazehound import shapes
import mock_objects

class TestShapes(object):
    def __init__(self):
        super(TestShapes, self).__init__()
        
    def setup(self):
        pass
        
    @raises(NotImplementedError)
    def test_shape_does_not_have_contains(self):
        s = shapes.Shape()
        p = (0,0)
        assert p not in s
                

class TestRectangle(object):
    def __init__(self):
        super(TestRectangle, self).__init__()
        
    def setup(self):
        self.origin_rect = shapes.Rectangle(0,0,99,99)
        
    def test_rectangle_knows_points_out(self):
        not_includes_(self.origin_rect, (100,100))
        
    def test_rectangle_knows_points_on_edge(self):
        includes_(self.origin_rect, (0,0))
        includes_(self.origin_rect, (0,99))
        includes_(self.origin_rect, (99,99))
        includes_(self.origin_rect, (99, 0))
    
    def test_rectangle_knows_points_in(self):
        includes_(self.origin_rect, (50,50))
        

class TestRectangle(object):
    def __init__(self):
        super(TestRectangle, self).__init__()
        
    def setup(self):
        self.ellipse = shapes.Ellipse(50,50,20,40)
        
    def test_ellipse_knows_points_out(self):
        not_includes_(self.ellipse, (0,0))
        
    def test_ellipse_knows_points_in(self):
        includes_(self.ellipse, (50,50))
        includes_(self.ellipse, (70,50))
        includes_(self.ellipse, (30,50))
        includes_(self.ellipse, (50,90))
        includes_(self.ellipse, (50,10))
        

class TestShapeParser(object):
    def __init__(self):
        super(TestShapeParser, self).__init__()
    
    def setup(self):
        self.rect_str = '1, 0, 1, 60, 24  Rect, topleft, long x short y'
        self.ell_str = '2, 0, 1, 21, 599  Ellipse topleft short x long y'
        self.parser = shapes.ShapeParser()
    
    def test_parser_makes_none_from_empty_str(self):
        s = self.parser.parse_obt_str("")
        assert s is None
    
    def tesT_parser_makes_none_from_invalid_str(self):
        s = self.parser.parse_obt_str("0, Foo")
        assert s is None
    
    def test_parser_makes_rectangles_from_obt(self):
        pass
        s = self.parser.parse_obt_str(self.rect_str)
        assert isinstance(s, shapes.Rectangle)
        eq_(s.x1, 0)
        eq_(s.y1, 1)
        eq_(s.x2, 60)
        eq_(s.y2, 24)
    
    def test_parser_makes_ellipses_from_obt(self):
        s = self.parser.parse_obt_str(self.ell_str)
        assert isinstance(s, shapes.Ellipse)
        eq_(s.cx, 0)
        eq_(s.cy, 1)
        eq_(s.semix, 21)
        eq_(s.semiy, 599)
        