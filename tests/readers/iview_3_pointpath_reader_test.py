# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

from __future__ import with_statement
from os import path
from gazehound.readers.iview import IView3PointPathReader

from ..testutils import *
from nose.tools import *


class TestIView3PointPathReader(object):
    """ Test out the reader for Version 3 of the iview files """
    def __init__(self):
        self.EXPECTED_POINTS=15
        self.EXPECTED_COMMENTS=20
    
    def setup(self):
        p = path.abspath(path.dirname(__file__))
        self.point_file = path.join(p, "../examples/iview_3_small.txt")
        with open(self.point_file, 'rU') as f:
            self.point_lines = f.readlines()
    
    def test_comment_lines(self):
        ir = IView3PointPathReader(self.point_lines)
        eq_("##", ir.comment_char)
        eq_(self.EXPECTED_COMMENTS, len(ir.comment_lines))
    
    def test_content_len(self):
        ir = IView3PointPathReader(self.point_lines)
        eq_(self.EXPECTED_POINTS, len(ir.content_lines))
    
    def test_header_map(self):
        ir = IView3PointPathReader(self.point_lines)
        h = ir.header()
        includes_(h, 'file_version')
        eq_(h['file_version'], 'IDF Converter 3.0.9')
        
    def test_pointpath_len(self):
        ir = IView3PointPathReader(self.point_lines)
        pp = ir.pointpath()
        eq_(60, pp.samples_per_second)
        eq_(self.EXPECTED_POINTS, len(pp))
        
    def test_column_headers(self):
        ir = IView3PointPathReader(self.point_lines)
        assert ir.column_headers is not None
        includes_(ir.column_headers, 'Time')
    
    def test_measure_mapping(self):
        ir = IView3PointPathReader(self.point_lines)
        mapping = ir.measure_mapping['timestamp']
        eq_(0, mapping[0])
        eq_(int, mapping[1])
    
    def test_column_mapping_with_two_cols(self):
        ir = IView3PointPathReader(self.point_lines)
        mapping = ir.measure_mapping['x']
        eq_(11, mapping[0])
        eq_(float, mapping[1])
    
    def test_pointpath_mapping(self):
        ir = IView3PointPathReader(self.point_lines)
        pp = ir.pointpath()
        eq_(1776229331031, pp[0].timestamp)