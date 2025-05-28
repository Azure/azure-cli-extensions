# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict
# pylint: disable=import-error
from jmespath import compile as compile_jmes, Options


def amc_node_status_table_format(result):
    """Format a managed cluster as summary results for display with "-o table"."""
    return [_amc_node_status_table_format(r) for r in result['nodes']]


def _amc_node_status_table_format(result):
    result['tokensDisplay'] = 'N/A'
    if result['tokens'] is not None and result['tokens']:
        result['tokensDisplay'] = result['tokens'][0] + ",..."
    parsed = compile_jmes("""{
        Datacenter:datacenter,
        Status:status,
        State:state,
        Address:address,
        Rack:rack,
        Tokens:tokensDisplay,
        HostId: hostId,
        Load:load,
        Owns:owns
    }""")
    # use ordered dicts so headers are predictable
    return parsed.search(result, Options(dict_cls=OrderedDict))
