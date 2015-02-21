#!/usr/bin/env python3
#
# Author: Kyle Manna <kyle [at] kylemana [dot] com >
#

import os
import sys
import glob
import json
import subprocess
import xml.etree.ElementTree as ET

base=sys.argv[1]

manifest = ET.parse(os.path.join(base, '.repo', 'manifest.xml'))
root = manifest.getroot()

overlays=glob.glob("{}/*".format(os.path.join(base, '.repo', 'local_manifests')))

for f in overlays:
    overlay = ET.parse(f)
    for element in overlay.getroot():

        if element.tag == 'remote':
            #print("Appending remote {}".format(element.get('name')))
            root.insert(0, element)

        elif element.tag == 'remove-project':
            name = element.get('name')
           
            for e in manifest.findall("project/[@name='{}']".format(name)):
                #print("Pruning {}".format(e.get('name')))
                root.remove(e)

        elif element.tag == 'project':
            name = element.get('name')
            #print("Copying project", name)
            root.append(element)

        else:
            print("unhandled tag", element.tag)

manifest.write('output.xml', encoding="utf-8", xml_declaration=True)
