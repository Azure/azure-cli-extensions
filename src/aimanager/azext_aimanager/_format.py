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
