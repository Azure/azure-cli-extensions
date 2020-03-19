import os
import re
import json
from subprocess import check_output, check_call
from pkg_resources import parse_version

DEFAULT_TARGET_INDEX_URL = "https://extmigrate.blob.core.windows.net/extensions/index.json"

def _get_updated_extension_names():
    cmd = 'git --no-pager diff --diff-filter=ACMRT HEAD~1 -- src/index.json'
    changed_content = check_output(cmd.split()).decode('utf-8')
    changed_lines = [line.replace('+', '') for line in changed_content.splitlines() if line.startswith('+') and not line.startswith('+++')]
    changed_lines = '\n'.join(changed_lines)
    updated_exts = []
    NAME_REGEX = r'.*/([^/]*)-\d+.\d+.\d+'
    if not changed_lines:
        return updated_exts
    search_result = re.search(r'"downloadUrl":\s+"(.*?)"', changed_lines)
    if search_result is not None:
        url = search_result.group(1)
        try:
            extension_name = re.findall(NAME_REGEX, url)[0]
            extension_name = extension_name.replace('_', '-')
        except IndexError:
            raise CLIError('unable to parse extension name')
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
        raise CLIError("Request for {} failed: {}".format(url, str(the_ex)))
    return response


def main():
    import re
    import json
    import os
    import shutil
    import tempfile
    from azure.storage.blob import BlockBlobService
    storage_account_key = os.getenv('AZURE_SYNC_STORAGE_ACCOUNT_KEY')
    storage_account = 'extmigrate'
    storage_container = 'extensions'

    updated_exts = _get_updated_extension_names()
    migrate_all = (os.getenv('AZURE_SYNC_ALL_EXTENSIONS') and os.getenv('AZURE_SYNC_ALL_EXTENSIONS').lower() == 'true')

    if not migrate_all and not updated_exts:
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

    client = BlockBlobService(account_name=storage_account, account_key=storage_account_key)
    
    updated_indexes = []
    if migrate_all:
        print('Syncing all extensions...\n')
        updated_exts = current_extensions.keys()
        # backup the old index.json
        client.create_blob_from_path(container_name=storage_container, blob_name='index.json.sav',
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
        if migrate_all:
            for ext in current_extensions[extension_name]:
                _migrate_wheel(ext, updated_indexes, client, True, storage_container, temp_dir)
        else:
            ext = current_extensions[extension_name][-1]
            _migrate_wheel(ext, updated_indexes, client, True, storage_container, temp_dir)

    update_target_extension_index(updated_indexes, target_index_path)
    client.create_blob_from_path(container_name=storage_container, blob_name='index.json',
                                    file_path=os.path.abspath(target_index_path))
    print("\nSync finished, extensions available in:")
    for updated_index in updated_indexes:
        print(updated_index['downloadUrl'])

    shutil.rmtree(temp_dir)


def _migrate_wheel(ext, updated_indexes, client, overwrite, storage_container, temp_dir):
    download_url = ext['downloadUrl']
    response = _download_file(download_url)
    whl_file = download_url.split('/')[-1]
    whl_path = os.path.join(temp_dir, whl_file)
    open(whl_path, 'wb').write(response.content)

    if not overwrite:
        exists = client.exists(container_name=storage_container, blob_name=whl_file)
        if exists:
            print("Skipping '{}' as it already exists...".format(whl_file))
            return
    # upload the WHL file
    client.create_blob_from_path(container_name=storage_container, blob_name=whl_file,
                                 file_path=os.path.abspath(whl_path))
    url = client.make_blob_url(container_name=storage_container, blob_name=whl_file)

    updated_index = ext
    updated_index['downloadUrl'] = url
    updated_indexes.append(updated_index)


def update_target_extension_index(updated_indexes, target_index_path):
    import re

    NAME_REGEX = r'.*/([^/]*)-\d+.\d+.\d+'
    with open(target_index_path, 'r') as infile:
        curr_index = json.loads(infile.read())
    for entry in updated_indexes:
        # Get the URL
        url = entry['downloadUrl']
        # Extract the extension name
        try:
            extension_name = re.findall(NAME_REGEX, url)[0]
            extension_name = extension_name.replace('_', '-')
        except IndexError:
            raise CLIError('unable to parse extension name')

        if extension_name not in curr_index['extensions'].keys():
            print("Adding '{}' to index...".format(extension_name))
            curr_index['extensions'][extension_name] = [entry]
        else:
            print("Updating '{}' in index...".format(extension_name))
            if curr_index['extensions'][extension_name][-1]['filename'] == entry['filename']: # in case of overwrite
                curr_index['extensions'][extension_name][-1] = entry
            else:
                curr_index['extensions'][extension_name].append(entry)

    # update index and write back to file
    with open(os.path.join(target_index_path), 'w') as outfile:
        outfile.write(json.dumps(curr_index, indent=4, sort_keys=True))


if __name__ == '__main__':
    main()
