# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict
# pylint: disable=import-error
from jmespath import compile as compile_jmes, Options
# pylint: disable=import-error
from jmespath import functions


def aks_addon_list_available_table_format(result):
    def parser(entry):
        parsed = compile_jmes("""{
                name: name,
                description: description
            }""")
        return parsed.search(entry, Options(dict_cls=OrderedDict))
    return [parser(r) for r in result]


def aks_addon_list_table_format(result):
    def parser(entry):
        parsed = compile_jmes("""{
                name: name,
                enabled: enabled
            }""")
        return parsed.search(entry, Options(dict_cls=OrderedDict))
    return [parser(r) for r in result]


def aks_addon_show_table_format(result):
    def parser(entry):
        config = ""
        for k, v in entry["config"].items():
            config += k + "=" + v + ";"
        entry["config"] = config
        parsed = compile_jmes("""{
                name: name,
                api_key: api_key,
                config: config,
                identity: identity
            }""")
        return parsed.search(entry, Options(dict_cls=OrderedDict))
    return parser(result)


def aks_machine_list_table_format(results):
    return [aks_machine_show_table_format(r) for r in results]


def aks_machine_show_table_format(result):
    def parser(entry):
        ipv4_addresses = ""
        ipv6_addresses = ""
        for k in entry["properties"]["network"]["ipAddresses"]:
            if k["family"].lower() == "ipv4":
                ipv4_addresses += k["ip"] + ";"
            elif k["family"].lower() == "ipv6":
                ipv6_addresses += k["ip"] + ";"
        entry["ipv4"] = ipv4_addresses
        entry["ipv6"] = ipv6_addresses
        parsed = compile_jmes("""{
            name: name,
            zones: zones,
            ipv4: ipv4,
            ipv6: ipv6,
            nodeImageVersion: nodeImageVersion,
            provisioningState: provisioningState,
            orchestratorVersion: orchestratorVersion,
            currentOrchestratorVersion: currentOrchestratorVersion,
            vmSize: vmSize,
            priority: priority,
            mode: mode
        }""")
        return parsed.search(entry, Options(dict_cls=OrderedDict))
    return parser(result)


def aks_operation_show_table_format(result):
    def parser(entry):
        percentComplete = ""
        if entry["percentComplete"]:
            percentComplete = str(entry["percentComplete"]) + "%"
        entry["percentComplete"] = percentComplete
        parsed = compile_jmes("""{
                name: name,
                status: status,
                startTime: startTime,
                endTime: endTime,
                percentComplete: percentComplete
            }""")
        return parsed.search(entry, Options(dict_cls=OrderedDict))
    return parser(result)


def aks_namespace_list_table_format(results):
    """Format an managed namespace list for display with "-o table"."""
    return [_aks_namespace_list_table_format(r) for r in results]


def _aks_namespace_list_table_format(result):
    if not result.get("properties"):
        parsed = compile_jmes("""{
            name: name,
            resourceGroup: resourceGroup,
            location: location
        }""")
    else:
        parsed = compile_jmes("""{
            name: name,
            tags: to_string(tags),
            provisioningState: to_string(properties.provisioningState),
            labels: to_string(properties.labels),
            annotations: to_string(properties.annotations),
            cpuRequest: to_string(properties.defaultResourceQuota.cpuRequest),
            cpuLimit: to_string(properties.defaultResourceQuota.cpuLimit),
            memoryRequest: to_string(properties.defaultResourceQuota.memoryRequest),
            memoryLimit: to_string(properties.defaultResourceQuota.memoryLimit),
            ingress: to_string(properties.defaultNetworkPolicy.ingress),
            egress: to_string(properties.defaultNetworkPolicy.egress),
            adoptionPolicy: to_string(properties.adoptionPolicy),
            deletePolicy: to_string(properties.deletePolicy)
        }""")
    # use ordered dicts so headers are predictable
    return parsed.search(result, Options(dict_cls=OrderedDict))


def aks_agentpool_show_table_format(result):
    """Format an agent pool as summary results for display with "-o table"."""
    return [_aks_agentpool_table_format(result)]


def _aks_agentpool_table_format(result):
    parsed = compile_jmes("""{
        name: name,
        osType: osType,
        kubernetesVersion: kubernetesVersion,
        vmSize: vmSize,
        osDiskSizeGB: osDiskSizeGB,
        count: count,
        maxPods: maxPods,
        provisioningState: provisioningState,
        mode: mode
    }""")
    # use ordered dicts so headers are predictable
    return parsed.search(result, Options(dict_cls=OrderedDict))


def aks_agentpool_list_table_format(results):
    """Format an agent pool list for display with "-o table"."""
    return [_aks_agentpool_table_format(r) for r in results]


