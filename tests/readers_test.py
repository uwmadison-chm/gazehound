# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

# Hooray for with / as blocks! I miss ruby though :(
from __future__ import with_statement
from os import path
from gazehound.readers.delimited import DelimitedReader
from gazehound.readers.iview import IViewScanpathReader, IViewFixationReader
from gazehound.readers.timeline import TimelineReader
from testutils import *
from nose.tools import *

class TestDelimitedReader(object):
    """Exercises the DelmitedReader class"""

    def setup(self):
        p = path.abspath(path.dirname(__file__))
        # All of these should generate the same number of lines...
        self.norm_file = path.join(
            p, "examples/iview_normal.txt")
        self.blank_comment_file = path.join(
            p, "examples/iview_blank_comment.txt")
        self.comment_inbody = path.join(
            p, "examples/iview_comment_inbody.txt")
        
        with open(self.norm_file) as f:
            self.norm_lines = f.readlines()
        
        with open(self.blank_comment_file) as f:
            self.blank_comment_lines = f.readlines()
        
        with open(self.comment_inbody) as f:
            self.comment_inbody = f.readlines()
        
        self.EXPECTED_LINES = 13
        self.COMMENT_LINES = 11
        
    def teardown(self):
        pass
        
    def test_reader_skips_normal_comments(self):
        dr = DelimitedReader(self.norm_lines, 
            skip_comments = True, comment_char = "#")
        
        assert len(dr) == self.EXPECTED_LINES
    
    def test_reader_can_read_file(self):
        dr = DelimitedReader(None, 
            skip_comments = True, comment_char = "#")
        dr.read_file(self.norm_file)
        
        eq_(len(dr), self.EXPECTED_LINES)
    
    def test_reader_can_take_filename_arg(self):
        dr = DelimitedReader(filename = self.norm_file)
        
        eq_(len(dr), self.EXPECTED_LINES)
    
    def test_reader_skips_comments_with_blanks(self):
        dr = DelimitedReader(self.blank_comment_lines,
            skip_comments = True, comment_char = "#")
            
        eq_(len(dr), self.EXPECTED_LINES)
        
    def test_reader_contains_lines_with_same_elements(self):
        dr = DelimitedReader(self.norm_lines)
        
        first_element = dr.next()
        for l in dr:
            gt_(len(l), 1)
            eq_(len(l), len(first_element))
    
    def test_reader_yields_comment_lines(self):
        dr = DelimitedReader(self.norm_lines,
            skip_comments = True, comment_char = "#")

        eq_(len(dr.comment_lines), self.COMMENT_LINES)
    
    def test_reader_will_skip_lines(self):
        dr = DelimitedReader(self.norm_lines,
            skip_comments = True, comment_char = "#", skip_lines=1)
        eq_(len(dr.comment_lines), (self.COMMENT_LINES-1))
        
        
class TestIViewScanpathReader(object):
    """Exercise the IVIewScanpathReader class"""
    def setup(self):
        p = path.abspath(path.dirname(__file__))
        self.norm_file = path.join(p, "examples/iview_normal.txt")
        with open(self.norm_file) as f:
            self.norm_lines = f.readlines()

        self.EXPECTED_LINES = 13
        self.COMMENT_LINES = 11
    
    def test_header_map_lives_on(self):
        ir = IViewScanpathReader(self.norm_lines)
        includes_(ir.header_map, "FileVersion")
    
    def test_reader_basically_works(self):
        ir = IViewScanpathReader(self.norm_lines)
        
        eq_(len(ir), self.EXPECTED_LINES)
        
    def test_reader_uses_read_file(self):
        ir = IViewScanpathReader(filename = self.norm_file)
        
        eq_(len(ir), self.EXPECTED_LINES)
        
    def test_reader_finds_comment_lines(self):
        ir = IViewScanpathReader(self.norm_lines)
        comment_lines = ir.comment_lines
        
        eq_(ir.comment_char, "#")
        eq_(len(comment_lines), self.COMMENT_LINES)
    
    def test_basic_header_parsing(self):
        ir = IViewScanpathReader(self.norm_lines)
        h = ir.header()
        assert h is not None
        includes_(h, 'file_version')
        eq_(h.get('file_version'), '2')
        
    def test_calibration_size_parses_into_int_list(self):
        ir = IViewScanpathReader(self.norm_lines)
        h = ir.header()
        
        eq_(h.get('calibration_size'), [800,600])
    
    def test_pointpath_returns_expected_points(self):
        ir = IViewScanpathReader(self.norm_lines)
        
        pointpath = ir.pointpath()
        eq_(len(pointpath), self.EXPECTED_LINES)
    

class TestIViewFixationReader(object):
    """Exercise the IViewFixationReader"""
    def __init__(self):
        p = path.abspath(path.dirname(__file__))
        self.fix_file = path.join(p, "examples/fixations.txt")
        with open(self.fix_file) as f:
            self.fixation_lines = f.readlines()

        self.EXPECTED_FIXATIONS = 8
        
    def test_reader_basically_works(self):
        fr = IViewFixationReader(filename=self.fix_file)
        
        eq_(len(fr), self.EXPECTED_FIXATIONS)
        
    def test_reader_with_filename(self):
        fr = IViewFixationReader(self.fixation_lines)
        
        eq_(len(fr), self.EXPECTED_FIXATIONS)
        
        
    def test_basic_header_parsing(self):
        fr = IViewFixationReader(self.fixation_lines)
        
        h = fr.header()
        eq_(h.get('subject'), '001')
        
    def test_calibration_size_parses_into_int_list(self):
        ir = IViewFixationReader(self.fixation_lines)
        h = ir.header()

        eq_(h.get('calibration_size'), [800,600])

class TestTimelineReader(object):
    """ Exercise the TimelineReader """
    
    def __init__(self):
        p = path.abspath(path.dirname(__file__))
        self.pres_file = path.join(p, "examples/pres_tiny.txt")
    
        with open(self.pres_file) as f:
            self.pres_lines = f.readlines()
        
        self.CONTENT_LINES = len(self.pres_lines) - 1
    
    def test_reader_reads(self):
        tr = TimelineReader(self.pres_lines)
        eq_(len(tr), self.CONTENT_LINES)
    
    def test_reader_read_convenience(self):
        tr = TimelineReader(filename = self.pres_file)
        eq_(len(tr), self.CONTENT_LINES)
        