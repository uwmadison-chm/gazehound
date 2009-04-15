# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.
import csv
import re
from gazepoint import *
import timeline
import presentation

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
        opts_for_parser = {}
    ):
        self.__lines_cleaned = None
        self.parser = None
        self.file_data = file_data
        self.skip_comments = skip_comments
        self.comment_char = comment_char
        self.opts_for_parser = opts_for_parser
        for prop, val in self.__class__.STANDARD_DIALECT.iteritems():
            if not self.opts_for_parser.has_key(prop):
                self.opts_for_parser[prop] = val
    
    
    def __len__(self):
        self.__setup_parser()
        return len(self.__lines_cleaned)
    
    def comment_lines(self):
        comment_lines = []
        for line in self.file_data:
            stripped = line.strip()
            if (len(stripped) == 0 or
                stripped.startswith(self.comment_char)):
                comment_lines.append(line)
            else:
                break
        return comment_lines
    
    def __iter__(self):
        # We just need to implement next(self)
        return self
    
    def next(self):
        self.__setup_parser()
        return self.parser.next()
        
    def __setup_parser(self):
        self.__set_lines_cleaned()
        if self.parser is None:
            self.parser = csv.reader(
                self.__lines_cleaned, **self.opts_for_parser
            )
        
    def __set_lines_cleaned(self):
        if self.__lines_cleaned is not None:
            return
            
        if not self.skip_comments:
            self.__lines_cleaned = self.file_data
            return
            
        for i in range(len(self.file_data)):
            stripped = self.file_data[i].strip()
            if (len(stripped) > 0 and not
                stripped.startswith(self.comment_char)):
                break
        
        self.__lines_cleaned = self.file_data[i:]
    

class IViewReader(DelimitedReader):
    """A reader for files produced by SMI's iView software"""
    def __init__(self, header_map,
        file_data = None, skip_comments = True, comment_char = "#",
        opts_for_parser = {}):
        
        super(IViewReader, self).__init__(
            file_data, skip_comments, comment_char, opts_for_parser
        )
        self.header_map = header_map

    def header_pairs(self):
        coms = self.comment_lines()
        coms = [re.sub(("^%s" % self.comment_char), '', l).strip() for l in coms]
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
        opts_for_parser = {}):
        
        super(IViewScanpathReader, self).__init__(
            self.__header_map(), file_data, skip_comments, 
            comment_char, opts_for_parser
        )
    
    def pointpath(self):
        """Return a list of Points representing the scan path."""
        fact = IViewPointFactory()
        points = fact.from_component_list(self)
        return PointPath(points = points)
        
    
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
    

class FixationReader(DelimitedReader):
    # The second parameter is a function, taking one string argument,
    # that converts the value to its expected format.
    HEADER_MAP = {
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
    
    def __init__self( 
        file_data = None, skip_comments = True, comment_char = "#",
        opts_for_parser = {}):
        super(FixationReader, self).__init__(
            file_data, skip_comments, comment_char, opts_for_parser
        )
        
    def header(self):
        return None
        
class TimelineReader(object):
    """ 
    Reads files of the format: stim_name \t onset \t offset and creates
    timelines from them.
    """
    def __init__(self, stim_lines = None):
        super(TimelineReader, self).__init__()
        self.stim_lines = stim_lines
        
    def timeline(self):
        dr = presentation.DelimitedReader(
            lines = self.stim_lines, lines_to_skip = 1
        )
        presentations = dr.make_presentations()
        return timeline.Timeline(presentations = presentations)