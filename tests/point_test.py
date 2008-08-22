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
        
        
        # Fields are:
        # Time | Set | Pupil H | Pupil V | C.R. H | C.R. V | ScreenH | ScreenV | Diam H | Diam V 
        self.smi_gaze_ary = [
            ['0', '0', '5034', '3490', '4687', '3380', '358', '543', '2400', '2080'],
            ['16', '0', '5042', '3491', '4690', '3388', '353', '528', '2432', '2112'],
            ['33', '0', '5050', '3477', '4692', '3388', '357', '490', '2432', '2144'],
            ['50', '0', '5050', '3472', '4688', '3391', '365', '473', '2432', '2080'], 
            ['66', '0', '5017', '3595', '4691', '3367', '58', '986', '2368', '1824'],
            ['83', '0', '4929', '3946', '4686', '3357', '518', '-56', '2144', '1184']
        ]
        
        self.smi_mapping = [
            ('time', int),
            ('set', None),
            ('pupil_h', None),
            ('pupil_v', None),
            ('cr_h', None),
            ('cr_v', None),
            ('x', int),
            ('y', int),
            ('diam_h', None),
            ('diam_v', None)
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

    def test_factory_skips_none_attributes(self):
        points = self.generic_factory.from_component_list(
            self.smi_gaze_ary,
            self.smi_mapping
        )
        
        nones = [m for m in self.smi_mapping if m[1] is None]
        
        for point in points:
            for mapping in nones:
                assert not hasattr(point, mapping[0])