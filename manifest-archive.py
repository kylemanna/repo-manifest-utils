#!/usr/bin/env python3
#
# Author: Kyle Manna <kyle [at] kylemana [dot] com >
#
# Example invocation:
# ./manifest-archive.py -u https://android.googlesource.com/platform/manifest -b android-1.6_r1

import os
import sys
import shutil
import logging
import tarfile
import tempfile
import subprocess
import argparse
from time import gmtime, strftime

#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument("-b", "--manifest-branch", help="manifest branch or revision")
parser.add_argument("-u", "--manifest-url", help="manifest repository location")
parser.add_argument("-j", "--jobs", help="projects to fetch simultaneously")
parser.add_argument("-o", "--output", help="tarball output")

args = parser.parse_args()

name = args.manifest_branch
origdir = os.getcwd()

# Set TMPDIR to change the base
temp = tempfile.TemporaryDirectory()

# Check that temp directory isn't on a small tmpfs
temp_free_gb = shutil.disk_usage(temp.name)[2] / (2**30)
logging.debug('Free diskspace @ {}: {:.4} GB'.format(temp.name, temp_free_gb))

if temp_free_gb < 10:
    print('Insufficent free diskspace @ {}: {:.4} GB'.format(
        temp.name, temp_free_gb), file=sys.stderr)
    print('Set the env TMPDIR variable to move temp directory')
    sys.exit(1)

base = os.path.join(temp.name, name)
os.mkdir(base)
os.chdir(base)

if args.output:
    output = os.path.join(origdir, args.output)
else:
    output = os.path.join(origdir, "{}_{}.tar.xz".format(name, strftime("%Y%m%d")))

# Build repo command
cmd = ['repo', 'init']

if args.manifest_branch:
    cmd.extend(['--manifest-branch', args.manifest_branch])

if args.manifest_url:
    cmd.extend(['--manifest-url', args.manifest_url])

# Run repo init
logging.info("Running: {}".format(str(cmd)))
ret = subprocess.call(cmd)

# Run repo sync
cmd_sync = ['repo', 'sync']

if args.jobs:
    cmd_sync.extend(['--jobs', args.jobs])

logging.info("Running: {}".format(str(cmd_sync)))
ret = subprocess.call(cmd_sync)

logging.info("Creating tarball @ {}".format(output))
os.chdir(temp.name)
ext = os.path.splitext(output)[1][1:]

if shutil.which('pxz') and ext == 'xz':
    logging.debug("Using pxz for compression")
    # Hand it over to cmd line tools since multiple pipes in python is painful
    # and leverage pxz for best performance
    cmd_tar = 'tar cf - {} | pxz > {}'.format(name, output)
    subprocess.call(cmd_tar, shell=True)
else:
    # Failsafe tarball + compression (slow!)
    with tarfile.open(output, 'w:{}'.format(ext)) as tar:
        tar.add(name)
