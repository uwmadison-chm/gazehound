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
from gazehound.filters import iview

SUBJECTS = ['006', '007', '008', '009', '010']

viewer_groups = ['raw', 'deblinked', 'recentered']

viewer_directory = {}
viewers = []

all_events = {}
stim_images = {}


output_wrapper = {}
i = 0
for snum in SUBJECTS:
    print("Reading %s" % snum)
    spath = None
    tline = None
    spfile = "scanpaths/scanpath_%s.txt" % snum
    tlfile = "stim_timings/stims_%s.txt" % snum
    tline = TimelineReader(filename=tlfile).timeline
    
    pointpaths = {}
    
    spath = IViewScanpathReader(filename=spfile).pointpath()
    # print("tl: %s, sp: %s" % (len(tline), len(spath)))
    pointpaths['raw'] = Combiner(timeline=tline, pointpath=spath).viewings()
    
    denoised = iview.Denoise().process(spath)
    deblinked = iview.Deblink().deblink(denoised)
    pointpaths['deblinked'] = Combiner(timeline=tline, pointpath=deblinked).viewings()
    pointpaths['recentered'] = pointpaths['deblinked'].recenter_on(
            "fix_S", 399, 299).recenter_on("fix_D", 399, 299)
    
    for group in viewer_groups:
        swg = "%s-%s" % (snum, group)
        viewer_directory[swg] = i
        viewers.append({'name': swg, 'group': group})
        i += 1
        for e in pointpaths['raw']:
            if e.name not in all_events:
                stim_images[e.name] = "%s.png" % e.name
                all_events[e.name] = {}
            if swg not in all_events[e.name]:
                all_events[e.name][swg] = []
            all_events[e.name][swg].append([[p.x, p.y] for p in e.pointpath])


names = all_events.keys()
names.sort()
output_wrapper['stims'] = names
output_wrapper['viewers'] = viewers
output_wrapper['viewer_directory'] = viewer_directory;
output_wrapper['viewer_groups'] = viewer_groups
output_wrapper['stim_images'] = stim_images
output_wrapper['viewdata'] = all_events
output_wrapper['samples_per_second'] = 60


with open("js_data/pointdata_cleantest.js", "w") as f:
    f.write("EyeData = ")
    f.write(json.dumps(output_wrapper, f, indent=2))
#