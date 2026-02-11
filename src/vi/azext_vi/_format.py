# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict


def vi_extension_list_table_format(results):
    return [__get_extension_table_row(result) for result in results]


def vi_extension_show_table_format(result):
    return __get_extension_table_row(result)


def __get_extension_table_row(result):
    return OrderedDict([
        ('name', result.get('name', '')),
        ('extensionType', result.get('extensionType', '')),
        ('version', result.get('version', '')),
        ('provisioningState', result.get('provisioningState', '')),
        ('lastModifiedAt', result.get('systemData', {}).get('lastModifiedAt', '')),
    ])


def vi_camera_list_table_format(results):
    return [__get_camera_table_row(result) for result in results]


def __get_camera_table_row(result):
    return OrderedDict([
        ('name', result.get('name', '')),
        ('status', result.get('status', '')),
        ('rtspUrl', result.get('rtspUrl', '')),
        ('liveStreamingEnabled', result.get('liveStreamingEnabled', '')),
        ('recordingEnabled', result.get('recordingEnabled', '')),
    ])
