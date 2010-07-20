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
from gazehound.readers.auto_pointpath import AutoPointpathReader
from gazehound.readers.iview import IView2ScanpathReader, IView3PointPathReader

from ..testutils import *
from nose.tools import *

class TestAutoPointpath(object):
    
    def __init__(self):
        pass
        
    def setup(self):
        # Woo woo woo
        p = path.abspath(path.dirname(__file__))
        
        self.iview_2_file = path.join(
            p, "../examples/iview_normal.txt")
        self.iview_3_file = path.join(
            p, "../examples/iview_3_small.txt")
        self.event_file = path.join(
            p, "../examples/pres_tiny.txt")
            
        self.ar2 = AutoPointpathReader([IView2ScanpathReader])
        self.ar3 = AutoPointpathReader([IView3PointPathReader])
        self.ar_multi = AutoPointpathReader([
            IView2ScanpathReader, IView3PointPathReader
        ])
    
    def test_version_2_reader_gets_pointpath(self):
        app = self.ar2.read_pointpath(filename=self.iview_2_file)
        mpp = IView2ScanpathReader(filename=self.iview_2_file).pointpath()
        eq_(len(mpp), len(app))

    def test_version_2_reader_sets_success_class(self):
        app = self.ar2.read_pointpath(filename=self.iview_2_file)
        eq_(IView2ScanpathReader, self.ar2.success_class)
        
    def test_reader_returns_none_on_failure(self):
        app = self.ar2.read_pointpath(filename=self.iview_3_file)
        assert app is None
    
    def test_reader_records_failures(self):
        app = self.ar2.read_pointpath(filename=self.iview_3_file)
        eq_(1, len(self.ar2.failures))
        eq_(IView2ScanpathReader, self.ar2.failures[0][0])
    
    def test_multi_reader_succeeds(self):
        app = self.ar_multi.read_pointpath(self.iview_3_file)
        mpp = IView3PointPathReader(filename=self.iview_3_file)
        eq_(len(mpp), len(app))

    def test_multi_reader_records_failures(self):
        app = self.ar_multi.read_pointpath(self.iview_3_file)
        mpp = IView3PointPathReader(filename=self.iview_3_file)
        eq_(1, len(self.ar_multi.failures))
        eq_(IView2ScanpathReader, self.ar_multi.failures[0][0])
    
    def test_multi_reader_returns_none_on_fail(self):
        app = self.ar_multi.read_pointpath(self.event_file)
        eq_(2, len(self.ar_multi.failures))
        
    def test_multi_reader_has_no_success_class_on_fail(self):
        app = self.ar_multi.read_pointpath(self.event_file)
        assert self.ar_multi.success_class is None
