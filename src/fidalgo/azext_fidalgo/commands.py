# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_fidalgo._client_factory import cf_project
from azext_fidalgo._client_factory import cf_pool
from azext_fidalgo._client_factory import cf_virtual_machine


def load_command_table(self, _):

    # TODO: Add command type here
    # fidalgo_sdk = CliCommandType(
    #    operations_tmpl='<PATH>.operations#None.{}',
    #    client_factory=cf_fidalgo)

    fidalgo_pool = CliCommandType(
    operations_tmpl='azext_fidalgo.vendored_sdks.azure_fidalgo.operations._pool_operations#PoolOperations.{}',
    client_factory=cf_pool,
    )


    fidalgo_project = CliCommandType(
        operations_tmpl='azext_fidalgo.vendored_sdks.fidalgo_dataplane.operations._project_operations#ProjectOperations.{}',
        client_factory=cf_project,
    )

    fidalgo_virtual_machine = CliCommandType(
        operations_tmpl=(
            'azext_fidalgo.vendored_sdks.fidalgo_dataplane.operations._virtual_machine_operations#VirtualMachineOperations.{}'
        ),
        client_factory=cf_virtual_machine,
    )

    with self.command_group('fidalgo pool', fidalgo_pool, client_factory=cf_pool) as g:
        g.custom_command('list', 'fidalgo_pool_list')
        g.custom_show_command('show', 'fidalgo_pool_show')

    with self.command_group('fidalgo project', fidalgo_project, client_factory=cf_project) as g:
        g.custom_command('list', 'fidalgo_project_list')

    with self.command_group('fidalgo', is_preview=True):
        pass


    with self.command_group('fidalgo project', client_factory=cf_project) as g:
        g.custom_command('list', 'list_project')

    with self.command_group('fidalgo virtual-machine', fidalgo_virtual_machine, client_factory=cf_virtual_machine) as g:
        g.custom_command('list', 'fidalgo_virtual_machine_list')
        g.custom_show_command('show', 'fidalgo_virtual_machine_show')
        g.custom_command('create', 'fidalgo_virtual_machine_create')
        g.custom_command('delete', 'fidalgo_virtual_machine_delete', confirmation=True)
        g.custom_command('assign', 'fidalgo_virtual_machine_assign')
        g.custom_command('get-rdp-file-content', 'fidalgo_virtual_machine_get_rdp_file_content')
        g.custom_command('start', 'fidalgo_virtual_machine_start')
        g.custom_command('stop', 'fidalgo_virtual_machine_stop')
    
