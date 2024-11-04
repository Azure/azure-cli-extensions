# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import hashlib
import json
import re
import sys
import tempfile

from util import get_ext_metadata, get_whl_from_url

NAME_REGEX = r'.*/([^/]*)-\d+.\d+.\d+'


def get_sha256sum(a_file):
    sha256 = hashlib.sha256()
    with open(a_file, 'rb') as f:
        sha256.update(f.read())
    return sha256.hexdigest()


def main():

    # Get extension WHL from URL
    whl_path = None
    try:
        whl_path = sys.argv[1]
    except IndexError:
        pass
    if not whl_path or not whl_path.endswith('.whl') or not whl_path.startswith('https:'):
        raise ValueError('incorrect usage: update_script <URL TO WHL FILE>')

    # Extract the extension name
    try:
        extension_name = re.findall(NAME_REGEX, whl_path)[0]
        extension_name = extension_name.replace('_', '-')
    except IndexError:
        raise ValueError('unable to parse extension name')

    extensions_dir = tempfile.mkdtemp()
    ext_dir = tempfile.mkdtemp(dir=extensions_dir)
    whl_cache_dir = tempfile.mkdtemp()
    whl_cache = {}
    ext_file = get_whl_from_url(whl_path, extension_name, whl_cache_dir, whl_cache)

    with open('./src/index.json', 'r') as infile:
        curr_index = json.loads(infile.read())

    try:
        entry = curr_index['extensions'][extension_name]
    except IndexError:
        raise ValueError('{} not found in index.json'.format(extension_name))

    entry[0]['downloadUrl'] = whl_path
    entry[0]['sha256Digest'] = get_sha256sum(ext_file)
    entry[0]['filename'] = whl_path.split('/')[-1]
    entry[0]['metadata'] = get_ext_metadata(ext_dir, ext_file, extension_name)

    # update index and write back to file
    curr_index['extensions'][extension_name] = entry
    with open('./src/index.json', 'w') as outfile:
        outfile.write(json.dumps(curr_index, indent=4, sort_keys=True))


if __name__ == '__main__':
    main()
