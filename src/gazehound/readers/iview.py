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


class IViewScanpathReader(IViewReader):
    """A reader for files produced by SMI's iView software"""

    def __init__(self,
        file_data=None, skip_comments=True, comment_char="#",
        opts_for_parser={}, filename=None):

        super(IViewScanpathReader, self).__init__(
            self.__header_map(), file_data, skip_comments,
            comment_char, opts_for_parser, filename)

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
                'calibration_offset',
                lambda x: [int(e) for e in x.split("\t")]),
            'Size Of Calibration Area': (
                'calibration_size',
                lambda x: [int(e) for e in x.split("\t")]),
            'Sample Rate': ('sample_rate', int)}


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