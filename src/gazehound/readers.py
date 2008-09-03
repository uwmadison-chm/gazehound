# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.
import csv

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
    
    def __iter__(self):
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
            