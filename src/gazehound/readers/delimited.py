# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

from __future__ import with_statement
import csv


class DelimitedReader(object):

    """
    Converts files (or other enumerations of strings) into lists of lists.
    Optionally skips leading lines starting with some comment character
    (by defult the #)
    """

    STANDARD_DIALECT = {'delimiter': "\t"}

    def __init__(self,
        file_data=None, skip_comments=True, comment_char="#",
        opts_for_parser={}, filename=None, skip_lines=0):
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

    def read_file(self, filename, mode = 'rU'):
        """
        Convenience method. Reads a file into self.file_data. Generally uses
        the 'rU' method, which is almost certainly what you want.
        """
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
                self.__content_lines, **self.opts_for_parser)

    def __partition_lines(self):
        if len(self.__content_lines) > 0:
            return

        for line in self.file_data[self.skip_lines:]:
            stripped = line.strip()
            if self.skip_comments and stripped.startswith(self.comment_char):
                self.__comment_lines.append(stripped)
            elif len(stripped) > 0:
                self.__content_lines.append(stripped)


