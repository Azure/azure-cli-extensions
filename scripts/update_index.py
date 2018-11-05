# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import hashlib
import json
import re
import subprocess
import sys
import urllib2

NAME_REGEX = r'.*/([^/]*)-\d+.\d+.\d+'

def main():

    # TODO: This should be the download URL realistically
    whl_path = None
    try:
        whl_path = sys.argv[1]
    except IndexError:
        pass
    if not whl_path or not whl_path.endswith('.whl') or not whl_path.startswith('https:'):
        raise ValueError('incorrect usage: update_script <URL TO WHL FILE>')

    try:
        extension_name = re.findall(NAME_REGEX, whl_path)[0]
        extension_name = extension_name.replace('_', '-')
    except IndexError:
        raise ValueError('unable to parse extension name')

    # Download WHL file and compute hash
    whl_file = urllib2.urlopen(whl_path)
    sha256 = hashlib.sha256()
    for chunk in iter(lambda: whl_file.read(4096), b""):
        sha256.update(chunk)
    sha256_digest = sha256.hexdigest()

    with open('./src/index.json', 'r') as infile:
        curr_index = json.loads(infile.read())

    try:
        entry = curr_index['extensions'][extension_name]
    except IndexError:
        raise ValueError('{} not found in index.json'.format(extension_name))

    entry[0]['downloadUrl'] = whl_path
    entry[0]['sha256Digest'] = sha256_digest
    entry[0]['filename'] = whl_path.split('/')[-1]

    curr_index['extensions'][extension_name] = entry

    with open('./src/index.json', 'w') as outfile:
        outfile.write(json.dumps(curr_index, indent=4, sort_keys=True))

if __name__ == '__main__':
    main()
