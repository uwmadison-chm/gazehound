# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2008 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

# A simple set of functions to generate mock objects for use in
# our tests

from __future__ import with_statement
from gazehound import gazepoint, presentation, timeline, readers, viewing, shapes
from gazehound.runners import gaze_statistics
from os import path

EX_PATH = path.abspath(path.dirname(__file__))+"/examples"

def smi_ary_spreadout():
    return ([
        ['100', '0', '5034', '3490', '4687', '3380', '358', '543', '2400', '2080'],
        ['1160', '0', '5042', '3491', '4690', '3388', '353', '528', '2432', '2112'],
        ['1330', '0', '5050', '3477', '4692', '3388', '357', '490', '2432', '2144'],
        ['1500', '0', '5050', '3472', '4688', '3391', '365', '473', '2432', '2080'], 
        ['1660', '0', '5017', '3595', '4691', '3367', '58', '986', '2368', '1824'],
        ['1830', '0', '4929', '3946', '4686', '3357', '518', '-56', '2144', '1184'],
    ])
    
    

def smi_scanpath_normal():
    lines = []
    with open(EX_PATH+"/iview_normal.txt") as f:
        lines = f.readlines()
    ir = readers.IViewScanpathReader(lines)
    return ir.scanpath()

def tiny_timeline():
    lines = []
    with open(EX_PATH+"/pres_tiny.txt") as f:
        lines = [line.strip() for line in f.readlines()]
    tr = readers.TimelineReader(lines)
    return tr.timeline()
    
def tiny_viewings():
    scanpath = smi_scanpath_normal()
    timeline = tiny_timeline()
    return viewing.Combiner(
        scanpath = scanpath, timeline = timeline
    ).viewings()

def smi_scanpath_spreadout():
    ivf = gazepoint.IViewPointFactory()
    return gazepoint.ScanPath(ivf.from_component_list(smi_ary_spreadout()))
    

def simple_timeline():
    data = [
        ['120', '1350', 'stim1'],
        ['1490', '1900', 'objects']
    ]
    
    pres_fact = presentation.PresentationFactory()
    presentations = pres_fact.from_component_list(
        data, [('start', int), ('end', int), ('name', str)]
    )
    return timeline.Timeline(presentations)
    
def general_gaze_stats():
    return [
        gaze_statistics.GazeStats(
            presented = 'screen', area = 'all', start_ms = 0, end_ms = 21000, 
            total_points = 350, 
            points_in = 296, points_out = 54, 
            valid_strict = 296, valid_lax = 316
        )
    ]
    
def shape_tuples():
    return [
        ('object1', shapes.Rectangle(0, 1, 60, 24)),
        ('object2', shapes.Ellipse(0, 1, 21, 599))
    ]
    