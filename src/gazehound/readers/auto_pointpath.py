# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.
#
# This module provides general convenience methods for reading pointpath
# after auto-determinig its type.

from __future__ import with_statement
from gazehound.readers.iview import IView2ScanpathReader, IView3PointPathReader

class AutoPointpathReader(object):
    
    def __init__(self, try_order=[
        IView2ScanpathReader,
        IView3PointPathReader
    ]):
        self.try_order = try_order
        self.failures = []
        self.success_class = None
    
    def read_pointpath(self, filename=None, file_data=None):
        for klass in self.try_order:
            reader = klass(filename=filename, file_data=file_data)
            try:
                pp = reader.pointpath()
                if pp is not None:
                    self.success_class = klass
                    return pp
            except Exception, exc:
                self.failures.append((klass, exc))
        
    
    