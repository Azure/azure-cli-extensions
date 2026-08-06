# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict


def _get_resource_group(result):
    """Derive the resource group name from the resource id."""
    resource_id = result.get('id', '')
    if resource_id:
        from azure.mgmt.core.tools import parse_resource_id
        parsed = parse_resource_id(resource_id)
        return parsed.get('resource_group', '')
    return ''


def scheduler_table_format(result):
    """Format a single scheduler for table output."""
    return OrderedDict([
        ('Name', result.get('name', '')),
        ('ResourceGroup', _get_resource_group(result)),
        ('Location', result.get('location', '')),
        ('State', result.get('properties', {}).get('provisioningState', '')),
        ('SKU', result.get('properties', {}).get('sku', {}).get('name', '')),
        ('Capacity Units', result.get('properties', {}).get('sku', {}).get('capacity', '')),
    ])


def scheduler_list_table_format(results):
    """Format a list of schedulers for table output."""
    return [scheduler_table_format(r) for r in results]


def taskhub_table_format(result):
    """Format a single task hub for table output."""
    return OrderedDict([
        ('Name', result.get('name', '')),
        ('ResourceGroup', _get_resource_group(result)),
        ('State', result.get('properties', {}).get('provisioningState', '')),
    ])


def taskhub_list_table_format(results):
    """Format a list of task hubs for table output."""
    return [taskhub_table_format(r) for r in results]
