# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.
import csv

class Presentation(object):
    """ The generic stimulus presentation, providing start time, end time, and
    name. Can also contain viewing data (Is this a good idea?)
    """
    
    def __init__(self, start=None, end=None, name=None, pointpath = None):
        self.start = start
        self.end = end
        self.name = name
        self.pointpath = pointpath
        
    def valid(self):
        try:
            return self.start < self.end
        except:
            return False


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
    def __init__(self, *args, **keywords):
        Presentation.__init__(self, *args, **keywords)
        


class PresentationFactory(object):
    """ A factory that generates lists of Presentations from enumerable
    things.
    """
    def __init__(self, type_to_produce=Presentation):
        self.type_to_produce = type_to_produce
    
    def from_component_list(self, components, attribute_list):
        """ 
        Build a list of Presentations from a set of components.
        Presentations will be of the type specified at factory construction
        time.
        
        Arguments:
        components -- A list of lists -- each item of the first list
            containing one presentation, each item of the second containing
            one attribute.
        
        attribute_list -- A list of tuples, containing (attribute_name, type). 
            
        Components containing a different number of elements than the
        attribute_list will cause problems -- make sure you've filtered
        your input.
        """
        
        presentations = []
        expected_length = len(attribute_list)
        for data in components:
            pres = self.type_to_produce()
            
            # Map the listed attributes to their proper homes
            for i in range(0, expected_length):
                mapping = attribute_list[i]
                attr = mapping[0]
                attr_type = mapping[1]
                setattr(pres, attr, attr_type(data[i]))
            
            presentations.append(pres)
        return presentations
    

class DelimitedReader(object):
    """
    Presentations from themReads an enumeration of delimited strings and 
    constructs Presentations from them."""
    
    def __init__(self, lines = [], 
        delimiter = "\t",
        lines_to_skip = 0, 
        type_to_produce = Presentation,
        mapping = [('name', str), ('start', int), ('end', int)]):
        
        self.lines = lines
        self.delimiter = delimiter
        self.lines_to_skip = lines_to_skip
        self.type_to_produce = type_to_produce
        self.mapping = mapping
        
    
    def make_presentations(self):
        """
        Create a list of Presentation objects from self.lines, delimited with
        self.delimter after skipping self.lines_to_skip. Always return
        a list or raise an error.
        """
        if self.lines is None:
            return []
        factory = PresentationFactory(self.type_to_produce)
        reader = csv.reader(
            self.lines_after_skip(),
            delimiter=self.delimiter
        )
        pres_list = factory.from_component_list(
            reader, self.mapping
        )
        return pres_list
        
    def lines_after_skip(self):
        return self.lines[self.lines_to_skip:]
            
    

        