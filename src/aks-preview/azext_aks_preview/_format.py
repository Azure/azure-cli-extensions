# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict


def aks_agentpool_show_table_format(result):
    """Format an agent pool as summary results for display with "-o table"."""
    return [_aks_agentpool_table_format(result)]


def _aks_agentpool_table_format(result):
    # pylint: disable=import-error
    from jmespath import compile as compile_jmes, Options

    parsed = compile_jmes("""{
        name: name,
        location: location,
        resourceGroup: resourceGroup,
        kubernetesVersion: kubernetesVersion,
        provisioningState: provisioningState,
        count: count
    }""")
    # use ordered dicts so headers are predictable
    return parsed.search(result, Options(dict_cls=OrderedDict))


def aks_list_table_format(results):
    """"Format a list of managed clusters as summary results for display with "-o table"."""
    return [_aks_table_format(r) for r in results]


def aks_show_table_format(result):
    """Format a managed cluster as summary results for display with "-o table"."""
    return [_aks_table_format(result)]


def _aks_table_format(result):
    # pylint: disable=import-error
    from jmespath import compile as compile_jmes, Options

    parsed = compile_jmes("""{
        name: name,
        location: location,
        resourceGroup: resourceGroup,
        kubernetesVersion: kubernetesVersion,
        provisioningState: provisioningState,
        fqdn: fqdn
    }""")
    # use ordered dicts so headers are predictable
    return parsed.search(result, Options(dict_cls=OrderedDict))


def aks_upgrades_table_format(result):
    """Format get-upgrades results as a summary for display with "-o table"."""
    # pylint: disable=import-error
    from jmespath import compile as compile_jmes, Options

    preview = []
    for i, j in result.items():
        if i == "controlPlaneProfile":
            # the reason why we choose "upgrades" obejct, since only it has the isPreview boolean.
            for item in j["upgrades"]:
                if item["isPreview"]:
                    preview.append(item["kubernetesVersion"])
    # This expression assumes there is one node pool, and that the master and nodes upgrade in lockstep.
    parsed = compile_jmes("""{
        name: name,
        resourceGroup: resourceGroup,
        masterVersion: controlPlaneProfile.kubernetesVersion || `unknown` | set_preview(@),
        nodePoolVersion: agentPoolProfiles[0].kubernetesVersion || `unknown` | set_preview(@),
        upgrades: controlPlaneProfile.upgrades[].kubernetesVersion || [`None available`] | sort_versions(@) | set_preview_array(@) | join(`, `, @)
    }""")
    # use ordered dicts so headers are predictable
    return parsed.search(result, Options(dict_cls=OrderedDict, custom_functions=_custom_functions(preview)))


def aks_versions_table_format(result):
    """Format get-versions results as a summary for display with "-o table"."""
    # pylint: disable=import-error
    from jmespath import compile as compile_jmes, Options

    # get preview orchestrator version
    preview = []
    for key, value in result.items():
        if key == "orchestrators":
            for i in value:
                if i["isPreview"]:
                    preview.append(i["orchestratorVersion"])

    parsed = compile_jmes("""orchestrators[].{
        kubernetesVersion: orchestratorVersion | set_preview(@),
        upgrades: upgrades[].orchestratorVersion || [`None available`] | sort_versions(@) | set_preview_array(@) | join(`, `, @)
    }""")
    # use ordered dicts so headers are predictable
    results = parsed.search(result, Options(dict_cls=OrderedDict, custom_functions=_custom_functions(preview)))
    return sorted(results, key=lambda x: version_to_tuple(x.get('kubernetesVersion')), reverse=True)


def version_to_tuple(v):
    """Quick-and-dirty sort function to handle simple semantic versions like 1.7.12 or 1.8.7."""
    if v.endswith('(preview)'):
        return tuple(map(int, (v[:-9].split('.'))))
    return tuple(map(int, (v.split('.'))))


def _custom_functions(preview_versions):
    # pylint: disable=import-error
    from jmespath import functions

    class CustomFunctions(functions.Functions):  # pylint: disable=too-few-public-methods

        @functions.signature({'types': ['array']})
        def _func_sort_versions(self, s):  # pylint: disable=no-self-use
            """Custom JMESPath `sort_versions` function that sorts an array of strings as software versions."""
            try:
                return sorted(s, key=version_to_tuple)
            except (TypeError, ValueError):  # if it wasn't sortable, return the input so the pipeline continues
                return s

        @functions.signature({'types': ['array']})
        def _func_set_preview_array(self, s):  # pylint: disable=no-self-use
            """Custom JMESPath `set_preview_array` function that suffixes preview version"""
            try:
                res = []
                for version in s:
                    preview = False
                    for i in preview_versions:
                        if version == i:
                            res.append(version + "(preview)")
                            preview = True
                            break
                    if not preview:
                        res.append(version)
                return res
            except(TypeError, ValueError):
                return s

        @functions.signature({'types': ['string']})
        def _func_set_preview(self, s):  # pylint: disable=no-self-use
            """Custom JMESPath `set_preview` function that suffixes preview version"""
            try:
                for i in preview_versions:
                    if s == i:
                        return s + "(preview)"
                return s
            except(TypeError, ValueError):
                return s

    return CustomFunctions()
