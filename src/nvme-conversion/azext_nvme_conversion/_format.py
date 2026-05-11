# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Output table formatters for nvme-conversion commands."""


def check_result_table_format(result):
    """Format the check command output as a table."""
    if not result:
        return []

    rows = []
    for check_name, check_result in result.get('checks', {}).items():
        rows.append({
            'Check': check_name,
            'Status': check_result.get('status', 'unknown'),
            'Message': check_result.get('message', ''),
        })

    return rows


def convert_result_table_format(result):
    """Format the convert command output as a table."""
    if not result:
        return []

    return [{
        'VM': result.get('vm', ''),
        'ResourceGroup': result.get('resourceGroup', ''),
        'Status': result.get('status', ''),
        'PreviousSize': result.get('previousSize', ''),
        'NewSize': result.get('newSize', ''),
        'ControllerType': result.get('controllerType', ''),
        'VMStarted': str(result.get('vmStarted', '')),
    }]
