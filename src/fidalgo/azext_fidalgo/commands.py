# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_fidalgo._client_factory import *

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

    fidalgo_catalog_item = CliCommandType(
        operations_tmpl=(
            'azext_fidalgo.vendored_sdks.azure_fidalgo.operations._catalog_item_operations#CatalogItemOperations.{}'
        ),
        client_factory=cf_catalog_item,
    )


    fidalgo_deployment = CliCommandType(
        operations_tmpl=(
            'azext_fidalgo.vendored_sdks.azure_fidalgo.operations._deployments_operations#DeploymentsOperations.{}'
        ),
        client_factory=cf_deployment,
    )


    fidalgo_environment = CliCommandType(
        operations_tmpl=(
            'azext_fidalgo.vendored_sdks.azure_fidalgo.operations._environments_operations#EnvironmentsOperations.{}'
        ),
        client_factory=cf_environment,
    )


    fidalgo_environment_type = CliCommandType(
        operations_tmpl=(
            'azext_fidalgo.vendored_sdks.azure_fidalgo.operations._environment_type_operations#EnvironmentTypeOperations.{}'
        ),
        client_factory=cf_environment_type,
    )

    with self.command_group('fidalgo pool', fidalgo_pool, client_factory=cf_pool) as g:
        g.custom_command('list', 'fidalgo_pool_list')
        g.custom_show_command('show', 'fidalgo_pool_show')

    with self.command_group('fidalgo project', fidalgo_project, client_factory=cf_project) as g:
        g.custom_command('list', 'fidalgo_project_list')

    with self.command_group('fidalgo', is_preview=True):
        pass

    with self.command_group('fidalgo virtual-machine', fidalgo_virtual_machine, client_factory=cf_virtual_machine) as g:
        g.custom_command('list', 'fidalgo_virtual_machine_list')
        g.custom_show_command('show', 'fidalgo_virtual_machine_show')
        g.custom_command('create', 'fidalgo_virtual_machine_create')
        g.custom_command('delete', 'fidalgo_virtual_machine_delete', confirmation=True)
        g.custom_command('assign', 'fidalgo_virtual_machine_assign')
        g.custom_command('get-rdp-file-content', 'fidalgo_virtual_machine_get_rdp_file_content')
        g.custom_command('start', 'fidalgo_virtual_machine_start')
        g.custom_command('stop', 'fidalgo_virtual_machine_stop')

    with self.command_group('fidalgo catalog-item', fidalgo_catalog_item, client_factory=cf_catalog_item) as g:
        g.custom_command('list', 'fidalgo_catalog_item_list')

    with self.command_group('fidalgo deployment', fidalgo_deployment, client_factory=cf_deployment) as g:
        g.custom_command('list', 'fidalgo_deployment_list')

    with self.command_group('fidalgo environment', fidalgo_environment, client_factory=cf_environment) as g:
        g.custom_command('list', 'fidalgo_environment_list')
        g.custom_show_command('show', 'fidalgo_environment_show')
        g.custom_command('create', 'fidalgo_environment_create')
        g.custom_command('update', 'fidalgo_environment_update')
        g.custom_command('delete', 'fidalgo_environment_delete', confirmation=True)
        g.custom_command('deploy', 'fidalgo_environment_deploy')

    with self.command_group(
        'fidalgo environment-type', fidalgo_environment_type, client_factory=cf_environment_type
    ) as g:
        g.custom_command('list', 'fidalgo_environment_type_list')
    
