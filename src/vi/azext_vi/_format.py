# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict


def camera_list_table_format(results):
    return [__get_table_row(result) for result in results]


def __get_table_row(result):
    return OrderedDict([
        ('name', result['name']),
        ('status', result.get('status', '')),
        ('rtspUrl', result.get('rtspUrl', '')),
        ('liveEnabled', result.get('liveStreamingEnabled', '')),
        ('recordingEnabled', result.get('recordingEnabled', '')),
    ])
