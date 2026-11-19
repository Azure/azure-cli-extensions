# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.aaz import AAZCommand

from ._list import List as _MaintenanceEventList


_MAINTENANCE_MESSAGE = (
    'Maintenance updates are managed by the system. '
    'Currently, HorizonDB supports System-Managed Maintenance Window.'
)


class MaintenanceEventList(_MaintenanceEventList):
    AZ_HELP = {
        **_MaintenanceEventList.AZ_HELP,
        'short-summary': 'Show the system-managed maintenance policy for a HorizonDB pool.',
        'long-summary': _MAINTENANCE_MESSAGE,
        'examples': [{
            'name': 'Show maintenance information for a HorizonDB pool',
            'text': 'az horizondb cluster pool maintenance-event list --resource-group example-resource-group '
                    '--cluster-name example-cluster --pool-name example-pool',
        }],
    }

    AZ_SUPPORT_PAGINATION = False
    _arguments_schema = None
    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.filter._registered = False  # pylint: disable=protected-access
        return args_schema

    def _handler(self, command_args):
        AAZCommand._handler(self, command_args)
        return _MAINTENANCE_MESSAGE
