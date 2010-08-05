# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

from gazehound import gazepoint, shapes
import numpy as np

import mock_objects
from nose.tools import *
from testutils import *


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
                
class TestIView2PointFactory(object):
    def setup(self):
        self.point_ary = mock_objects.iview_points_blinky()
        self.iview_fact = gazepoint.IView2PointFactory()
        
    def test_get_components_returns_proper_number_of_elements(self):
        points = self.iview_fact.from_component_list(self.point_ary)
        assert len(points) == len(self.point_ary)
        
    def test_get_components_returns_points(self):
        points = self.iview_fact.from_component_list(self.point_ary)
        assert isinstance(points, np.ndarray)


class TestFixationFactory(object):
    def setup(self):
        self.fix_ary = mock_objects.smi_fixation_ary()
        self.fix_fact = gazepoint.IViewFixationFactory()
    
    def test_get_components_returns_proper_number_of_elements(self):
        fixations = self.fix_fact.from_component_list(self.fix_ary)
        eq_(len(fixations), len(self.fix_ary))
    
    def test_converting_to_scanpath_does_not_change_length(self):
        fixations = self.fix_fact.from_component_list(self.fix_ary)
        scanpath = gazepoint.Scanpath(fixations)
        eq_(len(fixations), len(scanpath))
        
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
        eq_(fixations[0].time, 18750)
        eq_(fixations[0].time_midpoint(), 18883)

class TestScanpath(object):
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
        scanpath = gazepoint.Scanpath(points = self.points)
        for p in scanpath:
            assert isinstance(p, self.generic_factory.type_to_produce)
    
    def test_scanpath_is_iterable(self):
        scanpath = gazepoint.Scanpath(points = self.points)
        eq_(scanpath[0].time, 0)
    
    def test_scanpath_is_slicable(self):
        scanpath = gazepoint.Scanpath(points = self.points)
        eq_(len(scanpath[0:2]), 2)
        eq_(type(scanpath[0:2]), type(scanpath))
    
    def test_scanpath_returns_all_with_free_criterion_in_valid(self):
        def criterion(point):
            return True
            
        scanpath = gazepoint.Scanpath(points = self.points)
        valid = scanpath.valid_points(criterion)
        eq_(len(valid), len(scanpath))
        
        
    def test_scanpath_returns_none_with_false_criterion_in_valid(self):
        def criterion(point):
            return False
            
        scanpath = gazepoint.Scanpath(points = self.points)
        valid = scanpath.valid_points(criterion)
        eq_(len(valid), 0)
        
    def test_scanpath_returns_valid_points_with_limiting_criterin(self):
        def criterion(point):
            return (point.x > 0 and point.x < 800)
    
    def test_scanpath_computes_total_length(self):
        scanpath = gazepoint.Scanpath(points = self.points)
        eq_(float(len(self.points)), scanpath.total_duration)
    
    def test_scanpath_computes_mean(self):
         scanpath = gazepoint.Scanpath(points = self.points)
         x, y = scanpath.mean()
         eq_(int(x), 334)
         eq_(int(y), 494)
        
    def test_mean_returns_none_for_zero_length(self):
        sp = gazepoint.Scanpath(points = [])
        assert sp.mean() is None
        
    def test_scanpath_computes_median(self):
        sp = gazepoint.Scanpath(points = self.points)
        x, y = sp.median()
        eq_((x,y), (357.5, 509.0))
    
    def test_scanpath_returns_nont_for_zero_length(self):
        sp = gazepoint.Scanpath(points = [])
        assert sp.median() is None

    def test_recenter_duplicates_scanpath(self):
        scanpath = gazepoint.Scanpath(points = self.points)
        sp2 = scanpath.recenter_by(-10, -20)
        assert not scanpath[0] is sp2[0]
    
    def test_recenter_changes_x_and_y(self):
        scanpath = gazepoint.Scanpath(points = self.points)
        sp2 = scanpath.recenter_by(-10, -20)
        for i in range(0, len(scanpath)):
            op = scanpath[i]
            np = sp2[i]
            eq_(op.x-10, np.x)
            eq_(op.y-20, np.y)
    
    def test_scanpath_constrains(self):
        scanpath = gazepoint.Scanpath(points = self.points)
        pp = scanpath.constrain_to(
            (60,0),
            (10,1),
            (400,400),
            (90,90)
        )
        p_ar = pp.as_array()
        eq_(min(p_ar[:,0]), 0)
        eq_(max(p_ar[:,0]), 400)
        eq_(min(p_ar[:,1]), 1)
        eq_(max(p_ar[:,1]), 90)

    def test_points_in_filters(self):
        scanpath = gazepoint.Scanpath(points = self.points)
        rect = shapes.Rectangle(300,500,360,600)
        filtered = scanpath.points_within(rect)
        assert len(filtered) < len(scanpath)
        
    def test_points_convert_to_numpy(self):
        scanpath = gazepoint.Scanpath(points = self.points)
        npath = scanpath.as_array()
        eq_(np.ndarray, type(npath))
        eq_(len(scanpath), len(npath))
        
    def test_points_convert_limited_properties(self):
        scanpath = gazepoint.Scanpath(points = self.points)
        props = ('x')
        npath = scanpath.as_array(props)
        eq_((len(scanpath), len(props)), npath.shape)
    
    def test_time_index_finds_at_zero(self):
        pp = gazepoint.Scanpath(points = self.points)
        eq_(0, pp.time_index(0))
    
    def test_time_index_finds_at_largish(self):
        pp = gazepoint.Scanpath(points = self.points)
        eq_(2, pp.time_index(35))
    
    def test_time_index_gets_last_point_for_large_t(self):
        pp = gazepoint.Scanpath(points = self.points)
        eq_(len(pp), pp.time_index(100000))

