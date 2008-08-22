# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

import gazehound.gaze
from gazehound.gaze import point

class TestPointFactory(object):
    
    def setup(self):
        self.dense_gaze_ary = [
            ['0', '300', '400'],
            ['17', '310', '410'],
            ['33', '302', '411'],
            ['50', '299', '405']
        ]
        
        self.dense_mapping = [
            ('time', int),
            ('x', int),
            ('y', int)
        ]
        
        self.generic_factory = point.PointFactory()
        
    def test_factory_produces_proper_count_from_dense(self):
        points = self.generic_factory.from_component_list(
            self.dense_gaze_ary,
            self.dense_mapping
        )
        
        assert len(points) == len(self.dense_gaze_ary)
    
    def test_factory_produces_proper_type_from_dense(self):
        points = self.generic_factory.from_component_list(
            self.dense_gaze_ary,
            self.dense_mapping
        )
        
        for point in points:
            assert type(point) is self.generic_factory.type_to_produce
    
    def test_factory_produces_proper_data_mappings(self):
        points = self.generic_factory.from_component_list(
            self.dense_gaze_ary,
            self.dense_mapping
        )
        for point in points:
            for map in self.dense_mapping:
                attr_name = map[0]
                expected_type = map[1]
                attr = getattr(point, attr_name)
                assert type(attr) is expected_type
        