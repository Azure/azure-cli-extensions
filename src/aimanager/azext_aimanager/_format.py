# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict


def _parse_resource_id(resource_id):
    """Parse an ARM resource id into its component parts (best-effort)."""
    if not resource_id:
        return {}
    from azure.mgmt.core.tools import parse_resource_id
    return parse_resource_id(resource_id)


def aimanager_table_format(result):
    """Format a single AI Manager resource for display with "-o table"."""
    parsed = _parse_resource_id(result.get('id', ''))
    properties = result.get('properties') or {}
    return OrderedDict([
        ('Name', result.get('name', '')),
        ('ProvisioningState', properties.get('provisioningState', '')),
        ('ResourceGroup', parsed.get('resource_group', '')),
        ('Location', result.get('location', '')),
    ])


def aimanager_list_table_format(results):
    """Format a list of AI Manager resources for display with "-o table"."""
    return [aimanager_table_format(r) for r in results]


def _labels_display(labels):
    """Render a labels dict as comma-joined key=value pairs, sorted for stable output."""
    if not labels:
        return ''
    return ','.join('{}={}'.format(k, labels[k]) for k in sorted(labels))


def namespace_table_format(result):
    """Format a single AI Manager namespace resource for display with "-o table"."""
    properties = result.get('properties') or {}
    return OrderedDict([
        ('Name', result.get('name', '')),
        ('ProvisioningState', properties.get('provisioningState', '')),
        ('Labels', _labels_display(properties.get('labels'))),
    ])


def namespace_list_table_format(results):
    """Format a list of AI Manager namespace resources for display with "-o table"."""
    return [namespace_table_format(r) for r in results]


def _replica_display(value):
    """Render a replica count, using '-' when the count is not yet reported."""
    return str(value) if value is not None else '-'


def modeldeployment_table_format(result):
    """Format a single model deployment resource for display with "-o table"."""
    parsed = _parse_resource_id(result.get('id', ''))
    properties = result.get('properties') or {}
    status = properties.get('status') or {}

    # ``modelId`` (human-readable, e.g. "meta-llama/Llama-3-8B") is resolved from the
    # deployment's ``modelResourceId`` by the custom list/show functions and injected onto
    # the result. Fall back to the AIModel resource name when resolution is unavailable.
    model_id = result.get('modelId')
    if not model_id:
        model_ref = _parse_resource_id(properties.get('modelResourceId', ''))
        model_id = model_ref.get('resource_name', '')

    replicas = '{}/{}'.format(
        _replica_display(status.get('currentReplicas')),
        _replica_display(status.get('desiredReplicas')),
    )

    return OrderedDict([
        ('Name', result.get('name', '')),
        ('ProvisioningState', properties.get('provisioningState', '')),
        ('ModelId', model_id or ''),
        ('Replicas', replicas),
        ('Endpoint', status.get('endpoint', '')),
        ('Namespace', parsed.get('child_name_1', '')),
    ])


def modeldeployment_list_table_format(results):
    """Format a list of model deployment resources for display with "-o table"."""
    return [modeldeployment_table_format(r) for r in results]
