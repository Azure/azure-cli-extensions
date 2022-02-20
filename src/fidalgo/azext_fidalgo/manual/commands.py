# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_fidalgo.manual._client_factory import *
from azext_fidalgo.generated._client_factory import (
    cf_dev_center,
    cf_project,
    cf_environment,
    cf_deployment,
    cf_environment_type,
    cf_catalog_item,
    cf_gallery,
    cf_image,
    cf_image_version,
    cf_catalog,
    cf_mapping,
    cf_operation_statuses,
    cf_sku,
    cf_pool,
    cf_machine_definition,
    cf_network_setting,
)

def load_command_table(self, _):

    #data plane
    fidalgo_pool_dp = CliCommandType(
    operations_tmpl='azext_fidalgo.vendored_sdks.azure_fidalgo.operations._pool_operations#PoolOperations.{}',
    client_factory=cf_pool_dp,
    )


    fidalgo_project_dp = CliCommandType(
        operations_tmpl='azext_fidalgo.vendored_sdks.fidalgo_dataplane.operations._project_operations#ProjectOperations.{}',
        client_factory=cf_project_dp,
    )

    fidalgo_virtual_machine = CliCommandType(
        operations_tmpl=(
            'azext_fidalgo.vendored_sdks.fidalgo_dataplane.operations._virtual_machine_operations#VirtualMachineOperations.{}'
        ),
        client_factory=cf_virtual_machine_dp,
    )

    fidalgo_catalog_item_dp = CliCommandType(
        operations_tmpl=(
            'azext_fidalgo.vendored_sdks.azure_fidalgo.operations._catalog_item_operations#CatalogItemOperations.{}'
        ),
        client_factory=cf_catalog_item_dp,
    )


    fidalgo_deployment_dp = CliCommandType(
        operations_tmpl=(
            'azext_fidalgo.vendored_sdks.azure_fidalgo.operations._deployments_operations#DeploymentsOperations.{}'
        ),
        client_factory=cf_deployment_dp,
    )


    fidalgo_environment_dp = CliCommandType(
        operations_tmpl=(
            'azext_fidalgo.vendored_sdks.azure_fidalgo.operations._environments_operations#EnvironmentsOperations.{}'
        ),
        client_factory=cf_environment_dp,
    )


    fidalgo_environment_type_dp = CliCommandType(
        operations_tmpl=(
            'azext_fidalgo.vendored_sdks.azure_fidalgo.operations._environment_type_operations#EnvironmentTypeOperations.{}'
        ),
        client_factory=cf_environment_type_dp,
    )

    #control plane
    fidalgo_catalog = CliCommandType(
        operations_tmpl='azext_fidalgo.vendored_sdks.fidalgo.operations._catalogs_operations#CatalogsOperations.{}',
        client_factory=cf_catalog,
    )


    fidalgo_catalog_item = CliCommandType(
        operations_tmpl=(
            'azext_fidalgo.vendored_sdks.fidalgo.operations._catalog_items_operations#CatalogItemsOperations.{}'
        ),
        client_factory=cf_catalog_item,
    )


    fidalgo_deployment = CliCommandType(
        operations_tmpl='azext_fidalgo.vendored_sdks.fidalgo.operations._deployments_operations#DeploymentsOperations.{}',
        client_factory=cf_deployment,
    )


    fidalgo_dev_center = CliCommandType(
        operations_tmpl='azext_fidalgo.vendored_sdks.fidalgo.operations._dev_centers_operations#DevCentersOperations.{}',
        client_factory=cf_dev_center,
    )


    fidalgo_environment = CliCommandType(
        operations_tmpl='azext_fidalgo.vendored_sdks.fidalgo.operations._environments_operations#EnvironmentsOperations.{}',
        client_factory=cf_environment,
    )


    fidalgo_environment_type = CliCommandType(
        operations_tmpl=(
            'azext_fidalgo.vendored_sdks.fidalgo.operations._environment_types_operations#EnvironmentTypesOperations.{}'
        ),
        client_factory=cf_environment_type,
    )


    fidalgo_gallery = CliCommandType(
        operations_tmpl='azext_fidalgo.vendored_sdks.fidalgo.operations._galleries_operations#GalleriesOperations.{}',
        client_factory=cf_gallery,
    )


    fidalgo_image = CliCommandType(
        operations_tmpl='azext_fidalgo.vendored_sdks.fidalgo.operations._images_operations#ImagesOperations.{}',
        client_factory=cf_image,
    )


    fidalgo_image_version = CliCommandType(
        operations_tmpl=(
            'azext_fidalgo.vendored_sdks.fidalgo.operations._image_versions_operations#ImageVersionsOperations.{}'
        ),
        client_factory=cf_image_version,
    )


    fidalgo_machine_definition = CliCommandType(
        operations_tmpl=(
            'azext_fidalgo.vendored_sdks.fidalgo.operations._machine_definitions_operations#MachineDefinitionsOperations.{}'
        ),
        client_factory=cf_machine_definition,
    )


    fidalgo_mapping = CliCommandType(
        operations_tmpl='azext_fidalgo.vendored_sdks.fidalgo.operations._mappings_operations#MappingsOperations.{}',
        client_factory=cf_mapping,
    )


    fidalgo_network_setting = CliCommandType(
        operations_tmpl=(
            'azext_fidalgo.vendored_sdks.fidalgo.operations._network_settings_operations#NetworkSettingsOperations.{}'
        ),
        client_factory=cf_network_setting,
    )


    fidalgo_operation_statuses = CliCommandType(
        operations_tmpl=(
            'azext_fidalgo.vendored_sdks.fidalgo.operations._operation_statuses_operations#OperationStatusesOperations.{}'
        ),
        client_factory=cf_operation_statuses,
    )


    fidalgo_pool = CliCommandType(
        operations_tmpl='azext_fidalgo.vendored_sdks.fidalgo.operations._pools_operations#PoolsOperations.{}',
        client_factory=cf_pool,
    )


    fidalgo_project = CliCommandType(
        operations_tmpl='azext_fidalgo.vendored_sdks.fidalgo.operations._projects_operations#ProjectsOperations.{}',
        client_factory=cf_project,
    )


    fidalgo_sku = CliCommandType(
        operations_tmpl='azext_fidalgo.vendored_sdks.fidalgo.operations._skus_operations#SkusOperations.{}',
        client_factory=cf_sku,
    )

    with self.command_group('fidalgo dev', fidalgo_project_dp):
            pass
    
    with self.command_group('fidalgo admin', fidalgo_project_dp):
            pass

    #data plane 
    with self.command_group('fidalgo dev project', fidalgo_project_dp, client_factory=cf_project_dp) as g:
        g.custom_command('list', 'fidalgo_project_list_dp')

    with self.command_group('fidalgo dev pool', fidalgo_pool_dp, client_factory=cf_pool_dp) as g:
        g.custom_command('list', 'fidalgo_pool_list_dp')
        g.custom_show_command('show', 'fidalgo_pool_show_dp')
    
    with self.command_group('fidalgo dev virtual-machine', fidalgo_virtual_machine, client_factory=cf_virtual_machine_dp) as g:
        g.custom_command('list', 'fidalgo_virtual_machine_list')
        g.custom_show_command('show', 'fidalgo_virtual_machine_show')
        g.custom_command('create', 'fidalgo_virtual_machine_create')
        g.custom_command('delete', 'fidalgo_virtual_machine_delete', confirmation=True)
        g.custom_command('assign', 'fidalgo_virtual_machine_assign')
        g.custom_command('get-rdp-file-content', 'fidalgo_virtual_machine_get_rdp_file_content')
        g.custom_command('start', 'fidalgo_virtual_machine_start')
        g.custom_command('stop', 'fidalgo_virtual_machine_stop')

    with self.command_group('fidalgo dev catalog-item', fidalgo_catalog_item_dp, client_factory=cf_catalog_item_dp) as g:
        g.custom_command('list', 'fidalgo_catalog_item_list_dp')

    with self.command_group('fidalgo dev deployment', fidalgo_deployment_dp, client_factory=cf_deployment_dp) as g:
        g.custom_command('list', 'fidalgo_deployment_list_dp')

    with self.command_group('fidalgo dev environment', fidalgo_environment_dp, client_factory=cf_environment_dp) as g:
        g.custom_command('list', 'fidalgo_environment_list_dp')
        g.custom_show_command('show', 'fidalgo_environment_show_dp')
        g.custom_command('create', 'fidalgo_environment_create_dp')
        g.custom_command('update', 'fidalgo_environment_update_dp')
        g.custom_command('delete', 'fidalgo_environment_delete_dp', confirmation=True)
        g.custom_command('deploy', 'fidalgo_environment_deploy_dp')

    with self.command_group(
        'fidalgo dev environment-type', fidalgo_environment_type_dp, client_factory=cf_environment_type_dp
    ) as g:
        g.custom_command('list', 'fidalgo_environment_type_list_dp')
    
    #control plane
    with self.command_group('fidalgo admin catalog', fidalgo_catalog, client_factory=cf_catalog) as g:
        g.custom_command('list', 'fidalgo_catalog_list')
        g.custom_show_command('show', 'fidalgo_catalog_show')
        g.custom_command('create', 'fidalgo_catalog_create', supports_no_wait=True)
        g.custom_command('update', 'fidalgo_catalog_update', supports_no_wait=True)
        g.custom_command('delete', 'fidalgo_catalog_delete', supports_no_wait=True, confirmation=True)
        g.custom_command('sync', 'fidalgo_catalog_sync', supports_no_wait=True)
        g.custom_wait_command('wait', 'fidalgo_catalog_show')

    with self.command_group('fidalgo admin catalog-item', fidalgo_catalog_item, client_factory=cf_catalog_item) as g:
        g.custom_command('list', 'fidalgo_catalog_item_list')
        g.custom_show_command('show', 'fidalgo_catalog_item_show')
        g.custom_command('create', 'fidalgo_catalog_item_create')
        g.custom_command('update', 'fidalgo_catalog_item_update')
        g.custom_command('delete', 'fidalgo_catalog_item_delete', confirmation=True)

    with self.command_group('fidalgo admin deployment', fidalgo_deployment, client_factory=cf_deployment) as g:
        g.custom_command('list', 'fidalgo_deployment_list')

    with self.command_group('fidalgo admin dev-center', fidalgo_dev_center, client_factory=cf_dev_center) as g:
        g.custom_command('list', 'fidalgo_dev_center_list')
        g.custom_show_command('show', 'fidalgo_dev_center_show')
        g.custom_command('create', 'fidalgo_dev_center_create', supports_no_wait=True)
        g.custom_command('update', 'fidalgo_dev_center_update', supports_no_wait=True)
        g.custom_command('delete', 'fidalgo_dev_center_delete', supports_no_wait=True, confirmation=True)
        g.custom_wait_command('wait', 'fidalgo_dev_center_show')

    with self.command_group('fidalgo admin environment', fidalgo_environment, client_factory=cf_environment) as g:
        g.custom_command('list', 'fidalgo_environment_list')
        g.custom_show_command('show', 'fidalgo_environment_show')
        g.custom_command('create', 'fidalgo_environment_create', supports_no_wait=True)
        g.custom_command('update', 'fidalgo_environment_update', supports_no_wait=True)
        g.custom_command('delete', 'fidalgo_environment_delete', supports_no_wait=True, confirmation=True)
        g.custom_command('deploy', 'fidalgo_environment_deploy', supports_no_wait=True)
        g.custom_wait_command('wait', 'fidalgo_environment_show')

    with self.command_group(
        'fidalgo admin environment-type', fidalgo_environment_type, client_factory=cf_environment_type
    ) as g:
        g.custom_command('list', 'fidalgo_environment_type_list')
        g.custom_show_command('show', 'fidalgo_environment_type_show')
        g.custom_command('create', 'fidalgo_environment_type_create')
        g.custom_command('update', 'fidalgo_environment_type_update')
        g.custom_command('delete', 'fidalgo_environment_type_delete', supports_no_wait=True, confirmation=True)
        g.custom_wait_command('wait', 'fidalgo_environment_type_show')

    with self.command_group('fidalgo admin gallery', fidalgo_gallery, client_factory=cf_gallery) as g:
        g.custom_command('list', 'fidalgo_gallery_list')
        g.custom_show_command('show', 'fidalgo_gallery_show')
        g.custom_command('create', 'fidalgo_gallery_create', supports_no_wait=True)
        g.generic_update_command(
            'update',
            supports_no_wait=True,
            custom_func_name='fidalgo_gallery_update',
            setter_arg_name='body',
            setter_name='begin_create_or_update',
        )
        g.custom_command('delete', 'fidalgo_gallery_delete', supports_no_wait=True, confirmation=True)
        g.custom_wait_command('wait', 'fidalgo_gallery_show')

    with self.command_group('fidalgo admin image', fidalgo_image, client_factory=cf_image) as g:
        g.custom_command('list', 'fidalgo_image_list')
        g.custom_show_command('show', 'fidalgo_image_show')

    with self.command_group('fidalgo admin image-version', fidalgo_image_version, client_factory=cf_image_version) as g:
        g.custom_command('list', 'fidalgo_image_version_list')
        g.custom_show_command('show', 'fidalgo_image_version_show')

    with self.command_group(
        'fidalgo admin machine-definition', fidalgo_machine_definition, client_factory=cf_machine_definition
    ) as g:
        g.custom_command('list', 'fidalgo_machine_definition_list')
        g.custom_show_command('show', 'fidalgo_machine_definition_show')
        g.custom_command('create', 'fidalgo_machine_definition_create', supports_no_wait=True)
        g.custom_command('update', 'fidalgo_machine_definition_update', supports_no_wait=True)
        g.custom_command('delete', 'fidalgo_machine_definition_delete', supports_no_wait=True, confirmation=True)
        g.custom_wait_command('wait', 'fidalgo_machine_definition_show')

    with self.command_group('fidalgo admin mapping', fidalgo_mapping, client_factory=cf_mapping) as g:
        g.custom_command('list', 'fidalgo_mapping_list')
        g.custom_show_command('show', 'fidalgo_mapping_show')
        g.custom_command('create', 'fidalgo_mapping_create')
        g.custom_command('update', 'fidalgo_mapping_update')
        g.custom_command('delete', 'fidalgo_mapping_delete', confirmation=True)

    with self.command_group('fidalgo admin network-setting', fidalgo_network_setting, client_factory=cf_network_setting) as g:
        g.custom_command('list', 'fidalgo_network_setting_list')
        g.custom_show_command('show', 'fidalgo_network_setting_show')
        g.custom_command('create', 'fidalgo_network_setting_create', supports_no_wait=True)
        g.custom_command('update', 'fidalgo_network_setting_update', supports_no_wait=True)
        g.custom_command('delete', 'fidalgo_network_setting_delete', supports_no_wait=True, confirmation=True)
        g.custom_command('show-health-detail', 'fidalgo_network_setting_show_health_detail')
        g.custom_wait_command('wait', 'fidalgo_network_setting_show')

    with self.command_group(
        'fidalgo admin operation-statuses', fidalgo_operation_statuses, client_factory=cf_operation_statuses
    ) as g:
        g.custom_show_command('show', 'fidalgo_operation_statuses_show')

    with self.command_group('fidalgo admin pool', fidalgo_pool, client_factory=cf_pool) as g:
        g.custom_command('list', 'fidalgo_pool_list')
        g.custom_show_command('show', 'fidalgo_pool_show')
        g.custom_command('create', 'fidalgo_pool_create', supports_no_wait=True)
        g.custom_command('update', 'fidalgo_pool_update', supports_no_wait=True)
        g.custom_command('delete', 'fidalgo_pool_delete', supports_no_wait=True, confirmation=True)
        g.custom_wait_command('wait', 'fidalgo_pool_show')

    with self.command_group('fidalgo admin project', fidalgo_project, client_factory=cf_project) as g:
        g.custom_command('list', 'fidalgo_project_list')
        g.custom_show_command('show', 'fidalgo_project_show')
        g.custom_command('create', 'fidalgo_project_create', supports_no_wait=True)
        g.custom_command('update', 'fidalgo_project_update', supports_no_wait=True)
        g.custom_command('delete', 'fidalgo_project_delete', supports_no_wait=True, confirmation=True)
        g.custom_wait_command('wait', 'fidalgo_project_show')

    with self.command_group('fidalgo admin sku', fidalgo_sku, client_factory=cf_sku) as g:
        g.custom_command('list', 'fidalgo_sku_list')

    with self.command_group('fidalgo', is_experimental=True):
        pass