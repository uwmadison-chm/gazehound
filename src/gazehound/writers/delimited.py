# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

from __future__ import with_statement
import sys
import csv

class DelimitedWriter(object):
    """Writes iterable things into text files"""
    def __init__(self, mapping, out = sys.stdout, delimiter = "\t"):
        """ Creates a new delimited writer."""
        super(DelimitedWriter, self).__init__()
        self.mapping = mapping
        self.out = out
        self.writer = csv.writer(out, delimiter=delimiter)
        self.delimiter = delimiter
        
    def write_header(self):
        headers = [ elem[0] for elem in self.mapping ]
        self.writer.writerow(headers)
    
    def write(self, data):
        for row in data:
            row_mapped = [ elem[1](row) for elem in self.mapping ]
            self.writer.writerow(row_mapped)
    