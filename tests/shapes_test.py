# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

from __future__ import with_statement
from os import path
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
        assert p not in s # Should raise NotImplentedError
                

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
        
class TestShapeReader(object):
    def __init__(self):
        super(TestShapeReader, self).__init__()
    
    def setup(self):
        p = path.abspath(path.dirname(__file__))
        self.path = p
        self.obt_file = path.join(p, 'examples/OBJECTS.OBT')
        self.reader = shapes.ShapeReader()
        # Object01=2, 0, 1, 21, 599  Ellipse topleft short x long y
        # Object02=1, 0, 0, 60, 24  Rect, topleft, long x short y
        self.shape_cfg = [
            ('Object01', '1, 0, 1, 60, 24  Rect, topleft, long x short y'),
            ('Object02', '2, 0, 1, 21, 599  Ellipse topleft short x long y')
        ]
    
    def test_reader_makes_shapes_from_shape_data(self):
        slist = self.reader.shapes_from_config_section(self.shape_cfg)
        eq_(len(slist), len(self.shape_cfg))
        assert all(isinstance(s, shapes.Shape) for s in slist)
        
    
    def test_reader_makes_shapes_from_obtfile(self):
        slist = self.reader.shapes_from_obt_file(self.obt_file)

        assert all(isinstance(s, shapes.Shape) for s in slist)
        # I know it contains a rect and an ellipse
        assert any(isinstance(s, shapes.Rectangle) for s in slist)
        assert any(isinstance(s, shapes.Ellipse) for s in slist)        
        
    def test_reader_sets_nanes(self):
        slist = self.reader.shapes_from_obt_file(self.obt_file)
        eq_(slist[0].name, 'object01')
    
    def test_reader_does_convienence_reading(self):
        self.reader.path = self.path+"/examples"
        slist = self.reader.find_file_and_create_shapes('objects')
        eq_(len(slist), len(self.shape_cfg))
        

class TestShapeFilename(object):
    def __init__(self):
        super(TestShapeFilename, self).__init__()
    
    def setup(self):
        p = path.abspath(path.dirname(__file__)+"/examples")
        self.a = shapes.ShapeFilename('a')
        self.objects = shapes.ShapeFilename('objects', path = p)
    
    def test_perms_contain_self(self):
        includes_(self.a.permutations(), 'a')
        
    def test_perms_tries_upcasing(self):
        includes_(self.a.permutations(), 'A')
    
    def test_perms_adds_obt(self):
        includes_(self.a.permutations(), 'a.obt')
    
    def test_perms_caps_with_obt(self):
        includes_(self.a.permutations(), 'A.OBT')
    
    def test_finds_first_valid(self):
        valid = self.objects.first_valid()
        should_valid = (self.objects.name+('.OBT')).upper()
        eq_(should_valid, valid.upper())
        
class TestTimelineDecorator(object):
    def __init__(self):
        super(TestTimelineDecorator, self).__init__()
        
    def setup(self):
        self.epath = path.abspath(path.dirname(__file__)+"/examples")
        self.reader = shapes.ShapeReader(path = self.epath)
        self.shape_hash = {
            'objects': mock_objects.shape_tuples()
        }
        self.timeline = mock_objects.simple_timeline()
        
    def test_decorator_adds_shapes_to_timeline(self):
        dec = shapes.TimelineDecorator()
        tls = dec.add_shapes_to_timeline(self.timeline, self.shape_hash)
        assert(tls[0].shapes is None)
        assert(tls[1].shapes is not None)
    
    def test_decorator_does_not_modify_original_timeline(self):
        dec = shapes.TimelineDecorator()
        tls = dec.add_shapes_to_timeline(self.timeline, self.shape_hash)
        assert(not hasattr(self.timeline[0], 'shapes'))
    
    def test_decorator_finds_shapes_in_path(self):
        dec = shapes.TimelineDecorator(self.reader)
        tls = dec.find_shape_files_and_add_to_timeline(self.timeline)
        #assert(tls[0].shapes is None)
    
    def test_find_shape_file_adds_none_for_failed_match(self):
        dec = shapes.TimelineDecorator(self.reader)
        p = dec.find_file_and_add_shapes_to_presentation(self.timeline[0])
        assert p.shapes is None
        
    def test_find_shape_file_adds_shape_for_good_match(self):
        dec = shapes.TimelineDecorator(self.reader)
        p = dec.find_file_and_add_shapes_to_presentation(self.timeline[1])
        assert p.shapes is not None