def aks_list_table_format(results):
    """"Format a list of managed clusters as summary results for display with "-o table"."""
    return [_aks_table_format(r) for r in results]


def aks_show_table_format(result):
    """Format a managed cluster as summary results for display with "-o table"."""
    return [_aks_table_format(result)]


def _aks_table_format(result):
    parsed = compile_jmes("""{
        name: name,
        location: location,
        resourceGroup: resourceGroup,
        kubernetesVersion: kubernetesVersion,
        currentKubernetesVersion: currentKubernetesVersion,
        provisioningState: provisioningState,
        fqdn: fqdn
    }""")
    # use ordered dicts so headers are predictable
    return parsed.search(result, Options(dict_cls=OrderedDict))


def aks_upgrades_table_format(result):
    """Format get-upgrades results as a summary for display with "-o table"."""

    preview = {}

    def find_preview_versions(versions_bag):
        for upgrade in versions_bag.get('upgrades', []):
            if upgrade.get('isPreview', False):
                preview[upgrade['kubernetesVersion']] = True
    find_preview_versions(result.get('controlPlaneProfile', {}))

    # This expression assumes there is one node pool, and that the master and nodes upgrade in lockstep.
    parsed = compile_jmes("""{
        name: name,
        resourceGroup: resourceGroup,
        masterVersion: controlPlaneProfile.kubernetesVersion || `unknown`,
        upgrades: controlPlaneProfile.upgrades[].kubernetesVersion || [`None available`] | sort_versions(@) | set_preview_array(@) | join(`, `, @)
    }""")
    # use ordered dicts so headers are predictable
    return parsed.search(result, Options(dict_cls=OrderedDict, custom_functions=_custom_functions(preview)))


def version_to_tuple(version):
    """Removes preview suffix"""
    if version.endswith('(preview)'):
        version = version[:-len('(preview)')]
    return tuple(map(int, (version.split('.'))))


# helper function used by aks get-versions, should be removed once dependency bumped to 2.50.0
def flatten_version_table(release_info):
    """Flattens version table"""
    flattened = []
    for release in release_info:
        isPreview = release.get("isPreview", False)
        supportPlan = release.get("capabilities", {}).get("supportPlan", {})
        for k, v in release.get("patchVersions", {}).items():
            item = {"version": k, "upgrades": v.get("upgrades", []), "isPreview": isPreview, "supportPlan": supportPlan}
            flattened.append(item)
    return flattened


def _custom_functions(preview_versions):
    class CustomFunctions(functions.Functions):  # pylint: disable=too-few-public-methods

        @functions.signature({'types': ['array']})
        def _func_sort_versions(self, versions):
            """Custom JMESPath `sort_versions` function that sorts an array of strings as software versions"""
            try:
                return sorted(versions, key=version_to_tuple)
            # if it wasn't sortable, return the input so the pipeline continues
            except (TypeError, ValueError):
                return versions

        @functions.signature({'types': ['array']})
        def _func_set_preview_array(self, versions):
            """Custom JMESPath `set_preview_array` function that suffixes preview version"""
            try:
                for i, _ in enumerate(versions):
                    versions[i] = self._func_set_preview(versions[i])
                return versions
            except (TypeError, ValueError):
                return versions

        @functions.signature({'types': ['string']})
        def _func_set_preview(self, version):
            """Custom JMESPath `set_preview` function that suffixes preview version"""
            try:
                if preview_versions.get(version, False):
                    return version + '(preview)'
                return version
            except (TypeError, ValueError):
                return version

        @functions.signature({'types': ['object']})
        def _func_pprint_labels(self, labels):
            """Custom JMESPath `pprint_labels` function that pretty print labels"""
            if not labels:
                return ''
            return ' '.join([
                f'{k}={labels[k]}'
                for k in sorted(labels.keys())
            ])

    return CustomFunctions()


def aks_pod_identity_exceptions_table_format(result):
    """Format pod identity exceptions results as a summary for display with "-o table"."""
    preview = {}
    parsed = compile_jmes("""podIdentityProfile.userAssignedIdentityExceptions[].{
        name: name,
        namespace: namespace,
        PodLabels: podLabels | pprint_labels(@)
    }""")
    # use ordered dicts so headers are predictable
    return parsed.search(result, Options(dict_cls=OrderedDict, custom_functions=_custom_functions(preview)))


def aks_pod_identities_table_format(result):
    """Format pod identities results as a summary for display with "-o table"."""
    preview = {}
    parsed = compile_jmes("""podIdentityProfile.userAssignedIdentities[].{
        name: name,
        namespace: namespace,
        provisioningState: provisioningState
        identity: identity.resourceId
    }""")
    # use ordered dicts so headers are predictable
    return parsed.search(result, Options(dict_cls=OrderedDict, custom_functions=_custom_functions(preview)))


