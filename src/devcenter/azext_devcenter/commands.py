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
)
from .custom import (
    AttachedNetworkCreate,
    AttachedNetworkDelete,
    AttachedNetworkList,
    AttachedNetworkShow,
    AttachedNetworkWait,
    CatalogCreate,
    CatalogDelete,
    CatalogList,
    CatalogShow,
    CatalogSync,
    CatalogUpdate,
    CatalogWait,
    DevBoxDefinitionCreate,
    DevBoxDefinitionDelete,
    DevBoxDefinitionList,
    DevBoxDefinitionShow,
    DevBoxDefinitionUpdate,
    DevBoxDefinitionWait,
    EnvironmentTypeCreate,
    EnvironmentTypeDelete,
    EnvironmentTypeList,
    EnvironmentTypeShow,
    EnvironmentTypeUpdate,
    GalleryCreate,
    GalleryDelete,
    GalleryList,
    GalleryShow,
    GalleryWait,
    ImageList,
    ImageShow,
    ImageVersionList,
    ImageVersionShow,
    PoolCreate,
    PoolDelete,
    PoolList,
    PoolShow,
    PoolUpdate,
    PoolWait,
    ProjectAllowedEnvironmentTypeList,
    ProjectAllowedEnvironmentTypeShow,
    ProjectEnvironmentTypeCreate,
    ProjectEnvironmentTypeDelete,
    ProjectEnvironmentTypeList,
    ProjectEnvironmentTypeShow,
    ProjectEnvironmentTypeUpdate,
    ScheduleCreate,
    ScheduleDelete,
    ScheduleShow,
    ScheduleUpdate,
    ScheduleWait,
)


def load_command_table(self, _):
    # Control plane
    self.command_table[
        "devcenter admin attached-network create"
    ] = AttachedNetworkCreate(loader=self)
    self.command_table[
        "devcenter admin attached-network delete"
    ] = AttachedNetworkDelete(loader=self)
    self.command_table["devcenter admin attached-network list"] = AttachedNetworkList(
        loader=self
    )
    self.command_table["devcenter admin attached-network show"] = AttachedNetworkShow(
        loader=self
    )
    self.command_table["devcenter admin attached-network wait"] = AttachedNetworkWait(
        loader=self
    )

    self.command_table["devcenter admin catalog create"] = CatalogCreate(loader=self)
    self.command_table["devcenter admin catalog delete"] = CatalogDelete(loader=self)
    self.command_table["devcenter admin catalog list"] = CatalogList(loader=self)
    self.command_table["devcenter admin catalog show"] = CatalogShow(loader=self)
    self.command_table["devcenter admin catalog sync"] = CatalogSync(loader=self)
    self.command_table["devcenter admin catalog update"] = CatalogUpdate(loader=self)
    self.command_table["devcenter admin catalog wait"] = CatalogWait(loader=self)

    self.command_table[
        "devcenter admin devbox-definition create"
    ] = DevBoxDefinitionCreate(loader=self)
    self.command_table[
        "devcenter admin devbox-definition delete"
    ] = DevBoxDefinitionDelete(loader=self)
    self.command_table["devcenter admin devbox-definition list"] = DevBoxDefinitionList(
        loader=self
    )
    self.command_table["devcenter admin devbox-definition show"] = DevBoxDefinitionShow(
        loader=self
    )
    self.command_table[
        "devcenter admin devbox-definition update"
    ] = DevBoxDefinitionUpdate(loader=self)
    self.command_table["devcenter admin devbox-definition wait"] = DevBoxDefinitionWait(
        loader=self
    )

    self.command_table[
        "devcenter admin environment-type create"
    ] = EnvironmentTypeCreate(loader=self)
    self.command_table[
        "devcenter admin environment-type delete"
    ] = EnvironmentTypeDelete(loader=self)
    self.command_table["devcenter admin environment-type list"] = EnvironmentTypeList(
        loader=self
    )
    self.command_table["devcenter admin environment-type show"] = EnvironmentTypeShow(
        loader=self
    )
    self.command_table[
        "devcenter admin environment-type update"
    ] = EnvironmentTypeUpdate(loader=self)

    self.command_table["devcenter admin gallery create"] = GalleryCreate(loader=self)
    self.command_table["devcenter admin gallery delete"] = GalleryDelete(loader=self)
    self.command_table["devcenter admin gallery list"] = GalleryList(loader=self)
    self.command_table["devcenter admin gallery show"] = GalleryShow(loader=self)
    self.command_table["devcenter admin gallery wait"] = GalleryWait(loader=self)

    self.command_table["devcenter admin image list"] = ImageList(loader=self)
    self.command_table["devcenter admin image show"] = ImageShow(loader=self)

    self.command_table["devcenter admin image-version list"] = ImageVersionList(
        loader=self
    )
    self.command_table["devcenter admin image-version show"] = ImageVersionShow(
        loader=self
    )

    self.command_table["devcenter admin pool create"] = PoolCreate(loader=self)
    self.command_table["devcenter admin pool delete"] = PoolDelete(loader=self)
    self.command_table["devcenter admin pool list"] = PoolList(loader=self)
    self.command_table["devcenter admin pool show"] = PoolShow(loader=self)
    self.command_table["devcenter admin pool update"] = PoolUpdate(loader=self)
    self.command_table["devcenter admin pool wait"] = PoolWait(loader=self)

    self.command_table[
        "devcenter admin project-allowed-environment-type list"
    ] = ProjectAllowedEnvironmentTypeList(loader=self)
    self.command_table[
        "devcenter admin project-allowed-environment-type show"
    ] = ProjectAllowedEnvironmentTypeShow(loader=self)

    self.command_table[
        "devcenter admin project-environment-type create"
    ] = ProjectEnvironmentTypeCreate(loader=self)
    self.command_table[
        "devcenter admin project-environment-type delete"
    ] = ProjectEnvironmentTypeDelete(loader=self)
    self.command_table[
        "devcenter admin project-environment-type list"
    ] = ProjectEnvironmentTypeList(loader=self)
    self.command_table[
        "devcenter admin project-environment-type show"
    ] = ProjectEnvironmentTypeShow(loader=self)
    self.command_table[
        "devcenter admin project-environment-type update"
    ] = ProjectEnvironmentTypeUpdate(loader=self)

    self.command_table["devcenter admin schedule create"] = ScheduleCreate(loader=self)
    self.command_table["devcenter admin schedule delete"] = ScheduleDelete(loader=self)
    self.command_table["devcenter admin schedule show"] = ScheduleShow(loader=self)
    self.command_table["devcenter admin schedule update"] = ScheduleUpdate(loader=self)
    self.command_table["devcenter admin schedule wait"] = ScheduleWait(loader=self)

    # Data plane

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

    with self.command_group("devcenter", is_preview=True):
        pass

    with self.command_group("devcenter dev"):
        pass

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