class TestIViewScanpath(object):
    def __init__(self):
        super(TestIViewScanpath, self).__init__()
        
    def setup(self):
        self.points = mock_objects.iview_noisy_point_list()
        self.path = gazepoint.IViewScanpath(
            samples_per_second=60, points=self.points,
            measures=gazepoint.IView2PointFactory().numeric_measures)
        
    @raises(TypeError)
    def test_iview_scanpath_requires_samples_per_second(self):
        gazepoint.IViewScanpath()
    
    def test_to_array_is_proper_shape(self):
        arr = self.path.as_array()
        eq_(len(self.path), arr.shape[0])
        eq_(len(self.path.measures), arr.shape[1])
    
    def test_finds_points_in_shape(self):
        rect = shapes.Rectangle(300,500,360,600)
        filtered = self.path.points_within(rect)
        neq_(0, len(filtered))
        gt_(len(self.path), len(filtered))
    
    def test_constrain_works(self):
        pre_ar = self.path.as_array(('x')) < 400
        lt_(0, np.sum(pre_ar))
        constrained = self.path.constrain_to(
            (400, 400), (300,300), (800, 800), (600,600))
        ar = constrained.as_array(('x'))
        eq_(0, np.sum(ar < 400))
    
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

    def test_has_interpolable_attributes(self):
        for attr in gazepoint.Point.interp_attrs:
            x = getattr(self.hundreds, attr)
    
    def test_interpolates(self):
        p = gazepoint.Point(50,50)
        p.time = 50
        p.interpolate_from(self.hundreds)
        eq_(100, p.x)
        eq_(100, p.y)
        eq_(50, p.time)

class TestIViewPoint(object):
    def __init__(self):
        super(TestIViewPoint, self).__init__()
        
    def setup(self):
        self.pt = gazepoint.IViewPoint(x=100, y=100, diam_h=100)
    
    def test_has_interpolable_attributes(self):
        for attr in gazepoint.IViewPoint.interp_attrs:
            x = getattr(self.pt, attr)
    
    def test_interpolates(self):
        p = gazepoint.IViewPoint(x=50, y=50, diam_h=50)
        p.time = 50
        p.interpolate_from(self.pt)
        eq_(100, p.x)
        eq_(100, p.y)
        eq_(100, p.diam_h)
        eq_(50, p.time)
        