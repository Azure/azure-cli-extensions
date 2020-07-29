# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import filecmp
import os
from azure.storage.blob import BlockBlobService
from sync_extensions import _download_file

STORAGE_ACCOUNT_KEY = os.getenv('AZURE_EXTENSION_CMD_INDEX_STORAGE_ACCOUNT_KEY')
STORAGE_ACCOUNT = os.getenv('AZURE_EXTENSION_CMD_INDEX_STORAGE_ACCOUNT')
STORAGE_CONTAINER = os.getenv('AZURE_EXTENSION_CMD_INDEX_STORAGE_CONTAINER')


def main():
    file_name = 'extCmdIndexToUpload.json'
    file_path = os.path.expanduser(os.path.join('~', '.azure', file_name))

    client = BlockBlobService(account_name=STORAGE_ACCOUNT, account_key=STORAGE_ACCOUNT_KEY)
    client.create_blob_from_path(container_name=STORAGE_CONTAINER, blob_name='extCmdIndex.json',
                                 file_path=file_path)

    url = client.make_blob_url(container_name=STORAGE_CONTAINER, blob_name='extCmdIndex.json')

    download_file_path = os.path.expanduser(os.path.join('~', '.azure', 'extCmdIndexDownloaded.json'))
    _download_file(url, download_file_path)
    if filecmp.cmp(file_path, download_file_path):
        print("extCmdIndex.json uploaded successfully. URL: {}".format(url))
    else:
        raise Exception("Failed to update extCmdIndex.json in storage account")


if __name__ == '__main__':
    main()
