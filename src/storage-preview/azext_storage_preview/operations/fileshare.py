# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.log import get_logger

logger = get_logger(__name__)


def _get_client(client, kwargs):
    directory_path = kwargs.pop("directory_name", None)
    if directory_path and directory_path.startswith('./'):
        directory_path = directory_path.replace('./', '', 1)
    dir_client = client.get_directory_client(directory_path=directory_path)
    file_name = kwargs.pop("file_name", None)
    if file_name:
        total_path = directory_path + '/' + file_name if directory_path else file_name
        dir_client = client.get_directory_client(directory_path=total_path)
        exists = False
        from azure.core.exceptions import ClientAuthenticationError
        try:
            exists = dir_client.exists()
        except ClientAuthenticationError:
            exists = False
        if not exists:
            dir_client = client.get_directory_client(directory_path=directory_path)
            client = dir_client.get_file_client(file_name=file_name)
            if "recursive" in kwargs:
                kwargs.pop("recursive")
        else:
            client = dir_client
    else:
        client = dir_client
    return client


def list_handle(client, marker, num_results, **kwargs):
    from ..track2_util import list_generator
    client = _get_client(client, kwargs)

    generator = client.list_handles(results_per_page=num_results, **kwargs)
    pages = generator.by_page(continuation_token=marker)  # SharePropertiesPaged
    result = list_generator(pages=pages, num_results=num_results)

    return {"items": result, "nextMarker": pages.continuation_token}


def close_handle(client, **kwargs):
    client = _get_client(client, kwargs)

    handle = kwargs.pop("handle", None)
    if kwargs.pop("close_all", None) or handle == '*':
        return client.close_all_handles(**kwargs)
    return client.close_handle(handle=handle, **kwargs)
