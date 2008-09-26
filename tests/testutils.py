# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

def gt_(a, b, msg = None):
    """Shorthand for 'assert a > b, "%r != %r" % (a, b)
    """
    assert a > b, msg or "%r <= %r" % (a, b)

def gte_(a, b, msg = None):
    """Shorthand for 'assert a >= b, "%r != %r" % (a, b)
    """
    assert a >= b, msg or "%r < %r" % (a, b)

def lt_(a, b, msg = None):
    """Shorthand for 'assert a < b, "%r != %r" % (a, b)
    """
    assert a < b, msg or "%r >= %r" % (a, b)


def lte_(a, b, msg = None):
    """Shorthand for 'assert a <= b, "%r != %r" % (a, b)
    """
    assert a <= b, msg or "%r > %r" % (a, b)

def includes_(l, elem, msg = None):
    """ Shorthand for 'assert elem in l'
    """
    assert elem in l, msg or "%r does not contain %r" % (l, elem)