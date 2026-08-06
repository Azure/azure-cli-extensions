# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict
from jmespath import compile as compile_jmes, Options


def appnet_list_versions_table_format(results):
    """Format appnet list-versions results for display with "-o table"."""
    formatted_results = []
    for result in results:
        # Extract the main info
        base_info = {
            'kubernetesVersion': result.get('properties', {}).get('kubernetesVersion', 'N/A'),
        }

        # Get fully managed versions
        fully_managed = result.get('properties', {}).get('fullyManagedVersions', {})
        if fully_managed and fully_managed.get('releaseChannels'):
            for channel in fully_managed['releaseChannels']:
                formatted_results.append({
                    'kubernetesVersion': base_info['kubernetesVersion'],
                    'mode': 'FullyManaged',
                    'releaseChannel': channel.get('releaseChannel', 'N/A'),
                    'version': channel.get('version', 'N/A'),
                })

        # Get self managed versions
        self_managed = result.get('properties', {}).get('selfManagedVersions', {})
        if self_managed and self_managed.get('versions'):
            for version_info in self_managed['versions']:
                upgrades_str = ', '.join(version_info.get('upgrades', []))
                formatted_results.append({
                    'kubernetesVersion': base_info['kubernetesVersion'],
                    'mode': 'SelfManaged',
                    'releaseChannel': 'N/A',
                    'version': version_info.get('version', 'N/A'),
                    'availableUpgrades': upgrades_str if upgrades_str else 'None',
                })

    return formatted_results


def appnet_member_list_table_format(results):
    """Format appnet member list results for display with "-o table"."""
    return [_appnet_member_show_table_format(r) for r in results]


def _appnet_member_show_table_format(result):
    """Format a single appnet member as summary results for display with "-o table"."""
    # Extract resource group from ID
    resource_id = result.get('id', '')
    resource_group = 'N/A'
    if resource_id:
        parts = resource_id.split('/resourceGroups/')
        if len(parts) > 1:
            resource_group = parts[1].split('/')[0]

    parsed = compile_jmes("""{
        name: name,
        location: location,
        clusterType: properties.clusterType,
        mode: properties.mode,
        provisioningState: properties.provisioningState,
        clusterResourceId: properties.metadata.resourceId
    }""")

    result_dict = parsed.search(result, Options(dict_cls=OrderedDict))
    result_dict['resourceGroup'] = resource_group

    # Shorten cluster resource ID for readability
    if result_dict.get('clusterResourceId'):
        result_dict['clusterName'] = result_dict['clusterResourceId'].split('/')[-1]
        del result_dict['clusterResourceId']

    return result_dict


def appnet_member_upgrade_history_table_format(results):
    """Format appnet member upgrade history results for display with "-o table"."""
    formatted_results = []
    for result in results:
        parsed = compile_jmes("""{
            name: name,
            upgradeState: properties.upgradeState,
            fromVersion: properties.fromVersion,
            toVersion: properties.toVersion,
            startTime: properties.startTime,
            endTime: properties.endTime,
            upgradeType: properties.upgradeType
        }""")
        formatted_results.append(parsed.search(result, Options(dict_cls=OrderedDict)))

    return formatted_results
