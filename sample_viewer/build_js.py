#!/usr/bin/env python
# coding=utf8
from __future__ import with_statement

import json

# So ok the plan of attack here is to go all like
# 1: Make a Timeline for every subject, decorated with points
# 2: Convert that into a list of events, with a pointpath for each
#    subject. Maybe order by event name?
# 3: Write the resulting structure out as javascript
# 
# SUPER OPTIONAL EXTRA CREDIT:
# Try a deblinked version!

import gazehound
from gazehound.readers import IViewScanpathReader, TimelineReader
from gazehound.viewing import Combiner


SUBJECTS = [
    {'name': '006', 'group': 'light_fix'}, 
    {'name': '007', 'group': 'dark_fix'}, 
    {'name': '008', 'group': 'light_fix'}, 
    {'name': '009', 'group': 'dark_fix'}, 
    {'name': '010', 'group': 'light_fix'},
]

viewer_groups = ['light_fix', 'dark_fix']

all_events = {}
stim_images = {}

output_wrapper = {}

for snum in [s['name'] for s in SUBJECTS]:
    print("Subject %s" % snum)
    spath = None
    tline = None
    spfile = "scanpaths/scanpath_%s.txt" % snum
    tlfile = "stim_timings/stims_%s.txt" % snum
    tline = TimelineReader(filename=tlfile).timeline
    spath = IViewScanpathReader(filename=spfile).pointpath()
    # print("tl: %s, sp: %s" % (len(tline), len(spath)))
    decorated = Combiner(timeline=tline, pointpath=spath).viewings()
    
    for e in decorated:
        if e.name not in all_events:
            stim_images[e.name] = "%s.png" % e.name
            all_events[e.name] = {}
        if snum not in all_events[e.name]:
            all_events[e.name][snum] = []
        all_events[e.name][snum].append([[p.x, p.y] for p in e.pointpath])

names = all_events.keys()
names.sort()
output_wrapper['stims'] = names
output_wrapper['viewers'] = SUBJECTS
output_wrapper['viewer_groups'] = viewer_groups
output_wrapper['stim_images'] = stim_images
output_wrapper['viewdata'] = all_events
output_wrapper['samples_per_second'] = 60


with open("js_data/pointdata_orig.js", "w") as f:
    f.write("EyeData = ")
    f.write(json.dumps(output_wrapper, f, indent=2))
