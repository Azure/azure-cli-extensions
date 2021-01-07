# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def string_to_bytearray(data):
    from msrest.serialization import Deserializer
    if isinstance(data, str):
        return Deserializer.deserialize_bytearray(data)

    return data


def make_file_url(client, directory_name, file_name, sas_token=None):

    if not directory_name:
        url = '{}/{}'.format(client.primary_endpoint, file_name)
    else:
        url = '{}/{}/{}'.format(client.primary_endpoint, directory_name, file_name)

    if sas_token:
        url += '?' + sas_token

    return url