# helper function used by aks get-versions, should be removed once dependency bumped to 2.50.0
def aks_versions_table_format(result):
    """Format get-versions results as a summary for display with "-o table"."""

    version_table = flatten_version_table(result.get("values", []))

    parsed = compile_jmes("""[].{
        kubernetesVersion: version,
        isPreview: isPreview,
        upgrades: upgrades || [`None available`] | sort_versions(@) | join(`, `, @),
        supportPlan: supportPlan | join(`, `, @)
    }""")
    # use ordered dicts so headers are predictable
    results = parsed.search(version_table, Options(
        dict_cls=OrderedDict, custom_functions=_custom_functions({})))
    return sorted(results, key=lambda x: version_to_tuple(x.get("kubernetesVersion")), reverse=True)


def aks_list_nodepool_snapshot_table_format(results):
    """"Format a list of nodepool snapshots as summary results for display with "-o table"."""
    return [_aks_nodepool_snapshot_table_format(r) for r in results]


def aks_show_nodepool_snapshot_table_format(result):
    """Format a nodepool snapshot as summary results for display with "-o table"."""
    return [_aks_nodepool_snapshot_table_format(result)]


def _aks_nodepool_snapshot_table_format(result):
    parsed = compile_jmes("""{
        name: name,
        location: location,
        resourceGroup: resourceGroup,
        nodeImageVersion: nodeImageVersion,
        kubernetesVersion: kubernetesVersion,
        osType: osType,
        osSku: osSku,
        enableFIPS: enableFIPS
    }""")
    # use ordered dicts so headers are predictable
    return parsed.search(result, Options(dict_cls=OrderedDict))


def aks_list_snapshot_table_format(results):
    """"Format a list of cluster snapshots as summary results for display with "-o table"."""
    return [_aks_snapshot_table_format(r) for r in results]


def aks_show_snapshot_table_format(result):
    """Format a cluster snapshot as summary results for display with "-o table"."""
    return [_aks_snapshot_table_format(result)]


def _aks_snapshot_table_format(result):
    parsed = compile_jmes("""{
        name: name,
        location: location,
        resourceGroup: resourceGroup,
        sku: managedClusterPropertiesReadOnly.sku.tier,
        enableRbac: managedClusterPropertiesReadOnly.enableRbac,
        kubernetesVersion: managedClusterPropertiesReadOnly.kubernetesVersion,
        networkPlugin: managedClusterPropertiesReadOnly.networkProfile.networkPlugin,
        networkPolicy: managedClusterPropertiesReadOnly.networkProfile.networkPolicy,
        networkMode: managedClusterPropertiesReadOnly.networkProfile.networkMode,
        loadBalancerSku: managedClusterPropertiesReadOnly.networkProfile.loadBalancerSku
    }""")
    # use ordered dicts so headers are predictable
    return parsed.search(result, Options(dict_cls=OrderedDict))


def aks_mesh_revisions_table_format(result):
    """Format a list of mesh revisions as summary results for display with "-o table". """
    revision_table = flatten_mesh_revision_table(result['meshRevisions'])
    parsed = compile_jmes("""[].{
        revision: revision,
        upgrades: upgrades || [`None available`] | sort_versions(@) | join(`, `, @),
        compatibleWith: compatibleWith_name,
        compatibleVersions: compatibleVersions || [`None available`] | sort_versions(@) | join(`, `, @)
    }""")
    # Use ordered dicts so headers are predictable
    results = parsed.search(revision_table, Options(
        dict_cls=OrderedDict, custom_functions=_custom_functions({})))

    return results


# Helper function used by aks_mesh_revisions_table_format
def flatten_mesh_revision_table(revision_info):
    """Flattens revision information"""
    flattened = []
    for revision_data in revision_info:
        flattened.extend(_format_mesh_revision_entry(revision_data))
    return flattened


def aks_mesh_upgrades_table_format(result):
    """Format a list of mesh upgrades as summary results for display with "-o table". """
    upgrades_table = _format_mesh_revision_entry(result)
    parsed = compile_jmes("""[].{
        revision: revision,
        upgrades: upgrades || [`None available`] | sort_versions(@) | join(`, `, @),
        compatibleWith: compatibleWith_name,
        compatibleVersions: compatibleVersions || [`None available`] | sort_versions(@) | join(`, `, @)
    }""")
    # Use ordered dicts so headers are predictable
    results = parsed.search(upgrades_table, Options(
        dict_cls=OrderedDict, custom_functions=_custom_functions({})))
    return results


