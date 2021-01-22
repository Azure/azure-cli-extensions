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
COMMIT_NUM = os.getenv('AZURE_EXTENSION_COMMIT_NUM') or 1


def _get_updated_extension_filenames():
    cmd = 'git --no-pager diff --diff-filter=ACMRT HEAD~{} -- src/index.json'.format(COMMIT_NUM)
    updated_content = check_output(cmd.split()).decode('utf-8')
    FILENAME_REGEX = r'"filename":\s+"(.*?)"'
    added_ext_filenames = [re.findall(FILENAME_REGEX, line)[0] for line in updated_content.splitlines() if line.startswith('+') and not line.startswith('+++') and 'filename' in line]
    deleted_ext_filenames = [re.findall(FILENAME_REGEX, line)[0] for line in updated_content.splitlines() if line.startswith('-') and not line.startswith('---') and 'filename' in line]
    return added_ext_filenames, deleted_ext_filenames


def download_file(url, file_path):
    import requests
    count = 3
    the_ex = None
    while count > 0:
        try:
            response = requests.get(url, stream=True, allow_redirects=True)
            assert response.status_code == 200, "Response code {}".format(response.status_code)
            break
        except Exception as ex:
            the_ex = ex
            count -= 1
    if count == 0:
        msg = "Request for {} failed: {}".format(url, str(the_ex))
        print(msg)
        raise Exception(msg)

    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:  # ignore keep-alive new chunks
                f.write(chunk)


def _sync_wheel(ext, updated_indexes, failed_urls, client, overwrite, temp_dir):
    download_url = ext['downloadUrl']
    whl_file = download_url.split('/')[-1]
    whl_path = os.path.join(temp_dir, whl_file)
    try:
        download_file(download_url, whl_path)
    except Exception:
        failed_urls.append(download_url)
        return
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


def _update_target_extension_index(updated_indexes, deleted_ext_filenames, target_index_path):
    NAME_REGEX = r'^(.*?)-\d+.\d+.\d+'
    with open(target_index_path, 'r') as infile:
        curr_index = json.loads(infile.read())
    for entry in updated_indexes:
        filename = entry['filename']
        extension_name = re.findall(NAME_REGEX, filename)[0].replace('_', '-')
        if extension_name not in curr_index['extensions'].keys():
            print("Adding '{}' to index...".format(filename))
            curr_index['extensions'][extension_name] = [entry]
        else:
            print("Updating '{}' in index...".format(filename))
            curr_entry = next((ext for ext in curr_index['extensions'][extension_name] if ext['filename'] == entry['filename']), None)
            if curr_entry is not None:  # in case of overwrite
                curr_entry = entry
            else:
                curr_index['extensions'][extension_name].append(entry)
    for filename in deleted_ext_filenames:
        extension_name = re.findall(NAME_REGEX, filename)[0].replace('_', '-')
        print("Deleting '{}' in index...".format(filename))
        curr_index['extensions'][extension_name] = [ext for ext in curr_index['extensions'][extension_name] if ext['filename'] != filename]
        if not curr_index['extensions'][extension_name]:
            del curr_index['extensions'][extension_name]

    with open(os.path.join(target_index_path), 'w') as outfile:
        outfile.write(json.dumps(curr_index, indent=4, sort_keys=True))


def main():
    import shutil
    import tempfile
    from azure.storage.blob import BlockBlobService

    added_ext_filenames = []
    deleted_ext_filenames = []
    sync_all = (os.getenv('AZURE_SYNC_ALL_EXTENSIONS') and os.getenv('AZURE_SYNC_ALL_EXTENSIONS').lower() == 'true')
    if not sync_all:
        added_ext_filenames, deleted_ext_filenames = _get_updated_extension_filenames()
        if not added_ext_filenames and not deleted_ext_filenames:
            print('index.json not changed. End task.')
            return
    temp_dir = tempfile.mkdtemp()
    with open('src/index.json', 'r') as fd:
        current_extensions = json.loads(fd.read()).get("extensions")

    target_index = DEFAULT_TARGET_INDEX_URL
    os.mkdir(os.path.join(temp_dir, 'target'))
    target_index_path = os.path.join(temp_dir, 'target', 'index.json')
    download_file(target_index, target_index_path)

    client = BlockBlobService(account_name=STORAGE_ACCOUNT, account_key=STORAGE_ACCOUNT_KEY)
    updated_indexes = []
    failed_urls = []
    if sync_all:
        print('Syncing all extensions...\n')
        # backup the old index.json
        client.create_blob_from_path(container_name=STORAGE_CONTAINER, blob_name='index.json.sav',
                                     file_path=os.path.abspath(target_index_path))
        inital_index = {"extensions": {}, "formatVersion": "1"}
        open(target_index_path, 'w').write(json.dumps(inital_index, indent=4, sort_keys=True))
        for extension_name in current_extensions.keys():
            for ext in current_extensions[extension_name]:
                print('Uploading {}'.format(ext['filename']))
                _sync_wheel(ext, updated_indexes, failed_urls, client, True, temp_dir)
    else:
        NAME_REGEX = r'^(.*?)-\d+.\d+.\d+'
        for filename in added_ext_filenames:
            extension_name = re.findall(NAME_REGEX, filename)[0].replace('_', '-')
            print('Uploading {}'.format(filename))
            ext = current_extensions[extension_name][-1]
            if ext['filename'] != filename:
                ext = next((ext for ext in current_extensions[extension_name] if ext['filename'] == filename), None)
            if ext is not None:
                _sync_wheel(ext, updated_indexes, failed_urls, client, True, temp_dir)

    print("")
    _update_target_extension_index(updated_indexes, deleted_ext_filenames, target_index_path)
    client.create_blob_from_path(container_name=STORAGE_CONTAINER, blob_name='index.json',
                                 file_path=os.path.abspath(target_index_path))
    if updated_indexes:
        print("\nSync finished, extensions available in:")
    for updated_index in updated_indexes:
        print(updated_index['downloadUrl'])
    shutil.rmtree(temp_dir)

    if failed_urls:
        print("\nFailed to donwload and sync the following files. They are skipped:")
        for url in failed_urls:
            print(url)
        print("")
        raise Exception("Failed to sync some packages.")


if __name__ == '__main__':
    main()
