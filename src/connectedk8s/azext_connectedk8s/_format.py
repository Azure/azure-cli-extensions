from jmespath import compile as compile_jmes, Options
from collections import OrderedDict


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