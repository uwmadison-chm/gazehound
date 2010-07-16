# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

from gazehound.readers.delimited import DelimitedReader
from gazehound import event, timeline

class TimelineReader(DelimitedReader):
    """
    Reads files of the format: stim_name \t onset \t offset and creates
    timelines from them.
    """

    def __init__(self, file_data = None, filename = None, skip_lines = 1):
        super(TimelineReader, self).__init__(
            file_data = file_data,
            filename = filename,
            skip_lines = skip_lines)
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
