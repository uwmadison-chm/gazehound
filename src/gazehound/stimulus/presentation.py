# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.


class Presentation(object):
    """ The generic stimulus presentation, providing start time, end time, and
    name.
    """
    
    def __init__(self, start=None, end=None, name=None):
        self.start = start
        self.end = end
        self.name = name


class Picture(Presentation):
    """ A picture-type stimulus. Generally also contains filename, type,
    width, and height.
    """    
    def __init__(self, start=None, end=None, name=None, path=None, type=None,
                width=None, height=None):
        Presentation.__init__(self, start, end, name)
        self.path = path
        self.type = type
        self.width = width
        self.height = height

class Blank(Presentation):
    """ A 'nothing' type stimulus.
    """
    def __init__(self, *args):
        Presentation.__init__(self, *args)
        


class PresentationFactory(object):
    """ A factory that generates lists of Presentations from enumerable
    things.
    """
    def __init__(self, type_to_produce=Presentation):
        self.type_to_produce = type_to_produce
    
    def from_component_list(components, attribute_list):
        """ 
        Build a list of Presentations from a set of components.
        Presentations will be of the type specified at factory construction
        time.
        
        Arguments:
        components -- A list of lists -- each item of the first list
            containing one presentation, each item of the second containing
            one attribute.
        
        attribute_list -- A list containing the expected attributes for each
            stimulus, in the order they appear on each line.
            
        Components containing a different number of elements than the
        attribute_list will be skipped.
        """
        
        presentations = []
        expected_length = len(attribute_list)
        for data in components:
            if len(data) == expected_length:
                pres = self.type_to_produce()
                
                # Map the listed attributes to 
                for i in range(0, expected_length):
                    setattr(pres, attr[i], data[i])
                    
                presentations.append(pres)
        return presentations
    

