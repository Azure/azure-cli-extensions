# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_devcenter.manual._client_factory import *
from azext_devcenter.generated._client_factory import (
    cf_dev_center,
    cf_project,
    cf_attached_network,
    cf_environment_type,
    cf_project_environment_type,
    cf_gallery,
    cf_image,
    cf_image_version,
    cf_catalog,
    cf_dev_box_definition,
    cf_usage,
    cf_sku,
    cf_pool,
    cf_network_connection,
    cf_schedule
)

def load_command_table(self, _):

    #data plane
    devcenter_action_dp = CliCommandType(
        operations_tmpl=(
            'azext_devcenter.vendored_sdks.devcenter_dataplane.operations._actions_operations#ActionsOperations.{}'
        ),
        client_factory=cf_action_dp,
    )

    devcenter_artifact_dp = CliCommandType(
        operations_tmpl=(
            'azext_devcenter.vendored_sdks.devcenter_dataplane.operations._artifacts_operations#ArtifactsOperations.{}'
        ),
        client_factory=cf_artifact_dp,
    )

    devcenter_pool_dp = CliCommandType(
    operations_tmpl='azext_devcenter.vendored_sdks.devcenter_dataplane.operations._pool_operations#PoolOperations.{}',
    client_factory=cf_pool_dp,
    )


    devcenter_project_dp = CliCommandType(
        operations_tmpl='azext_devcenter.vendored_sdks.devcenter_dataplane.operations._project_operations#ProjectOperations.{}',
        client_factory=cf_project_dp,
    )

    devcenter_dev_box_dp = CliCommandType(
        operations_tmpl=(
            'azext_devcenter.vendored_sdks.devcenter_dataplane.operations._dev_box_operations#DevBoxOperations.{}'
        ),
        client_factory=cf_dev_box_dp,
    )

    devcenter_catalog_item_dp = CliCommandType(
        operations_tmpl=(
            'azext_devcenter.vendored_sdks.devcenter_dataplane.operations._catalog_item_operations#CatalogItemOperations.{}'
        ),
        client_factory=cf_catalog_item_dp,
    )

    devcenter_catalog_item_version_dp = CliCommandType(
        operations_tmpl='azext_devcenter.vendored_sdks.devcenter_dataplane.operations._catalog_item_versions_operations#CatalogItemVersionsOperations.{}',
        client_factory=cf_catalog_item_version_dp,
    )

    devcenter_environment_dp = CliCommandType(
        operations_tmpl=(
            'azext_devcenter.vendored_sdks.devcenter_dataplane.operations._environments_operations#EnvironmentsOperations.{}'
        ),
        client_factory=cf_environment_dp,
    )


    devcenter_environment_type_dp = CliCommandType(
        operations_tmpl=(
            'azext_devcenter.vendored_sdks.devcenter_dataplane.operations._environment_type_operations#EnvironmentTypeOperations.{}'
        ),
        client_factory=cf_environment_type_dp,
    )

    devcenter_schedule_dp = CliCommandType(
        operations_tmpl=(
            'azext_devcenter.vendored_sdks.devcenter_dataplane.operations._schedule_operations#ScheduleOperations.{}'
        ),
        client_factory=cf_schedule_dp,
    )

    #control plane

    devcenter_attached_network = CliCommandType(
        operations_tmpl=(
            'azext_devcenter.vendored_sdks.devcenter.operations._attached_networks_operations#AttachedNetworksOperations.{}'
        ),
        client_factory=cf_attached_network,
    )

    devcenter_catalog = CliCommandType(
        operations_tmpl='azext_devcenter.vendored_sdks.devcenter.operations._catalogs_operations#CatalogsOperations.{}',
        client_factory=cf_catalog,
    )


    devcenter_dev_center = CliCommandType(
        operations_tmpl='azext_devcenter.vendored_sdks.devcenter.operations._dev_centers_operations#DevCentersOperations.{}',
        client_factory=cf_dev_center,
    )


    devcenter_environment_type = CliCommandType(
        operations_tmpl=(
            'azext_devcenter.vendored_sdks.devcenter.operations._environment_types_operations#EnvironmentTypesOperations.{}'
        ),
        client_factory=cf_environment_type,
    )

    devcenter_dev_box_definition = CliCommandType(
        operations_tmpl=(
            'azext_devcenter.vendored_sdks.devcenter.operations._dev_box_definitions_operations#DevBoxDefinitionsOperations.{}'
        ),
        client_factory=cf_dev_box_definition,
    )

    devcenter_gallery = CliCommandType(
        operations_tmpl='azext_devcenter.vendored_sdks.devcenter.operations._galleries_operations#GalleriesOperations.{}',
        client_factory=cf_gallery,
    )


    devcenter_image = CliCommandType(
        operations_tmpl='azext_devcenter.vendored_sdks.devcenter.operations._images_operations#ImagesOperations.{}',
        client_factory=cf_image,
    )


    devcenter_image_version = CliCommandType(
        operations_tmpl=(
            'azext_devcenter.vendored_sdks.devcenter.operations._image_versions_operations#ImageVersionsOperations.{}'
        ),
        client_factory=cf_image_version,
    )


    devcenter_network_connection = CliCommandType(
        operations_tmpl=(
            'azext_devcenter.vendored_sdks.devcenter.operations._network_connections_operations#NetworkConnectionsOperations.{}'
        ),
        client_factory=cf_network_connection,
    )


    devcenter_pool = CliCommandType(
        operations_tmpl='azext_devcenter.vendored_sdks.devcenter.operations._pools_operations#PoolsOperations.{}',
        client_factory=cf_pool,
    )


    devcenter_project = CliCommandType(
        operations_tmpl='azext_devcenter.vendored_sdks.devcenter.operations._projects_operations#ProjectsOperations.{}',
        client_factory=cf_project,
    )

    devcenter_project_environment_type = CliCommandType(
        operations_tmpl='azext_devcenter.vendored_sdks.devcenter.operations._project_environment_types_operations#ProjectEnvironmentTypesOperations.{}',
        client_factory=cf_project_environment_type,
    )

    devcenter_schedule = CliCommandType(
        operations_tmpl='azext_devcenter.vendored_sdks.devcenter.operations._schedules_operations#SchedulesOperations.{}',
        client_factory=cf_schedule,
    )

    devcenter_sku = CliCommandType(
        operations_tmpl='azext_devcenter.vendored_sdks.devcenter.operations._skus_operations#SkusOperations.{}',
        client_factory=cf_sku,
    )

    devcenter_usage = CliCommandType(
        operations_tmpl='azext_devcenter.vendored_sdks.devcenter.operations._usages_operations#UsagesOperations.{}',
        client_factory=cf_usage,
    )

    with self.command_group('devcenter dev', devcenter_project_dp):
            pass
    
    with self.command_group('devcenter admin', devcenter_project_dp):
            pass

    #data plane 
    with self.command_group('devcenter dev project', devcenter_project_dp, client_factory=cf_project_dp) as g:
        g.custom_command('list', 'devcenter_project_list_dp')
        g.custom_command('show', 'devcenter_project_show_dp')

    with self.command_group('devcenter dev pool', devcenter_pool_dp, client_factory=cf_pool_dp) as g:
        g.custom_command('list', 'devcenter_pool_list_dp')
        g.custom_show_command('show', 'devcenter_pool_show_dp')
    
    with self.command_group('devcenter dev dev-box', devcenter_dev_box_dp, client_factory=cf_dev_box_dp) as g:
        g.custom_command('list', 'devcenter_dev_box_list')
        g.custom_show_command('show', 'devcenter_dev_box_show')
        g.custom_command('create', 'devcenter_dev_box_create', supports_no_wait=True)
        g.custom_command('delete', 'devcenter_dev_box_delete', supports_no_wait=True, confirmation=True)
        g.custom_command('get-remote-connection', 'devcenter_dev_box_get_remote_connection')
        g.custom_command('start', 'devcenter_dev_box_start', supports_no_wait=True)
        g.custom_command('stop', 'devcenter_dev_box_stop', supports_no_wait=True)

    with self.command_group('devcenter dev action', devcenter_action_dp, client_factory=cf_action_dp) as g:
        g.custom_command('list', 'devcenter_action_list')
        g.custom_show_command('show', 'devcenter_action_show')
        g.custom_command('create', 'devcenter_action_create', supports_no_wait=True)
        g.custom_wait_command('wait', 'devcenter_action_show')

    with self.command_group('devcenter dev artifact', devcenter_artifact_dp, client_factory=cf_artifact_dp) as g:
        g.custom_command('list', 'devcenter_artifact_list')

    with self.command_group('devcenter dev catalog-item', devcenter_catalog_item_dp, client_factory=cf_catalog_item_dp) as g:
        g.custom_command('list', 'devcenter_catalog_item_list')
        g.custom_show_command('show', 'devcenter_catalog_item_show')

    with self.command_group(
        'devcenter dev catalog-item-version', devcenter_catalog_item_version_dp, client_factory=cf_catalog_item_version_dp
    ) as g:
        g.custom_command('list', 'devcenter_catalog_item_version_list')
        g.custom_show_command('show', 'devcenter_catalog_item_version_show')

    with self.command_group('devcenter dev environment', devcenter_environment_dp, client_factory=cf_environment_dp) as g:
        g.custom_command('list', 'devcenter_environment_list')
        g.custom_show_command('show', 'devcenter_environment_show')
        g.custom_command('create', 'devcenter_environment_create', supports_no_wait=True)
        g.custom_command('update', 'devcenter_environment_update', supports_no_wait=True)
        g.custom_command('delete', 'devcenter_environment_delete', supports_no_wait=True, confirmation=True)
        g.custom_command('list-by-project', 'devcenter_environment_list_by_project')
        g.custom_wait_command('wait', 'devcenter_environment_show')

    with self.command_group(
        'devcenter dev environment-type', devcenter_environment_type, client_factory=cf_environment_type
    ) as g:
        g.custom_command('list', 'devcenter_environment_type_list_dp')

    with self.command_group('devcenter dev schedule', devcenter_schedule, client_factory=cf_schedule) as g:
        g.custom_command('list', 'devcenter_schedule_list_dp')
        g.custom_show_command('show', 'devcenter_schedule_show_dp')


    #control plane
    with self.command_group(
        'devcenter admin attached-network', devcenter_attached_network, client_factory=cf_attached_network
    ) as g:
        g.custom_command('list', 'devcenter_attached_network_list')
        g.custom_show_command('show', 'devcenter_attached_network_show')
        g.custom_command('create', 'devcenter_attached_network_create', supports_no_wait=True)
        g.custom_command('update', 'devcenter_attached_network_update', supports_no_wait=True)
        g.custom_command('delete', 'devcenter_attached_network_delete', supports_no_wait=True, confirmation=True)
        g.custom_wait_command('wait', 'devcenter_attached_network_show')

    with self.command_group('devcenter admin catalog', devcenter_catalog, client_factory=cf_catalog) as g:
        g.custom_command('list', 'devcenter_catalog_list')
        g.custom_show_command('show', 'devcenter_catalog_show')
        g.custom_command('create', 'devcenter_catalog_create', supports_no_wait=True)
        g.custom_command('update', 'devcenter_catalog_update', supports_no_wait=True)
        g.custom_command('delete', 'devcenter_catalog_delete', supports_no_wait=True, confirmation=True)
        g.custom_command('sync', 'devcenter_catalog_sync', supports_no_wait=True)
        g.custom_wait_command('wait', 'devcenter_catalog_show')

    with self.command_group(
        'devcenter admin devbox-definition', devcenter_dev_box_definition, client_factory=cf_dev_box_definition
    ) as g:
        g.custom_command('list', 'devcenter_dev_box_definition_list')
        g.custom_show_command('show', 'devcenter_dev_box_definition_show')
        g.custom_command('create', 'devcenter_dev_box_definition_create', supports_no_wait=True)
        g.custom_command('update', 'devcenter_dev_box_definition_update', supports_no_wait=True)
        g.custom_command('delete', 'devcenter_dev_box_definition_delete', supports_no_wait=True, confirmation=True)
        g.custom_wait_command('wait', 'devcenter_dev_box_definition_show')

    with self.command_group('devcenter admin dev-center', devcenter_dev_center, client_factory=cf_dev_center) as g:
        g.custom_command('list', 'devcenter_dev_center_list')
        g.custom_show_command('show', 'devcenter_dev_center_show')
        g.custom_command('create', 'devcenter_dev_center_create', supports_no_wait=True)
        g.custom_command('update', 'devcenter_dev_center_update', supports_no_wait=True)
        g.custom_command('delete', 'devcenter_dev_center_delete', supports_no_wait=True, confirmation=True)
        g.custom_wait_command('wait', 'devcenter_dev_center_show')

    with self.command_group(
        'devcenter admin environment-type', devcenter_environment_type, client_factory=cf_environment_type
    ) as g:
        g.custom_command('list', 'devcenter_environment_type_list')
        g.custom_show_command('show', 'devcenter_environment_type_show')
        g.custom_command('create', 'devcenter_environment_type_create')
        g.custom_command('update', 'devcenter_environment_type_update')
        g.custom_command('delete', 'devcenter_environment_type_delete', supports_no_wait=True, confirmation=True)
        g.custom_wait_command('wait', 'devcenter_environment_type_show')

    with self.command_group('devcenter admin gallery', devcenter_gallery, client_factory=cf_gallery) as g:
        g.custom_command('list', 'devcenter_gallery_list')
        g.custom_show_command('show', 'devcenter_gallery_show')
        g.custom_command('create', 'devcenter_gallery_create', supports_no_wait=True)
        g.generic_update_command(
            'update',
            supports_no_wait=True,
            custom_func_name='devcenter_gallery_update',
            setter_arg_name='body',
            setter_name='begin_create_or_update',
        )
        g.custom_command('delete', 'devcenter_gallery_delete', supports_no_wait=True, confirmation=True)
        g.custom_wait_command('wait', 'devcenter_gallery_show')

    with self.command_group('devcenter admin image', devcenter_image, client_factory=cf_image) as g:
        g.custom_command('list', 'devcenter_image_list')
        g.custom_show_command('show', 'devcenter_image_show')

    with self.command_group('devcenter admin image-version', devcenter_image_version, client_factory=cf_image_version) as g:
        g.custom_command('list', 'devcenter_image_version_list')
        g.custom_show_command('show', 'devcenter_image_version_show')

    with self.command_group('devcenter admin network-connection', devcenter_network_connection, client_factory=cf_network_connection) as g:
        g.custom_command('list', 'devcenter_network_connection_list')
        g.custom_show_command('show', 'devcenter_network_connection_show')
        g.custom_command('create', 'devcenter_network_connection_create', supports_no_wait=True)
        g.custom_command('update', 'devcenter_network_connection_update', supports_no_wait=True)
        g.custom_command('delete', 'devcenter_network_connection_delete', supports_no_wait=True, confirmation=True)
        g.custom_command('show-health-detail', 'devcenter_network_connection_show_health_detail')
        g.custom_wait_command('wait', 'devcenter_network_connection_show')

    with self.command_group('devcenter admin pool', devcenter_pool, client_factory=cf_pool) as g:
        g.custom_command('list', 'devcenter_pool_list')
        g.custom_show_command('show', 'devcenter_pool_show')
        g.custom_command('create', 'devcenter_pool_create', supports_no_wait=True)
        g.custom_command('update', 'devcenter_pool_update', supports_no_wait=True)
        g.custom_command('delete', 'devcenter_pool_delete', supports_no_wait=True, confirmation=True)
        g.custom_wait_command('wait', 'devcenter_pool_show')

    with self.command_group('devcenter admin project', devcenter_project, client_factory=cf_project) as g:
        g.custom_command('list', 'devcenter_project_list')
        g.custom_show_command('show', 'devcenter_project_show')
        g.custom_command('create', 'devcenter_project_create', supports_no_wait=True)
        g.custom_command('update', 'devcenter_project_update', supports_no_wait=True)
        g.custom_command('delete', 'devcenter_project_delete', supports_no_wait=True, confirmation=True)
        g.custom_wait_command('wait', 'devcenter_project_show')

    with self.command_group(
        'devcenter admin project-environment-type',
        devcenter_project_environment_type,
        client_factory=cf_project_environment_type,
    ) as g:
        g.custom_command('list', 'devcenter_project_environment_type_list')
        g.custom_show_command('show', 'devcenter_project_environment_type_show')
        g.custom_command('create', 'devcenter_project_environment_type_create')
        g.custom_command('update', 'devcenter_project_environment_type_update')
        g.custom_command('delete', 'devcenter_project_environment_type_delete', confirmation=True)

    with self.command_group('devcenter admin schedule', devcenter_schedule, client_factory=cf_schedule) as g:
        g.custom_command('list', 'devcenter_schedule_list')
        g.custom_show_command('show', 'devcenter_schedule_show')
        g.custom_command('create', 'devcenter_schedule_create', supports_no_wait=True)
        g.custom_command('update', 'devcenter_schedule_update', supports_no_wait=True)
        g.custom_command('delete', 'devcenter_schedule_delete', supports_no_wait=True, confirmation=True)
        g.custom_wait_command('wait', 'devcenter_schedule_show')

    with self.command_group('devcenter admin sku', devcenter_sku, client_factory=cf_sku) as g:
        g.custom_command('list', 'devcenter_sku_list')

    with self.command_group('devcenter admin usage', devcenter_usage, client_factory=cf_usage) as g:
        g.custom_command('list', 'devcenter_usage_list')

    with self.command_group('devcenter', is_experimental=True):
        pass