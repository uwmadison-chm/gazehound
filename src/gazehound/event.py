# coding: utf8
# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.
import csv


class Event(object):
    """ The generic stimulus event, providing start time, end time, and
    name. Can also contain viewing data (Is this a good idea?)
    """

    def __init__(self, start=None, end=None, name=None, pointpath=None):
        self.start = start
        self.end = end
        self.name = name
        self.pointpath = pointpath

    def valid(self):
        try:
            return self.start < self.end
        except:
            return False

    @property
    def duration(self):
        return (self.end - self.start)


class Picture(Event):
    """ A picture-type stimulus. Generally also contains filename, type,
    width, and height.
    """

    def __init__(self, start=None, end=None, name=None, path=None, type=None,
                width=None, height=None):
        Event.__init__(self, start, end, name)
        self.path = path
        self.type = type
        self.width = width
        self.height = height


class Blank(Event):
    """ A 'nothing' type stimulus.
    """

    def __init__(self, *args, **keywords):
        Event.__init__(self, *args, **keywords)


class Blink(Event):
    """ An eyeblink. """

    def __init__(self, start, end, name=None):
        Event.__init__(self, start, end, name)


class EventFactory(object):
    """ A factory that generates lists of Events from enumerable
    things.
    """

    def __init__(self, type_to_produce=Event):
        self.type_to_produce = type_to_produce

    def from_component_list(self, components, attribute_list):
        """
        Build a list of Events from a set of components.
        Events will be of the type specified at factory construction
        time.

        Arguments:
        components -- A list of lists -- each item of the first list
            containing one event, each item of the second containing
            one attribute.

        attribute_list -- A list of tuples, containing (attribute_name, type).

        Components containing a different number of elements than the
        attribute_list will cause problems -- make sure you've filtered
        your input.
        """

        events = []
        expected_length = len(attribute_list)
        for data in components:
            pres = self.type_to_produce()

            # Map the listed attributes to their proper homes
            for i in range(0, expected_length):
                mapping = attribute_list[i]
                attr = mapping[0]
                attr_type = mapping[1]
                setattr(pres, attr, attr_type(data[i]))

            events.append(pres)
        return events
