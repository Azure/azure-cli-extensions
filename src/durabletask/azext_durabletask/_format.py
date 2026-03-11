# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict


def scheduler_table_format(result):
    """Format a single scheduler for table output."""
    return OrderedDict([
        ('Name', result.get('name', '')),
        ('ResourceGroup', result.get('resourceGroup', '')),
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
        ('ResourceGroup', result.get('resourceGroup', '')),
        ('State', result.get('properties', {}).get('provisioningState', '')),
    ])


def taskhub_list_table_format(results):
    """Format a list of task hubs for table output."""
    return [taskhub_table_format(r) for r in results]
