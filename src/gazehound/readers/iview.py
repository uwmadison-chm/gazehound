# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

import re
from gazehound.readers.delimited import DelimitedReader
from gazehound import gazepoint

class IViewReader(DelimitedReader):
    """A reader for files produced by SMI's iView software"""

    def __init__(self, header_map,
        file_data = None, skip_comments = True, comment_char = "#",
        opts_for_parser = {}, filename = None):

        super(IViewReader, self).__init__(
            file_data, skip_comments, comment_char, opts_for_parser, filename)
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


class IView2ScanpathReader(IViewReader):
    """A reader for files produced by SMI's iView software"""

    def __init__(self,
        file_data=None, skip_comments=True, comment_char="#",
        opts_for_parser={}, filename=None):

        super(IView2ScanpathReader, self).__init__(
            self.__header_map(), file_data, skip_comments,
            comment_char, opts_for_parser, filename)

    def pointpath(self):
        """Return a list of Points representing the scan path."""
        fact = gazepoint.IView2PointFactory()
        points = fact.from_component_list(self)
        return gazepoint.IViewPointPath(
            points=points, samples_per_second=self.header()['sample_rate'])

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
                'calibration_offset',
                lambda x: [int(e) for e in x.split("\t")]),
            'Size Of Calibration Area': (
                'calibration_size',
                lambda x: [int(e) for e in x.split("\t")]),
            'Sample Rate': ('sample_rate', int)}


class IView3PointPathReader(IViewReader):
    # A list of 4-tuples:
    # measure_name,
    # measure_column(s),
    # conversion_from_string_function
    standard_column_mapping = [
        ('timestamp', 'Time', int),
        ('x', ['R POR X [px]', 'L POR X [px]'], float),
        ('y', ['R POR Y [px]', 'L POR Y [px]'], float),
        ('pupil_h', ['R Raw X [px]', 'L Raw X [px]'], float),
        ('pupil_v', ['R Raw Y [px]', 'L Raw Y [px]'], float),
        ('corneal_reflex_1_h', ['R CR1 X [px]', 'L CR1 X [px]'], float),
        ('corneal_reflex_1_v', ['R CR1 Y [px]', 'L CR1 Y [px]'], float),
        ('corneal_reflex_2_h', ['R CR2 X [px]', 'L CR2 X [px]'], float),
        ('corneal_reflex_2_v', ['R CR2 Y [px]', 'L CR2 Y [px]'], float),
        ('diam_h', ['R Dia X [px]', 'L Dia X [px]'], float),
        ('diam_v', ['R Dia Y [px]', 'L Dia Y [px]'], float),
    ]
    
    def __init__(self, file_data=None, skip_comments=True, comment_char="##",
        opts_for_parser={}, filename=None, 
        column_mapping=standard_column_mapping):
        
        super(IView3PointPathReader, self).__init__(
            self.__header_map, file_data, skip_comments, comment_char, 
            opts_for_parser, filename)
        self.column_mapping = column_mapping
        
    def pointpath(self):
        fact = gazepoint.IView3PointFactory(self.measure_mapping)
        points = fact.from_component_list(self)
        return gazepoint.IView3Pointpath(
            points=points, samples_per_second=self.header()['sample_rate'])
    
    @property
    def measure_mapping(self):
        self._setup_parser()
        return self._meas_map
    
    @property
    def column_headers(self):
        self._setup_parser()
        return self._column_headers
    
    def _partition_lines(self):
        if len(self._content_lines) > 0:
            return
        super(IView3PointPathReader, self)._partition_lines()
        self._column_header_line = self._content_lines[0]
        self._column_headers = self._column_header_line.split("\t")
        self._content_lines = self._content_lines[1:]
        self._build_measure_map()
        
        
    def _build_measure_map(self):
        self._meas_map = {}
        for measure_name, cols, fx in self.column_mapping:
            self._meas_map[measure_name] = (self._col_index(cols), fx)
    
    def _col_index(self, cols):
        if type(cols) == str:
            cols = [cols]
        
        return [self._column_headers.index(c) for c in cols 
                if c in self._column_headers][0]
    
    @property
    def __header_map(self):
        # The second parameter is a function, taking one string argument,
        # that converts the value to its expected format.
        return {
            'Version': ('file_version', str),
            'Format': ('file_format', str),
            'Subject': ('subject', str),
            'Date': ('date_string', str),
            'Description': ('description', str),
            'Number of Samples': ('recorded_points', int),
            'Calibration Area': (
                'calibration_size',
                lambda x: [int(e) for e in x.split("\t")]),
            'Sample Rate': ('sample_rate', int),
            'Calibration Type' : ('calibration_type', str),
            'Stimulus Dimension [mm]' : ('stimulus_dimension', 
                lambda x: [int(e) for e in x.split("\t")] + ['mm']),
            'Head Distance [mm]' : ('head_distance',
                lambda x : [x, 'mm']),
            'Reversed' : ('reversed', str)
        }


class IViewFixationReader(IViewReader):

    def __init__(self,
        file_data=None, skip_comments=True, comment_char="#",
        opts_for_parser={}, filename=None):

        super(IViewFixationReader, self).__init__(
            self.__header_map(), file_data, skip_comments,
            comment_char, opts_for_parser, filename)

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
                'calibration_offset',
                lambda x: [int(e) for e in x.split("\t")]),
            'Size Of Calibration Area': (
                'calibration_size',
                lambda x: [int(e) for e in x.split("\t")]),
            'Minimal Time': ('minimal_time', int),
            'Maximal Pixel': ('maximal_pixel', int)}

    def pointpath(self):
        """Return a list of Points representing the scan path."""
        fact = gazepoint.IViewFixationFactory()
        points = fact.from_component_list(self)
        return gazepoint.PointPath(points = points)