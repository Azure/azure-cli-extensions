# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=too-many-statements


def load_command_table(self, _):  # pylint: disable=unused-argument
    from azure.cli.core.commands import CliCommandType
    from azext_workload_manager.custom import RuntimeBindingCreate
    self.command_table[
        'workload-manager workload-space runtime-binding create'
    ] = RuntimeBindingCreate(loader=self)
    workload_space_up_commands = CliCommandType(
        operations_tmpl='azext_workload_manager._workload_space_up#{}'
    )
    with self.command_group(
            'workload-manager workload-space', custom_command_type=workload_space_up_commands) as g:
        g.custom_command('up', 'workload_space_up', supports_no_wait=True)
