# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.
from __future__ import with_statement

from gazehound import presentation

class TestPresentation(object):
    def setup(self):
        pass
        
    def test_presentations_with_normal_times_are_valid(self):
        p = presentation.Presentation(start = 0, end = 10)
        assert p.valid()
        
    def test_presentations_without_times_are_invalid(self):
        p = presentation.Presentation(start = None, end = None)
        assert not p.valid()
        
    def test_presentation_with_equal_start_and_end_is_invalid(self):
        p = presentation.Presentation(start = 0, end = 0)
        assert not p.valid()
        
    def test_presentation_with_start_before_end_is_invalid(self):
        p = presentation.Presentation(start = 10, end = 0)
        assert not p.valid()

class TestPresentationFactory(object):
    
    def setup(self):
        self.name_on_off_ary = [
            ['fixation', '10', '50'],
            ['kitten', '60', '90'],
            ['batman', '100', '150']
        ]
        
        self.name_on_off_map = [
            ('name', str),
            ('start', int),
            ('end', int)
        ]
        
        self.on_off_name_ary = [
            ['10', '50', 'fixation'],
            ['60', '90', 'kitten'],
            ['100', '150', 'batman']
        ]
        
        self.on_off_name_map = [
            ('start', int),
            ('end', int),
            ('name', str)
        ]
        
        self.generic_factory = presentation.PresentationFactory(
            presentation.Presentation
        )
        
    
    def teardown(self):
        pass
    
        
    def test_stim_length_converts(self):
        stims = self.generic_factory.from_component_list(
            self.name_on_off_ary,
            self.name_on_off_map
        )
        assert len(stims) == len(self.name_on_off_ary)
    
    def test_components_maps_name_in_order(self):
        stims = self.generic_factory.from_component_list(
            self.name_on_off_ary,
            self.name_on_off_map
        )
        for i in range(0, len(stims)):
            assert stims[i].name == self.name_on_off_ary[i][0]

    def test_components_map_converts_types(self):
        stims = self.generic_factory.from_component_list(
            self.name_on_off_ary,
            self.name_on_off_map
        )
        assert all(isinstance(stim.start, int) for stim in stims)
    
    def test_components_maps_name_out_of_order(self):
        stims = self.generic_factory.from_component_list(
            self.on_off_name_ary,
            self.on_off_name_map
        )
        for i in range(0, len(stims)):
            assert stims[i].name == self.on_off_name_ary[i][2]