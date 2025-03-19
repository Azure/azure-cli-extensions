#!/usr/bin/env python

# Copyright 2018 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import argparse
import datetime
import difflib
import glob
import os
import re
import sys

# list all the files contain a shebang line and should be ignored by this
# script
SKIP_FILES = ['hack/boilerplate/boilerplate.py']

parser = argparse.ArgumentParser()
parser.add_argument(
    "filenames",
    help="list of files to check, all files if unspecified",
    nargs='*')

rootdir = os.path.dirname(__file__) + "/../../"
rootdir = os.path.abspath(rootdir)
parser.add_argument(
    "--rootdir", default=rootdir, help="root directory to examine")

default_boilerplate_dir = os.path.join(rootdir, "hack/boilerplate")
parser.add_argument(
    "--boilerplate-dir", default=default_boilerplate_dir)

parser.add_argument(
    "-v", "--verbose",
    help="give verbose output regarding why a file does not pass",
    action="store_true")

args = parser.parse_args()

verbose_out = sys.stderr if args.verbose else open("/dev/null", "w")


def get_refs():
    refs = {}

    for path in glob.glob(os.path.join(
            args.boilerplate_dir, "boilerplate.*.txt")):
        extension = os.path.basename(path).split(".")[1]

        ref_file = open(path, 'r')
        ref = ref_file.read().splitlines()
        ref_file.close()
        refs[extension] = ref

    return refs


def file_passes(filename, refs, regexs):
    try:
        f = open(filename, 'r')
    except Exception as exc:
        print("Unable to open %s: %s" % (filename, exc), file=verbose_out)
        return False

    data = f.read()
    f.close()

    basename = os.path.basename(filename)
    extension = file_extension(filename)

    if extension != "":
        ref = refs[extension]
    else:
        ref = refs[basename]

    # remove extra content from the top of files
    if extension == "sh":
        p = regexs["shebang"]
        (data, found) = p.subn("", data, 1)

    data = data.splitlines()

    # if our test file is smaller than the reference it surely fails!
    if len(ref) > len(data):
        print('File %s smaller than reference (%d < %d)' %
              (filename, len(data), len(ref)),
              file=verbose_out)
        return False

    # trim our file to the same number of lines as the reference file
    data = data[:len(ref)]

    p = regexs["year"]
    for d in data:
        if p.search(d):
            print('File %s has the YEAR field, but missing the year of date' %
                  filename, file=verbose_out)
            return False

    # Replace all occurrences of regex "2014|2015|2016|2017|2018" with "YEAR"
    p = regexs["date"]
    for i, d in enumerate(data):
        (data[i], found) = p.subn('YEAR', d)
        if found != 0:
            break

    # if we don't match the reference at this point, fail
    if ref != data:
        print("Header in %s does not match reference, diff:" %
              filename, file=verbose_out)
        if args.verbose:
            print(file=verbose_out)
            for line in difflib.unified_diff(
                    ref, data, 'reference', filename, lineterm=''):
                print(line, file=verbose_out)
            print(file=verbose_out)
        return False

    return True


def file_extension(filename):
    return os.path.splitext(filename)[1].split(".")[-1].lower()


def normalize_files(files):
    newfiles = []
    for pathname in files:
        newfiles.append(pathname)
    for i, pathname in enumerate(newfiles):
        if not os.path.isabs(pathname):
            newfiles[i] = os.path.join(args.rootdir, pathname)

    return newfiles


def get_files(extensions):

    files = []
    if len(args.filenames) > 0:
        files = args.filenames
    else:
        for root, dirs, walkfiles in os.walk(args.rootdir):
            for name in walkfiles:
                pathname = os.path.join(root, name)
                files.append(pathname)

    files = normalize_files(files)
    outfiles = []
    for pathname in files:
        basename = os.path.basename(pathname)
        extension = file_extension(pathname)
        if extension in extensions or basename in extensions:
            outfiles.append(pathname)

    outfiles = list(set(outfiles) - set(normalize_files(SKIP_FILES)))
    return outfiles


def get_dates():
    years = datetime.datetime.now().year
    return '(%s)' % '|'.join((str(year) for year in range(2014, years+1)))


def get_regexs():
    regexs = {}
    # Search for "YEAR" which exists in the boilerplate,
    # but shouldn't in the real thing
    regexs["year"] = re.compile('YEAR')
    # get_dates return 2014, 2015, 2016, 2017, or 2018 until the current year
    # as a regex like: "(2014|2015|2016|2017|2018)";
    # company holder names can be anything
    regexs["date"] = re.compile(get_dates())
    # strip #!.* from shell scripts
    regexs["shebang"] = re.compile(r"^(#!.*\n)\n*", re.MULTILINE)
    return regexs


def main():
    regexs = get_regexs()
    refs = get_refs()
    filenames = get_files(refs.keys())

    for filename in filenames:
        if not file_passes(filename, refs, regexs):
            print(filename, file=sys.stdout)

    return 0


if __name__ == "__main__":
    sys.exit(main())
