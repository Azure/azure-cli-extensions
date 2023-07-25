# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import base64


def string_to_bytes(data, encoding="utf-8"):
    if isinstance(data, str):
        return data.encode(encoding)
    return data


def make_file_url(client, directory_name, file_name, sas_token=None):

    if not directory_name:
        url = '{}/{}'.format(client.primary_endpoint, file_name)
    else:
        url = '{}/{}/{}'.format(client.primary_endpoint, directory_name, file_name)

    if sas_token:
        url += '?' + sas_token

    return url


def list_generator(pages, num_results):
    result = []

    # get first page items
    page = list(next(pages))
    result += page

    while True:
        if not pages.continuation_token:
            break

        # handle num results
        if num_results is not None:
            if num_results == len(result):
                if pages.continuation_token:
                    next_marker = {"nextMarker": pages.continuation_token}
                    result.append(next_marker)
                break

        page = list(next(pages))
        result += page

    return result


def _encode_bytes(b):
    if isinstance(b, (bytes, bytearray)):
        return base64.b64encode(b).decode('utf-8')
    return b


def _str_to_bytearray(data):
    if data is not None:
        return bytearray(base64.b64decode(data))
    return data
