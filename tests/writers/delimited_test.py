# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

import StringIO
from nose.tools import eq_
from gazehound.writers import delimited

class TestDelimitedWriter(object):
    def __init__(self):
        super(TestDelimitedWriter, self).__init__()
    
    def setup(self):
        self.data = [
            ['foo', 15, 35],
            ['corge', 13, 20]
        ]
        
        self.simple_mapper = [ 
            ('Name', lambda elem: elem[0]),
            ('Thing1', lambda elem: elem[1])
        ]

        self.out = StringIO.StringIO()
    
    def teardown(self):
        self.out.close()
    
    def test_writer_prints_headers(self):
        writer = delimited.DelimitedWriter(self.simple_mapper, out = self.out)
        writer.write_header()
        self.out.seek(0)
        eq_(self.out.readlines()[0].strip(), 'Name\tThing1')

    def test_writer_prints_data(self):
        writer = delimited.DelimitedWriter(self.simple_mapper, out = self.out)
        writer.write(self.data)
        self.out.seek(0)
        lines = [line.strip() for line in self.out.readlines()]
        eq_(len(lines), len(self.data))
        eq_(lines[0], 'foo\t15')
        