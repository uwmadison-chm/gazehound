# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

from gazehound import gazepoint, shapes
import mock_objects
from nose.tools import eq_
from testutils import gt_, lt_, gte_, lte_, includes_

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
        
        self.generic_factory = gazepoint.PointFactory()
        
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
            assert isinstance(point, self.generic_factory.type_to_produce)
    
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
                assert isinstance(attr, expected_type)

    def test_factory_skips_none_attributes(self):
        points = self.generic_factory.from_component_list(
            self.smi_gaze_ary,
            self.smi_mapping
        )
        
        nones = [m for m in self.smi_mapping if m[1] is None]
        
        for point in points:
            for mapping in nones:
                assert not hasattr(point, mapping[0])
                
class TestIViewPointFactory(object):
    def setup(self):
        self.point_ary = mock_objects.smi_ary_spreadout()
        self.iview_fact = gazepoint.IViewPointFactory()
        
    def test_get_components_returns_proper_number_of_elements(self):
        points = self.iview_fact.from_component_list(self.point_ary)
        assert len(points) == len(self.point_ary)
        
    def test_get_components_returns_points(self):
        points = self.iview_fact.from_component_list(self.point_ary)
        assert all(isinstance(p, gazepoint.Point) for p in points)
        

class TestFixationFactory(object):
    def setup(self):
        self.fix_ary = mock_objects.smi_fixation_ary()
        self.fix_fact = gazepoint.IViewFixationFactory()
    
    def test_get_components_returns_proper_number_of_elements(self):
        fixations = self.fix_fact.from_component_list(self.fix_ary)
        eq_(len(fixations), len(self.fix_ary))
        
    def test_components_have_proper_properties(self):
        fixations = self.fix_fact.from_component_list(self.fix_ary)
        for fix in fixations:
            for mapping in self.fix_fact.data_map:
                eq_(type(getattr(fix, mapping[0])), mapping[1])
    # and a spot test...
    def test_one_value(self):
        fixations = self.fix_fact.from_component_list(self.fix_ary)
        # Check the mock_objects
        eq_(fixations[0].x, 365)

class TestScanPath(object):
    def setup(self):
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
        
        self.generic_factory = gazepoint.PointFactory()
        self.points = self.generic_factory.from_component_list(
            self.smi_gaze_ary,
            self.smi_mapping
        )
        
    
    def test_scanpath_iterates(self):
        scanpath = gazepoint.ScanPath(points = self.points)
        for p in scanpath:
            assert isinstance(p, self.generic_factory.type_to_produce)
    
    def test_scanpath_is_iterable(self):
        scanpath = gazepoint.ScanPath(points = self.points)
        eq_(scanpath[0].time, 0)
    
    def test_scanpath_is_slicable(self):
        scanpath = gazepoint.ScanPath(points = self.points)
        eq_(len(scanpath[0:2]), 2)
        eq_(type(scanpath[0:2]), type(scanpath))
    
    def test_scanpath_returns_all_with_free_criterion_in_valid(self):
        def criterion(point):
            return True
            
        scanpath = gazepoint.ScanPath(points = self.points)
        valid = scanpath.valid_points(criterion)
        eq_(len(valid), len(scanpath))
        
        
    def test_scanpath_returns_none_with_false_criterion_in_valid(self):
        def criterion(point):
            return False
            
        scanpath = gazepoint.ScanPath(points = self.points)
        valid = scanpath.valid_points(criterion)
        eq_(len(valid), 0)
        
    def test_scanpath_returns_valid_points_with_limiting_criterin(self):
        def criterion(point):
            return (point.x > 0 and point.x < 800)
    
    def test_scanpath_computes_mean(self):
         scanpath = gazepoint.ScanPath(points = self.points)
         x, y = scanpath.mean()
         eq_(int(x), 334)
         eq_(int(y), 494)
    
    def tets_mean_returns_none_for_zero_length(self):
        sp = gazepoint.ScanPath(points = [])
        p = scanpath.mean()
        assert p is None

    def test_recenter_duplicates_scanpath(self):
        scanpath = gazepoint.ScanPath(points = self.points)
        sp2 = scanpath.recenter_by(-10, -20)
        assert not scanpath[0] is sp2[0]
    
    def test_recenter_changes_x_and_y(self):
        scanpath = gazepoint.ScanPath(points = self.points)
        sp2 = scanpath.recenter_by(-10, -20)
        for i in range(0, len(scanpath)):
            op = scanpath[i]
            np = sp2[i]
            eq_(op.x-10, np.x)
            eq_(op.y-20, np.y)
    
    def test_points_in_filters(self):
        scanpath = gazepoint.ScanPath(points = self.points)
        rect = shapes.Rectangle(300,500,360,600)
        filtered = scanpath.points_within(rect)
        assert len(filtered) < len(scanpath)
        

class TestPoint(object):
    def __init__(self):
        super(TestPoint, self).__init__()
    
    def setup(self):
        self.hundreds = gazepoint.Point(100,100)
        
    def teardown(self):
        pass
        
    def test_within(self):
        in_bounds = (50,50,150,150)
        out_bounds = (0,0,50,50)
        
        assert self.hundreds.within(in_bounds)
        assert not self.hundreds.within(out_bounds)
    
    def test_time_midpoint(self):
        self.hundreds.time = 100
        self.hundreds.duration = 50
        eq_(self.hundreds.time_midpoint(), 125)