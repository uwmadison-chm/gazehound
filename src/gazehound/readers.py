# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.
from __future__ import with_statement

import csv
import re
from gazehound import timeline, event, gazepoint


class DelimitedReader(object):
    
    """
    Converts files (or other enumerations of strings) into lists of lists.
    Optionally skips leading lines starting with some comment character
    (by defult the #)
    """

    STANDARD_DIALECT = {
        'delimiter': "\t"
    }
    def __init__(self, 
        file_data = None, skip_comments = True, comment_char = "#",
        opts_for_parser = {}, filename = None, skip_lines = 0
    ):
        self.__comment_lines = []
        self.__content_lines = []
        self.parser = None
        self.file_data = file_data
        self.skip_comments = skip_comments
        self.comment_char = comment_char
        self.opts_for_parser = self.__class__.STANDARD_DIALECT.copy()
        self.opts_for_parser.update(opts_for_parser)
        self.skip_lines = skip_lines
        self.filename = filename
        if file_data is None and filename is not None:
            self.read_file(filename)
    

    """ 
    Convenience method. Reads a file into self.file_data. Generally uses
    the 'rU' method, which is almost certainly what you want.
    """
    def read_file(self, filename, mode = 'rU'):
        with open(filename, mode) as f:
            self.file_data = f.readlines()
            
    def __len__(self):
        self.__setup_parser()
        return len(self.__content_lines)
    
    @property
    def comment_lines(self):
        self.__setup_parser()
        return self.__comment_lines
    
    @property
    def content_lines(self):
        self.__setup_parser()
        return self.__content_lines
    
    def __iter__(self):
        # We just need to implement next(self)
        return self
    
    def next(self):
        self.__setup_parser()
        return self.parser.next()
        
    def __setup_parser(self):
        self.__partition_lines()
        if self.parser is None:
            self.parser = csv.reader(
                self.__content_lines, **self.opts_for_parser
            )
        
    def __partition_lines(self):
        if len(self.__content_lines) > 0:
            return
                
        for line in self.file_data[self.skip_lines:]:
            stripped = line.strip()
            if self.skip_comments and stripped.startswith(self.comment_char):
                self.__comment_lines.append(stripped)
            elif len(stripped) > 0:
                self.__content_lines.append(stripped)
    
class IViewReader(DelimitedReader):
    """A reader for files produced by SMI's iView software"""
    def __init__(self, header_map,
        file_data = None, skip_comments = True, comment_char = "#",
        opts_for_parser = {}, filename = None):
        
        super(IViewReader, self).__init__(
            file_data, skip_comments, comment_char, opts_for_parser, filename
        )
        self.header_map = header_map

    def header_pairs(self):
        coms = [re.sub(("^%s" % self.comment_char), '', l).strip() 
                for l in self.comment_lines]
        return [l.split(":\t", 1) for l in coms]

    def header(self):
        header_pairs = self.header_pairs()

        header_pairs = [p for p in header_pairs if len(p) == 2]
        # Kill line endings in header_pairs
        header_pairs = [[p[0], p[1].strip()] for p in header_pairs]

        header_ret = {}
        for p in header_pairs:
            cleaned_pair = self.__map_header_value(p)
            if cleaned_pair is not None:
                header_ret.update([cleaned_pair])
        return header_ret

    def __map_header_value(self, pair):
        """
        Return a tuple of the form (key, value), or None if 
        pair[0] isn't in HEADER_MAP
        """
        raw_key, raw_val = pair
        mapper = self.header_map.get(raw_key)
        if mapper is None:
            return None

        cleaned_key, converter = mapper

        cleaned_val = converter(raw_val)
        return (cleaned_key, cleaned_val)

        
class IViewScanpathReader(IViewReader):

    """A reader for files produced by SMI's iView software"""
    def __init__(self, 
        file_data = None, skip_comments = True, comment_char = "#",
        opts_for_parser = {}, filename = None):
        
        super(IViewScanpathReader, self).__init__(
            self.__header_map(), file_data, skip_comments, 
            comment_char, opts_for_parser, filename
        )
    

    def pointpath(self):
        """Return a list of Points representing the scan path."""
        fact = gazepoint.IViewPointFactory()
        points = fact.from_component_list(self)
        return gazepoint.PointPath(points = points)


    
    def __header_map(self):
        # The second parameter is a function, taking one string argument,
        # that converts the value to its expected format.
        return {
            'FileVersion': ('file_version', str),
            'Fileformat': ('file_format', str),
            'Subject': ('subject', str),
            'Date': ('date_string', str),
            'Description': ('description', str),
            '# of Pts Recorded': ('recorded_points', int),
            'Offset Of Calibration Area': (
                'calibration_offset', lambda x: [int(e) for e in x.split("\t")]
            ),
            'Size Of Calibration Area': (
                'calibration_size', lambda x: [int(e) for e in x.split("\t")]
            ),
            'Sample Rate': ('sample_rate', int)
        }
    

class IViewFixationReader(IViewReader):

    def __init__(self, 
        file_data = None, skip_comments = True, comment_char = "#",
        opts_for_parser = {}, filename = None):
        
        super(IViewFixationReader, self).__init__(
            self.__header_map(), file_data, skip_comments, 
            comment_char, opts_for_parser, filename
        )
    
    def __header_map(self):
        # The second parameter is a function, taking one string argument,
        # that converts the value to its expected format.
        return {
            'Subject': ('subject', str),
            'Date': ('date_string', str),
            'Description': ('description', str),
            '# Of Fixations': ('recorded_fixations', int),
            'Sample Rate': ('sample_rate', int),
            'Offset Of Calibration Area': (
                'calibration_offset', lambda x: [int(e) for e in x.split("\t")]
            ),
            'Size Of Calibration Area': (
                'calibration_size', lambda x: [int(e) for e in x.split("\t")]
            ),
            'Minimal Time': ('minimal_time', int),
            'Maximal Pixel': ('maximal_pixel', int)
        }

    def pointpath(self):
        """Return a list of Points representing the scan path."""
        fact = gazepoint.IViewFixationFactory()
        points = fact.from_component_list(self)
        return gazepoint.PointPath(points = points)


       
class TimelineReader(DelimitedReader):
    """ 
    Reads files of the format: stim_name \t onset \t offset and creates
    timelines from them.
    """
    def __init__(self, file_data = None, filename = None, skip_lines = 1):
        super(TimelineReader, self).__init__(
            file_data = file_data,
            filename = filename,
            skip_lines = skip_lines
        )
        self.components = self.__default_components()
        self.__events = []
        self.__timeline = []
    
    def __make_events(self):
        if len(self.__events) > 0:
            return
        factory = event.EventFactory()
        self.__events=factory.from_component_list(self, self.components)

    def __default_components(self):
        return [('name', str), ('start', int), ('end', int)]

    @property
    def events(self):
        self.__make_events()
        return self.__events
    
    @property
    def timeline(self):
        if len(self.__timeline) == 0:
            self.__timeline = timeline.Timeline(events = self.events)
        return self.__timeline
    
