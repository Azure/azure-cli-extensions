# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict
from jmespath import compile as compile_jmes, Options  # pylint: disable=import-error


def connectedk8s_show_table_format(result):
    """Format a connected cluster as summary results for display with "-o table"."""
    return [_connectedk8s_table_format(result)]


def connectedk8s_list_table_format(results):
    """Format an connected cluster list for display with "-o table"."""
    return [_connectedk8s_list_table_format(r) for r in results]


def _connectedk8s_table_format(result):
    parsed = compile_jmes("""{
        name: name,
        location: location,
        resourceGroup: resourceGroup
    }""")
    # use ordered dicts so headers are predictable
    return parsed.search(result, Options(dict_cls=OrderedDict))


def _connectedk8s_list_table_format(result):
    parsed = compile_jmes("""{
        name: name,
        location: location,
        resourceGroup: resourceGroup
    }""")
    # use ordered dicts so headers are predictable
    return parsed.search(result, Options(dict_cls=OrderedDict))
