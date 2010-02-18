# Part of the gazehound package for analzying eyetracking data
#
# Copyright (c) 2010 Board of Regents of the University of Wisconsin System
#
# Written by Nathan Vack <njvack@wisc.edu> at the Waisman Laborotory
# for Brain Imaging and Behavior, University of Wisconsin - Madison.

# A simple set of functions to generate mock objects for use in
# our tests

from __future__ import with_statement
from gazehound import gazepoint, event, timeline, readers, viewing, shapes
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

def iview_points_noisy():
    return gazepoint.PointPath(gazepoint.IViewPointFactory().from_component_list([
    ['0', '0', '5034', '3490', '4687', '3380', '358', '543', '2400', '2080'],
    ['16', '0', '5042', '3491', '4690', '3388', '353', '528', '2432', '2112'],
    ['33', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['50', '0', '5050', '3472', '4688', '3391', '365', '473', '2432', '2080'], 
    ['67', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['83', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['100', '0', '5050', '3477', '4692', '3388', '357', '490', '2432', '2144'],
    ['116', '0', '0', '0', '0', '0', '0', '0', '0', '0'], 
    ['133', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['150', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['167', '0', '5050', '3477', '4692', '3388', '357', '490', '2432', '2144'],
    ['183', '0', '5050', '3472', '4688', '3391', '365', '473', '2432', '2080'], 
    ['200', '0', '5017', '3595', '4691', '3367', '58', '490', '2368', '1824'],
    ['216', '0', '4929', '3946', '4686', '3357', '518', '528', '2144', '1184'],
    ]))

def iview_points_blinky():
    return gazepoint.PointPath(gazepoint.IViewPointFactory().from_component_list([
    ['0', '0', '5034', '3490', '4687', '3380', '358', '577', '2400', '2080'],
    ['16', '0', '5042', '3491', '4690', '3388', '353', '528', '2432', '2112'],
    ['33', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['50', '0', '5050', '3472', '4688', '3391', '365', '473', '2432', '2080'], 
    ['67', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['83', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['100', '0', '5050', '3477', '4692', '3388', '357', '490', '2432', '2144'],
    ['116', '0', '0', '0', '0', '0', '0', '0', '0', '0'], 
    ['133', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['150', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['167', '0', '5050', '3477', '4692', '3388', '357', '490', '2432', '2144'],
    ['183', '0', '5050', '3472', '4688', '3391', '365', '473', '2432', '2080'], 
    ['200', '0', '5017', '3595', '4691', '3367', '58', '490', '2368', '1824'],
    ['216', '0', '4929', '3946', '4686', '3357', '518', '488', '2144', '1184'],
    ['233', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['250', '0', '0', '0', '0', '0', '0', '0', '0', '0'], 
    ['267', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['283', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['300', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['316', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['333', '0', '5050', '3477', '4692', '3388', '357', '700', '2432', '2144'],
    ['350', '0', '5050', '3472', '4688', '3391', '365', '610', '2432', '2080'], 
    ['367', '0', '5017', '3595', '4691', '3367', '582', '490', '2368', '1824'],
    ['383', '0', '4929', '3946', '4686', '3357', '520', '485', '2144', '1184'],
    ['400', '0', '5017', '3595', '4691', '3367', '559', '490', '2368', '1824'],
    ['416', '0', '4929', '3946', '4686', '3357', '522', '528', '2144', '1184'],
    ['433', '0', '5050', '3477', '4692', '3388', '357', '490', '2432', '2144'],
    ['450', '0', '5050', '3472', '4688', '3391', '365', '473', '2432', '2080'], 
    ['467', '0', '5017', '3595', '4691', '3367', '58', '490', '2368', '1824'],
    ['483', '0', '4929', '3946', '4686', '3357', '518', '528', '2144', '1184'],
    ]))
        
def smi_pointpath_normal():
    lines = []
    with open(EX_PATH+"/iview_normal.txt") as f:
        lines = f.readlines()
    ir = readers.IViewScanpathReader(lines)
    return ir.pointpath()

def smi_fixation_ary():
    # Fields are:
    #Start#	End#	StartT	EndT	X	Y	Object	Duration
    return([
    ['1125', '1141', '18750', '19017', '365', '236', '1', '267'],
    ['1166', '1188', '19433', '19800', '182', '551', '1', '367'],
    ['1201', '1255', '20017', '20917', '410', '299', '1', '900'],
    ['1260', '1263', '21000', '21051', '365', '236', '1', '51'],
    ['1278', '1321', '21305', '22017', '365', '236', '1', '712'],
    ['1345', '1375', '22416', '22914', '365', '236', '1', '498'],
    ['1475', '1629', '24583', '27150', '365', '236', '1', '2567'],
    ['1927', '2083', '32117', '34717', '365', '236', '1', '2600'],
    ])

def smi_fixation_points():
    ivf = gazepoint.IViewFixationFactory()
    return gazepoint.PointPath(ivf.from_component_list(smi_fixation_ary()))

def tiny_timeline():
    lines = []
    with open(EX_PATH+"/pres_tiny.txt") as f:
        lines = [line.strip() for line in f.readlines()]
    tr = readers.TimelineReader(lines)
    return tr.timeline
    
def tiny_viewings():
    pointpath = smi_pointpath_normal()
    timeline = tiny_timeline()
    return viewing.Combiner(
        pointpath = pointpath, timeline = timeline
    ).viewings()

def smi_pointpath_spreadout():
    ivf = gazepoint.IViewPointFactory()
    return gazepoint.PointPath(ivf.from_component_list(smi_ary_spreadout()))
    

def standard_timeline():
    data = [
        ['fixation', '19992', '20892'],
        ['3102', '21003', '32992'],
        ['fixation', '42992', '43892'],
        ['6230', '43992', '55992'],
        ['fixation', '60992', '61892'],
        ['9810', '62008', '73992'],
    ]
    pres_fact = event.EventFactory()
    return timeline.Timeline(
        pres_fact.from_component_list(
            data, [('name', str), ('start', int), ('end', int)]
        )
    )

def simple_timeline():
    data = [
        ['120', '1350', 'stim1'],
        ['1490', '1900', 'objects']
    ]
    
    pres_fact = event.EventFactory()
    events = pres_fact.from_component_list(
        data, [('start', int), ('end', int), ('name', str)]
    )
    return timeline.Timeline(events)
    
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
    