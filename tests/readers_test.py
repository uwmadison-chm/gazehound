# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

# Hooray for with / as blocks! I miss ruby though :(
from __future__ import with_statement
from os import path
from gazehound.readers import DelimitedReader, IViewReader


class TestDelimitedReader(object):
    """Exercises the DelmitedReader class"""

    def setup(self):
        p = path.abspath(path.dirname(__file__))
        # All of these should generate the same number of lines...
        with open(path.join(p, "examples/iview_normal.txt")) as f:
            self.norm_lines = f.readlines()
        
        with open(path.join(p, "examples/iview_blank_comment.txt")) as f:
            self.blank_comment_lines = f.readlines()
        
        with open(path.join(p, "examples/iview_comment_inbody.txt")) as f:
            self.comment_inbody = f.readlines()
        
        self.EXPECTED_LINES = 13
        self.COMMENT_LINES = 11
        
    def teardown(self):
        pass
        
    def test_reader_skips_normal_comments(self):
        dr = DelimitedReader(self.norm_lines, 
            skip_comments = True, comment_char = "#")
        
        assert len(dr) == self.EXPECTED_LINES
    
    def test_reader_skips_comments_with_blanks(self):
        dr = DelimitedReader(self.blank_comment_lines,
            skip_comments = True, comment_char = "#")
            
        assert len(dr) == self.EXPECTED_LINES
        
    def test_reader_keeps_comment_lines_in_body(self):
        dr = DelimitedReader(self.comment_inbody,
            skip_comments = True, comment_char = "#")

        assert len(dr) == self.EXPECTED_LINES

    def test_reader_contains_lines_with_same_elements(self):
        dr = DelimitedReader(self.norm_lines)
        
        first_element = dr.next()
        for l in dr:
            assert len(l) > 1
            assert len(l) == len(first_element)
    
    def test_reader_yields_comment_lines(self):
        dr = DelimitedReader(self.norm_lines,
            skip_comments = True, comment_char = "#")
            
        assert len(dr.comment_lines()) == self.COMMENT_LINES
        
class TestIViewReader(object):
    """Exercise the IViewReader class"""
    def setup(self):
        p = path.abspath(path.dirname(__file__))
        with open(path.join(p, "examples/iview_normal.txt")) as f:
            self.norm_lines = f.readlines()

        self.EXPECTED_LINES = 13
    
    
    def test_reader_basically_works(self):
        ir = IViewReader(self.norm_lines)
        
        assert len(ir) == self.EXPECTED_LINES
        
    def test_basic_header_parsing(self):
        ir = IViewReader(self.norm_lines)
        h = ir.header()
        assert h.get('file_version') == '2'
        
    def test_calibration_size_parses_into_int_list(self):
        ir = IViewReader(self.norm_lines)
        h = ir.header()
        
        assert h.get('calibration_size') == [800,600]
    
    def test_scanpath_returns_expected_points(self):
        ir = IViewReader(self.norm_lines)
        
        scanpath = ir.scanpath()
        #assert len(scanpath) == self.EXPECTED_LINES