def _format_mesh_revision_entry(revision):
    flattened = []
    revision_entry = revision['revision']
    upgrades = revision['upgrades']
    compatible_with_list = revision['compatibleWith']
    for compatible_with in compatible_with_list:
        item = {
            'revision': revision_entry,
            'upgrades': upgrades,
            'compatibleWith_name': compatible_with['name'],
            'compatibleVersions': compatible_with['versions']
        }
        flattened.append(item)
    return flattened


def aks_extension_list_table_format(results):
    """Format a list of K8s extensions as summary results for display with "-o table". """
    return [_get_extension_table_row(result) for result in results]


def aks_extension_show_table_format(result):
    """Format a K8s extension as summary results for display with "-o table". """
    return _get_extension_table_row(result)


def _get_extension_table_row(result):
    return OrderedDict([
        ('name', result['name']),
        ('extensionType', result.get('extensionType', '')),
        ('version', result.get('version', '')),
        ('provisioningState', result.get('provisioningState', '')),
        ('lastModifiedAt', result.get('systemData', {}).get('lastModifiedAt', '')),
        ('isSystemExtension', result.get('isSystemExtension', '')),
    ])


def aks_extension_types_list_table_format(results):
    """Format a list of K8s extension types as summary results for display with "-o table". """
    return [_get_extension_type_table_row(result) for result in results]


def aks_extension_type_show_table_format(result):
    """Format a K8s extension type as summary results for display with "-o table". """
    return _get_extension_type_table_row(result)


def _get_extension_type_table_row(result):
    # Populate the values to be returned if they are not undefined
    clusterTypes = ''
    if result['properties']['supportedClusterTypes'] is not None:
        clusterTypes = ', '.join(result['properties']['supportedClusterTypes'])

    name = result['name']
    defaultScope, allowMultInstances, defaultReleaseNamespace = '', '', ''
    if result['properties']['supportedScopes']:
        defaultScope = result['properties']['supportedScopes']['defaultScope']
        if result['properties']['supportedScopes']['clusterScopeSettings'] is not None:
            clusterScopeSettings = result['properties']['supportedScopes']['clusterScopeSettings']
            allowMultInstances = clusterScopeSettings['allowMultipleInstances']
            defaultReleaseNamespace = clusterScopeSettings['defaultReleaseNamespace']

    retVal = OrderedDict([
        ('name', name),
        ('defaultScope', defaultScope),
        ('clusterTypes', clusterTypes),
        ('allowMultipleInstances', allowMultInstances),
        ('defaultReleaseNamespace', defaultReleaseNamespace)
    ])

    return retVal


def aks_extension_type_versions_list_table_format(results):
    """Format a list of K8s extension type versions as summary results for display with "-o table". """
    return [_get_extension_type_versions_table_row(result) for result in results]


def aks_extension_type_version_show_table_format(results):
    """Format a K8s extension type version as summary results for display with "-o table". """
    return _get_extension_type_versions_table_row(results)


def _get_extension_type_versions_table_row(result):
    return OrderedDict([
        ('versions', result['properties']['version'])
    ])


def aks_jwtauthenticator_list_table_format(results):
    """Format a list of JWT authenticators as summary results for display with "-o table". """
    return [_get_jwtauthenticator_table_row(result) for result in results]


def aks_jwtauthenticator_show_table_format(result):
    """Format a JWT authenticator as summary results for display with "-o table". """
    return _get_jwtauthenticator_table_row(result)


def _get_jwtauthenticator_table_row(result):
    """Extract information from a JWT authenticator for table display."""
    properties = result.get('properties', {})
    provisioningState = properties.get('provisioningState', '')
    issuer = properties.get('issuer', {})

    issuer_url = issuer.get('url', '') if issuer else ''
    audiences = issuer.get('audiences', []) if issuer else []
    audience_list = ', '.join(audiences) if audiences else ''

    claim_mappings = properties.get('claimMappings', {})
    has_claim_mappings = 'No'
    if claim_mappings:
        has_username = bool(claim_mappings.get('username'))
        has_groups = bool(claim_mappings.get('groups'))
        has_uid = bool(claim_mappings.get('uid'))
        has_extra = (claim_mappings.get('extra') and
                     isinstance(claim_mappings['extra'], list) and
                     len(claim_mappings['extra']) > 0)

        if has_username or has_groups or has_uid or has_extra:
            has_claim_mappings = 'Yes'

    claim_rules = properties.get('claimValidationRules', [])
    user_rules = properties.get('userValidationRules', [])
    has_claim_rules = 'Yes' if claim_rules else 'No'
    has_user_rules = 'Yes' if user_rules else 'No'

    return OrderedDict([
        ('name', result.get('name', '')),
        ('provisioningState', provisioningState),
        ('issuerUrl', issuer_url),
        ('audiences', audience_list),
        ('hasClaimMappings', has_claim_mappings),
        ('hasClaimRules', has_claim_rules),
        ('hasUserRules', has_user_rules),
    ])
