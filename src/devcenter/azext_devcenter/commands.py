# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
from azure.cli.core.commands import CliCommandType

from azext_devcenter._client_factory import (
    cf_project_dp,
    cf_pool_dp,
    cf_schedule_dp,
    cf_dev_box_dp,
    cf_environment_dp,
    cf_catalog_item_dp,
    cf_catalog_item_version_dp,
    cf_environment_type_dp,
    cf_notification_setting_dp,
    cf_dev_center,
    cf_project,
    cf_attached_network,
    cf_gallery,
    cf_image,
    cf_image_version,
    cf_catalog,
    cf_environment_type,
    cf_project_allowed_environment_type,
    cf_project_environment_type,
    cf_dev_box_definition,
    cf_operation_statuses,
    cf_sku,
    cf_pool,
    cf_schedule,
    cf_network_connection,
    cf_check_name_availability,
)


def load_command_table(self, _):

    # data plane

    devcenter_pool_dp = CliCommandType(
        operations_tmpl="azext_devcenter.vendored_sdks.devcenter_dataplane.operations._pool_operations#PoolOperations.{}",
        client_factory=cf_pool_dp,
    )

    devcenter_project_dp = CliCommandType(
        operations_tmpl="azext_devcenter.vendored_sdks.devcenter_dataplane.operations._project_operations#ProjectOperations.{}",
        client_factory=cf_project_dp,
    )

    devcenter_dev_box_dp = CliCommandType(
        operations_tmpl=(
            "azext_devcenter.vendored_sdks.devcenter_dataplane.operations._dev_box_operations#DevBoxOperations.{}"
        ),
        client_factory=cf_dev_box_dp,
    )

    devcenter_catalog_item_dp = CliCommandType(
        operations_tmpl=(
            "azext_devcenter.vendored_sdks.devcenter_dataplane.operations._catalog_item_operations#CatalogItemOperations.{}"
        ),
        client_factory=cf_catalog_item_dp,
    )

    devcenter_catalog_item_version_dp = CliCommandType(
        operations_tmpl="azext_devcenter.vendored_sdks.devcenter_dataplane.operations._catalog_item_versions_operations#CatalogItemVersionsOperations.{}",
        client_factory=cf_catalog_item_version_dp,
    )

    devcenter_environment_dp = CliCommandType(
        operations_tmpl=(
            "azext_devcenter.vendored_sdks.devcenter_dataplane.operations._environments_operations#EnvironmentsOperations.{}"
        ),
        client_factory=cf_environment_dp,
    )

    devcenter_environment_type_dp = CliCommandType(
        operations_tmpl=(
            "azext_devcenter.vendored_sdks.devcenter_dataplane.operations._environment_type_operations#EnvironmentTypeOperations.{}"
        ),
        client_factory=cf_environment_type_dp,
    )

    devcenter_schedule_dp = CliCommandType(
        operations_tmpl=(
            "azext_devcenter.vendored_sdks.devcenter_dataplane.operations._schedule_operations#ScheduleOperations.{}"
        ),
        client_factory=cf_schedule_dp,
    )

    devcenter_notification_setting_dp = CliCommandType(
        operations_tmpl=(
            "azext_devcenter.vendored_sdks.devcenter_dataplane.operations._notification_setting_operations#NotificationSettingOperations.{}"
        ),
        client_factory=cf_notification_setting_dp,
    )

    # control plane

    devcenter_attached_network = CliCommandType(
        operations_tmpl=(
            "azext_devcenter.vendored_sdks.devcenter.operations._attached_networks_operations#AttachedNetworksOperations.{}"
        ),
        client_factory=cf_attached_network,
    )

    devcenter_catalog = CliCommandType(
        operations_tmpl="azext_devcenter.vendored_sdks.devcenter.operations._catalogs_operations#CatalogsOperations.{}",
        client_factory=cf_catalog,
    )

    devcenter_dev_box_definition = CliCommandType(
        operations_tmpl="azext_devcenter.vendored_sdks.devcenter.operations._dev_box_definitions_operations#DevBoxDefinitionsOperations.{}",
        client_factory=cf_dev_box_definition,
    )

    devcenter_dev_center = CliCommandType(
        operations_tmpl=(
            "azext_devcenter.vendored_sdks.devcenter.operations._dev_centers_operations#DevCentersOperations.{}"
        ),
        client_factory=cf_dev_center,
    )

    devcenter_environment_type = CliCommandType(
        operations_tmpl=(
            "azext_devcenter.vendored_sdks.devcenter.operations._environment_types_operations#EnvironmentTypesOperations.{}"
        ),
        client_factory=cf_environment_type,
    )

    devcenter_gallery = CliCommandType(
        operations_tmpl="azext_devcenter.vendored_sdks.devcenter.operations._galleries_operations#GalleriesOperations.{}",
        client_factory=cf_gallery,
    )

    devcenter_image = CliCommandType(
        operations_tmpl="azext_devcenter.vendored_sdks.devcenter.operations._images_operations#ImagesOperations.{}",
        client_factory=cf_image,
    )

    devcenter_image_version = CliCommandType(
        operations_tmpl=(
            "azext_devcenter.vendored_sdks.devcenter.operations._image_versions_operations#ImageVersionsOperations.{}"
        ),
        client_factory=cf_image_version,
    )

    devcenter_network_connection = CliCommandType(
        operations_tmpl="azext_devcenter.vendored_sdks.devcenter.operations._network_connections_operations#NetworkConnectionsOperations.{}",
        client_factory=cf_network_connection,
    )

    devcenter_operation_statuses = CliCommandType(
        operations_tmpl="azext_devcenter.vendored_sdks.devcenter.operations._operation_statuses_operations#OperationStatusesOperations.{}",
        client_factory=cf_operation_statuses,
    )

    devcenter_pool = CliCommandType(
        operations_tmpl="azext_devcenter.vendored_sdks.devcenter.operations._pools_operations#PoolsOperations.{}",
        client_factory=cf_pool,
    )

    devcenter_project = CliCommandType(
        operations_tmpl="azext_devcenter.vendored_sdks.devcenter.operations._projects_operations#ProjectsOperations.{}",
        client_factory=cf_project,
    )

    devcenter_project_allowed_environment_type = CliCommandType(
        operations_tmpl="azext_devcenter.vendored_sdks.devcenter.operations._project_allowed_environment_types_operations#ProjectAllowedEnvironmentTypesOperations.{}",
        client_factory=cf_project_allowed_environment_type,
    )

    devcenter_project_environment_type = CliCommandType(
        operations_tmpl="azext_devcenter.vendored_sdks.devcenter.operations._project_environment_types_operations#ProjectEnvironmentTypesOperations.{}",
        client_factory=cf_project_environment_type,
    )

    devcenter_schedule = CliCommandType(
        operations_tmpl="azext_devcenter.vendored_sdks.devcenter.operations._schedules_operations#SchedulesOperations.{}",
        client_factory=cf_schedule,
    )

    devcenter_sku = CliCommandType(
        operations_tmpl="azext_devcenter.vendored_sdks.devcenter.operations._skus_operations#SkusOperations.{}",
        client_factory=cf_sku,
    )

    devcenter_check_name_availability = CliCommandType(
        operations_tmpl="azext_devcenter.vendored_sdks.devcenter.operations._check_name_availability_operations#CheckNameAvailabilityOperations.{}",
        client_factory=cf_check_name_availability,
    )

    with self.command_group("devcenter", is_preview=True):
        pass

    with self.command_group("devcenter dev"):
        pass

    # data plane
    with self.command_group("devcenter dev project", devcenter_project_dp) as g:
        g.custom_command("list", "devcenter_project_list_dp")
        g.custom_show_command("show", "devcenter_project_show_dp")

    with self.command_group("devcenter dev pool", devcenter_pool_dp) as g:
        g.custom_command("list", "devcenter_pool_list_dp")
        g.custom_show_command("show", "devcenter_pool_show_dp")

    with self.command_group("devcenter dev dev-box", devcenter_dev_box_dp) as g:
        g.custom_command("list", "devcenter_dev_box_list")
        g.custom_show_command("show", "devcenter_dev_box_show")
        g.custom_command("create", "devcenter_dev_box_create", supports_no_wait=True)
        g.custom_command(
            "delete",
            "devcenter_dev_box_delete",
            supports_no_wait=True,
            confirmation=True,
        )
        g.custom_command(
            "show-remote-connection", "devcenter_dev_box_get_remote_connection"
        )
        g.custom_command("start", "devcenter_dev_box_start", supports_no_wait=True)
        g.custom_command("stop", "devcenter_dev_box_stop", supports_no_wait=True)
        g.custom_command(
            "delay-upcoming-action", "devcenter_dev_box_delay_upcoming_action"
        )
        g.custom_command(
            "list-upcoming-action", "devcenter_dev_box_list_upcoming_action"
        )
        g.custom_command(
            "show-upcoming-action", "devcenter_dev_box_show_upcoming_action"
        )
        g.custom_command(
            "skip-upcoming-action", "devcenter_dev_box_skip_upcoming_action"
        )

    with self.command_group(
        "devcenter dev catalog-item", devcenter_catalog_item_dp
    ) as g:
        g.custom_command("list", "devcenter_catalog_item_list")
        g.custom_show_command("show", "devcenter_catalog_item_show")

    with self.command_group(
        "devcenter dev catalog-item-version", devcenter_catalog_item_version_dp
    ) as g:
        g.custom_command("list", "devcenter_catalog_item_version_list")
        g.custom_show_command("show", "devcenter_catalog_item_version_show")

    with self.command_group("devcenter dev environment", devcenter_environment_dp) as g:
        g.custom_command("list", "devcenter_environment_list")
        g.custom_show_command("show", "devcenter_environment_show")
        g.custom_command(
            "create", "devcenter_environment_create", supports_no_wait=True
        )
        g.custom_command("update", "devcenter_environment_update")
        g.custom_command(
            "delete",
            "devcenter_environment_delete",
            supports_no_wait=True,
            confirmation=True,
        )
        g.custom_command(
            "deploy-action",
            "devcenter_environment_deploy_action",
            supports_no_wait=True,
        )
        g.custom_wait_command("wait", "devcenter_environment_show")

    with self.command_group(
        "devcenter dev environment-type", devcenter_environment_type_dp
    ) as g:
        g.custom_command("list", "devcenter_environment_type_list_dp")

    with self.command_group("devcenter dev schedule", devcenter_schedule_dp) as g:
        g.custom_command("list", "devcenter_schedule_list_dp")
        g.custom_show_command("show", "devcenter_schedule_show_dp")

    with self.command_group(
        "devcenter dev notification-setting", devcenter_notification_setting_dp
    ) as g:
        g.custom_command(
            "list-allowed-culture",
            "devcenter_notification_setting_list_allowed_culture_dp",
        )
        g.custom_show_command("show", "devcenter_notification_setting_show_dp")
        g.custom_command(
            "create", "devcenter_notification_setting_create_dp", supports_no_wait=True
        )
