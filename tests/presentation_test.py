import gazehound.stimulus
from gazehound.stimulus import presentation

class TestPresentationFactory(object):
    
    def setup(self):
        self.name_on_off_ary = [
            ['fixation', '10', '50'],
            ['kitten', '60', '90'],
            ['batman', '100', '150']
        ]
        
        self.name_on_off_map = [
            {'name': str},
            {'start': int},
            {'end': int}
        ]
        
        self.on_off_name_ary = [
            ['10', '50', 'fixation'],
            ['60', '90', 'kitten'],
            ['100', '150', 'batman']
        ]
        self.on_off_name_map = [
            {'start':int},
            {'end':int},
            {'name':str}
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
        for i in range(0, len(stims)):
            assert type(stims[i].start) is int
    
    def test_components_maps_name_out_of_order(self):
        stims = self.generic_factory.from_component_list(
            self.on_off_name_ary,
            self.on_off_name_map
        )
        for i in range(0, len(stims)):
            assert stims[i].name == self.on_off_name_ary[i][2]
        