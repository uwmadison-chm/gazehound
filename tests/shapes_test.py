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