# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=broad-except

import os
import re
import json
from subprocess import check_output

DEFAULT_TARGET_INDEX_URL = os.getenv('AZURE_EXTENSION_TARGET_INDEX_URL')
STORAGE_ACCOUNT_KEY = os.getenv('AZURE_EXTENSION_TARGET_STORAGE_ACCOUNT_KEY')
STORAGE_ACCOUNT = os.getenv('AZURE_EXTENSION_TARGET_STORAGE_ACCOUNT')
STORAGE_CONTAINER = os.getenv('AZURE_EXTENSION_TARGET_STORAGE_CONTAINER')

def _get_updated_extension_names():
    cmd = 'git --no-pager diff --diff-filter=ACMRT HEAD~1 -- src/index.json'
    updated_content = check_output(cmd.split()).decode('utf-8')
    updated_urls = [line.replace('+', '') for line in updated_content.splitlines() if line.startswith('+') and not line.startswith('+++') and 'downloadUrl' in line]
    updated_exts = []
    NAME_REGEX = r'.*/([^/]*)-\d+.\d+.\d+'
    if not updated_urls:
        return updated_exts
    for line in updated_urls:
        search_result = re.search(r'"downloadUrl":\s+"(.*?)"', line)
        if search_result is not None:
            url = search_result.group(1)
            extension_name = re.findall(NAME_REGEX, url)[0].replace('_', '-')
            updated_exts.append(extension_name)
    return updated_exts

def _download_file(url):
    import requests
    count = 3
    the_ex = None
    while count > 0:
        try:
            response = requests.get(url, allow_redirects=True)
            break
        except Exception as ex:
            the_ex = ex
            count -= 1
    if count == 0:
        raise Exception("Request for {} failed: {}".format(url, str(the_ex)))
    return response


def _sync_wheel(ext, updated_indexes, client, overwrite, temp_dir):
    download_url = ext['downloadUrl']
    response = _download_file(download_url)
    whl_file = download_url.split('/')[-1]
    whl_path = os.path.join(temp_dir, whl_file)
    open(whl_path, 'wb').write(response.content)
    if not overwrite:
        exists = client.exists(container_name=STORAGE_CONTAINER, blob_name=whl_file)
        if exists:
            print("Skipping '{}' as it already exists...".format(whl_file))
            return
    client.create_blob_from_path(container_name=STORAGE_CONTAINER, blob_name=whl_file,
                                 file_path=os.path.abspath(whl_path))
    url = client.make_blob_url(container_name=STORAGE_CONTAINER, blob_name=whl_file)
    updated_index = ext
    updated_index['downloadUrl'] = url
    updated_indexes.append(updated_index)


def _update_target_extension_index(updated_indexes, target_index_path):
    import re

    NAME_REGEX = r'.*/([^/]*)-\d+.\d+.\d+'
    with open(target_index_path, 'r') as infile:
        curr_index = json.loads(infile.read())
    for entry in updated_indexes:
        url = entry['downloadUrl']
        extension_name = re.findall(NAME_REGEX, url)[0].replace('_', '-')
        if extension_name not in curr_index['extensions'].keys():
            print("Adding '{}' to index...".format(extension_name))
            curr_index['extensions'][extension_name] = [entry]
        else:
            print("Updating '{}' in index...".format(extension_name))
            if curr_index['extensions'][extension_name][-1]['filename'] == entry['filename']:  # in case of overwrite
                curr_index['extensions'][extension_name][-1] = entry
            else:
                curr_index['extensions'][extension_name].append(entry)

    with open(os.path.join(target_index_path), 'w') as outfile:
        outfile.write(json.dumps(curr_index, indent=4, sort_keys=True))


def main():
    import shutil
    import tempfile
    from azure.storage.blob import BlockBlobService

    updated_exts = _get_updated_extension_names()
    sync_all = (os.getenv('AZURE_SYNC_ALL_EXTENSIONS') and os.getenv('AZURE_SYNC_ALL_EXTENSIONS').lower() == 'true')
    if not sync_all and not updated_exts:
        print('index.json not changed. End task.')
        return
    temp_dir = tempfile.mkdtemp()
    with open('src/index.json', 'r') as fd:
        current_extensions = json.loads(fd.read()).get("extensions")

    target_index = DEFAULT_TARGET_INDEX_URL
    target_index_file = _download_file(target_index)
    os.mkdir(os.path.join(temp_dir, 'target'))
    target_index_path = os.path.join(temp_dir, 'target', 'index.json')
    open(target_index_path, 'wb').write(target_index_file.content)
    client = BlockBlobService(account_name=STORAGE_ACCOUNT, account_key=STORAGE_ACCOUNT_KEY)
    updated_indexes = []
    if sync_all:
        print('Syncing all extensions...\n')
        updated_exts = current_extensions.keys()
        # backup the old index.json
        client.create_blob_from_path(container_name=STORAGE_CONTAINER, blob_name='index.json.sav',
                                     file_path=os.path.abspath(target_index_path))
        inital_index = \
"""{
"extensions": {
},
"formatVersion": "1"
}"""
        open(target_index_path, 'w').write(inital_index)

    for extension_name in updated_exts:
        print('Uploading {}'.format(extension_name))
        if sync_all:
            for ext in current_extensions[extension_name]:
                _sync_wheel(ext, updated_indexes, client, True, temp_dir)
        else:
            ext = current_extensions[extension_name][-1]
            _sync_wheel(ext, updated_indexes, client, True, temp_dir)

    _update_target_extension_index(updated_indexes, target_index_path)
    client.create_blob_from_path(container_name=STORAGE_CONTAINER, blob_name='index.json',
                                 file_path=os.path.abspath(target_index_path))
    print("\nSync finished, extensions available in:")
    for updated_index in updated_indexes:
        print(updated_index['downloadUrl'])
    shutil.rmtree(temp_dir)


if __name__ == '__main__':
    main()
