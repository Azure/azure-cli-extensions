# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
from .custom import (
    AttachedNetworkCreate,
    AttachedNetworkDelete,
    AttachedNetworkList,
    AttachedNetworkShow,
    AttachedNetworkWait,
    CheckNameAvailabilityExecute,
    CheckScopedNameAvailabilityExecute,
    CatalogConnect,
    CatalogCreate,
    CatalogDelete,
    CatalogList,
    CatalogShow,
    CatalogSync,
    CatalogUpdate,
    CatalogWait,
    CatalogGetSyncErrorDetail,
    CatalogTaskGetErrorDetail,
    CatalogTaskList,
    CatalogTaskShow,
    DevBoxDefinitionCreate,
    DevBoxDefinitionDelete,
    DevBoxDefinitionList,
    DevBoxDefinitionShow,
    DevBoxDefinitionUpdate,
    DevBoxDefinitionWait,
    EnvironmentDefinitionGetErrorDetail,
    EnvironmentDefinitionList,
    EnvironmentDefinitionShow,
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
    NetworkConnectionCreate,
    PoolCreate,
    PoolDelete,
    PoolList,
    PoolShow,
    PoolUpdate,
    PoolWait,
    ProjectCreate,
    ProjectAllowedEnvironmentTypeList,
    ProjectAllowedEnvironmentTypeShow,
    ProjectCatalogConnect,
    ProjectCatalogCreate,
    ProjectCatalogDelete,
    ProjectCatalogList,
    ProjectCatalogShow,
    ProjectCatalogSync,
    ProjectCatalogUpdate,
    ProjectCatalogWait,
    ProjectCatalogGetSyncErrorDetail,
    ProjectEnvironmentDefinitionGetErrorDetail,
    ProjectEnvironmentDefinitionList,
    ProjectEnvironmentDefinitionShow,
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
    ProjectImageList,
    ProjectImageShow,
    ProjectImageVersionList,
    ProjectImageVersionShow,
    ProjectPolicyList,
    ProjectPolicyShow,
    ProjectPolicyCreate,
    ProjectPolicyUpdate,
    ProjectPolicyDelete,
    ProjectPolicyWait,
    ProjectSkuList,
    ProjectImageDefinitionList,
    ProjectImageDefinitionShow,
    ProjectImageDefinitionBuildImage,
    ProjectImageDefinitionGetErrorDetail,
    ProjectImageDefinitionBuildList,
    ProjectImageDefinitionBuildShow,
    ProjectImageDefinitionBuildCancel,
    ProjectImageDefinitionBuildGetDetail,
)


def load_command_table(self, _):
    # Control plane
    self.command_table["devcenter admin project-image-definition list"] = (
        ProjectImageDefinitionList(loader=self)
    )
    self.command_table["devcenter admin project-image-definition get-error-detail"] = (
        ProjectImageDefinitionGetErrorDetail(loader=self)
    )
    self.command_table["devcenter admin project-image-definition show"] = (
        ProjectImageDefinitionShow(loader=self)
    )
    self.command_table["devcenter admin project-image-definition build-image"] = (
        ProjectImageDefinitionBuildImage(loader=self)
    )

    self.command_table["devcenter admin project-image-definition-build list"] = (
        ProjectImageDefinitionBuildList(loader=self)
    )
    self.command_table["devcenter admin project-image-definition-build show"] = (
        ProjectImageDefinitionBuildShow(loader=self)
    )
    self.command_table["devcenter admin project-image-definition-build cancel"] = (
        ProjectImageDefinitionBuildCancel(loader=self)
    )
    self.command_table["devcenter admin project-image-definition-build get-build-detail"] = (
        ProjectImageDefinitionBuildGetDetail(loader=self)
    )

    self.command_table["devcenter admin project-image list"] = (
        ProjectImageList(loader=self)
    )
    self.command_table["devcenter admin project-image show"] = (
        ProjectImageShow(loader=self)
    )

    self.command_table["devcenter admin project-image-version list"] = (
        ProjectImageVersionList(loader=self)
    )
    self.command_table["devcenter admin project-image-version show"] = (
        ProjectImageVersionShow(loader=self)
    )

    self.command_table["devcenter admin project-policy create"] = (
        ProjectPolicyCreate(loader=self)
    )
    self.command_table["devcenter admin project-policy delete"] = (
        ProjectPolicyDelete(loader=self)
    )
    self.command_table["devcenter admin project-policy list"] = (
        ProjectPolicyList(loader=self)
    )
    self.command_table["devcenter admin project-policy show"] = (
        ProjectPolicyShow(loader=self)
    )
    self.command_table["devcenter admin project-policy update"] = (
        ProjectPolicyUpdate(loader=self)
    )
    self.command_table["devcenter admin project-policy wait"] = (
        ProjectPolicyWait(loader=self)
    )

    self.command_table["devcenter admin project-sku list"] = (
        ProjectSkuList(loader=self)
    )

    self.command_table["devcenter admin attached-network create"] = (
        AttachedNetworkCreate(loader=self)
    )
    self.command_table["devcenter admin attached-network delete"] = (
        AttachedNetworkDelete(loader=self)
    )
    self.command_table["devcenter admin attached-network list"] = AttachedNetworkList(
        loader=self
    )
    self.command_table["devcenter admin attached-network show"] = AttachedNetworkShow(
        loader=self
    )
    self.command_table["devcenter admin attached-network wait"] = AttachedNetworkWait(
        loader=self
    )

    self.command_table["devcenter admin check-name-availability execute"] = (
        CheckNameAvailabilityExecute(loader=self)
    )

    self.command_table["devcenter admin check-scoped-name-availability execute"] = (
        CheckScopedNameAvailabilityExecute(loader=self)
    )

    self.command_table["devcenter admin catalog create"] = CatalogCreate(loader=self)
    self.command_table["devcenter admin catalog delete"] = CatalogDelete(loader=self)
    self.command_table["devcenter admin catalog list"] = CatalogList(loader=self)
    self.command_table["devcenter admin catalog show"] = CatalogShow(loader=self)
    self.command_table["devcenter admin catalog sync"] = CatalogSync(loader=self)
    self.command_table["devcenter admin catalog update"] = CatalogUpdate(loader=self)
    self.command_table["devcenter admin catalog wait"] = CatalogWait(loader=self)
    self.command_table["devcenter admin catalog connect"] = CatalogConnect(loader=self)
    self.command_table["devcenter admin catalog get-sync-error-detail"] = (
        CatalogGetSyncErrorDetail(loader=self)
    )

    self.command_table["devcenter admin catalog-task get-error-detail"] = (
        CatalogTaskGetErrorDetail(loader=self)
    )
    self.command_table["devcenter admin catalog-task list"] = CatalogTaskList(
        loader=self
    )
    self.command_table["devcenter admin catalog-task show"] = CatalogTaskShow(
        loader=self
    )

    self.command_table["devcenter admin environment-definition get-error-detail"] = (
        EnvironmentDefinitionGetErrorDetail(loader=self)
    )
    self.command_table["devcenter admin environment-definition list"] = (
        EnvironmentDefinitionList(loader=self)
    )
    self.command_table["devcenter admin environment-definition show"] = (
        EnvironmentDefinitionShow(loader=self)
    )

    self.command_table["devcenter admin devbox-definition create"] = (
        DevBoxDefinitionCreate(loader=self)
    )
    self.command_table["devcenter admin devbox-definition delete"] = (
        DevBoxDefinitionDelete(loader=self)
    )
    self.command_table["devcenter admin devbox-definition list"] = DevBoxDefinitionList(
        loader=self
    )
    self.command_table["devcenter admin devbox-definition show"] = DevBoxDefinitionShow(
        loader=self
    )
    self.command_table["devcenter admin devbox-definition update"] = (
        DevBoxDefinitionUpdate(loader=self)
    )
    self.command_table["devcenter admin devbox-definition wait"] = DevBoxDefinitionWait(
        loader=self
    )

    self.command_table["devcenter admin environment-type create"] = (
        EnvironmentTypeCreate(loader=self)
    )
    self.command_table["devcenter admin environment-type delete"] = (
        EnvironmentTypeDelete(loader=self)
    )
    self.command_table["devcenter admin environment-type list"] = EnvironmentTypeList(
        loader=self
    )
    self.command_table["devcenter admin environment-type show"] = EnvironmentTypeShow(
        loader=self
    )
    self.command_table["devcenter admin environment-type update"] = (
        EnvironmentTypeUpdate(loader=self)
    )

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

    self.command_table["devcenter admin network-connection create"] = (
        NetworkConnectionCreate(loader=self)
    )

    self.command_table["devcenter admin pool create"] = PoolCreate(loader=self)
    self.command_table["devcenter admin pool delete"] = PoolDelete(loader=self)
    self.command_table["devcenter admin pool list"] = PoolList(loader=self)
    self.command_table["devcenter admin pool show"] = PoolShow(loader=self)
    self.command_table["devcenter admin pool update"] = PoolUpdate(loader=self)
    self.command_table["devcenter admin pool wait"] = PoolWait(loader=self)

    self.command_table["devcenter admin project create"] = ProjectCreate(loader=self)

    self.command_table["devcenter admin project-allowed-environment-type list"] = (
        ProjectAllowedEnvironmentTypeList(loader=self)
    )
    self.command_table["devcenter admin project-allowed-environment-type show"] = (
        ProjectAllowedEnvironmentTypeShow(loader=self)
    )

    self.command_table["devcenter admin project-catalog create"] = ProjectCatalogCreate(
        loader=self
    )
    self.command_table["devcenter admin project-catalog delete"] = ProjectCatalogDelete(
        loader=self
    )
    self.command_table["devcenter admin project-catalog list"] = ProjectCatalogList(
        loader=self
    )
    self.command_table["devcenter admin project-catalog show"] = ProjectCatalogShow(
        loader=self
    )
    self.command_table["devcenter admin project-catalog sync"] = ProjectCatalogSync(
        loader=self
    )
    self.command_table["devcenter admin project-catalog update"] = ProjectCatalogUpdate(
        loader=self
    )
    self.command_table["devcenter admin project-catalog wait"] = ProjectCatalogWait(
        loader=self
    )
    self.command_table["devcenter admin project-catalog connect"] = (
        ProjectCatalogConnect(loader=self)
    )
    self.command_table["devcenter admin project-catalog get-sync-error-detail"] = (
        ProjectCatalogGetSyncErrorDetail(loader=self)
    )

    self.command_table[
        "devcenter admin project-environment-definition get-error-detail"
    ] = ProjectEnvironmentDefinitionGetErrorDetail(loader=self)
    self.command_table["devcenter admin project-environment-definition list"] = (
        ProjectEnvironmentDefinitionList(loader=self)
    )
    self.command_table["devcenter admin project-environment-definition show"] = (
        ProjectEnvironmentDefinitionShow(loader=self)
    )

    self.command_table["devcenter admin project-environment-type create"] = (
        ProjectEnvironmentTypeCreate(loader=self)
    )
    self.command_table["devcenter admin project-environment-type delete"] = (
        ProjectEnvironmentTypeDelete(loader=self)
    )
    self.command_table["devcenter admin project-environment-type list"] = (
        ProjectEnvironmentTypeList(loader=self)
    )
    self.command_table["devcenter admin project-environment-type show"] = (
        ProjectEnvironmentTypeShow(loader=self)
    )
    self.command_table["devcenter admin project-environment-type update"] = (
        ProjectEnvironmentTypeUpdate(loader=self)
    )

    self.command_table["devcenter admin schedule create"] = ScheduleCreate(loader=self)
    self.command_table["devcenter admin schedule delete"] = ScheduleDelete(loader=self)
    self.command_table["devcenter admin schedule show"] = ScheduleShow(loader=self)
    self.command_table["devcenter admin schedule update"] = ScheduleUpdate(loader=self)
    self.command_table["devcenter admin schedule wait"] = ScheduleWait(loader=self)

# Data plane

    with self.command_group("devcenter dev project") as g:
        g.custom_command("list", "devcenter_project_list")
        g.custom_show_command("show", "devcenter_project_show")
        g.custom_command("list-abilities", "devcenter_project_list_abilities")
        g.custom_command("show-operation", "devcenter_project_show_operation")

    with self.command_group("devcenter dev approval") as g:
        g.custom_command("list", "devcenter_approval_list")

    with self.command_group("devcenter dev pool") as g:
        g.custom_command("list", "devcenter_pool_list")
        g.custom_show_command("show", "devcenter_pool_show")

    with self.command_group("devcenter dev schedule") as g:
        g.custom_command("list", "devcenter_schedule_list")
        g.custom_show_command("show", "devcenter_schedule_show")

    with self.command_group("devcenter dev dev-box") as g:
        g.custom_command("list", "devcenter_dev_box_list")
        g.custom_show_command("show", "devcenter_dev_box_show")
        g.custom_command("create", "devcenter_dev_box_create", supports_no_wait=True)
        g.custom_command(
            "delete",
            "devcenter_dev_box_delete",
            supports_no_wait=True,
            confirmation=True,
        )
        g.custom_command("start", "devcenter_dev_box_start", supports_no_wait=True)
        g.custom_command("stop", "devcenter_dev_box_stop", supports_no_wait=True)
        g.custom_command("restart", "devcenter_dev_box_restart", supports_no_wait=True)
        g.custom_command("repair", "devcenter_dev_box_repair", supports_no_wait=True)
        g.custom_command(
            "show-remote-connection", "devcenter_dev_box_get_remote_connection"
        )
        g.custom_command("list-action", "devcenter_dev_box_list_action")
        g.custom_command("show-action", "devcenter_dev_box_show_action")
        g.custom_command("skip-action", "devcenter_dev_box_skip_action")
        g.custom_command("delay-action", "devcenter_dev_box_delay_action")
        g.custom_command("delay-all-actions", "devcenter_dev_box_delay_all_actions")
        g.custom_command("list-operation", "devcenter_dev_box_list_operation")
        g.custom_command("show-operation", "devcenter_dev_box_show_operation")
        g.custom_command("capture-snapshot", "devcenter_dev_box_capture_snapshot", supports_no_wait=True)
        g.custom_command("restore-snapshot", "devcenter_dev_box_restore_snapshot", supports_no_wait=True)
        g.custom_command("show-snapshot", "devcenter_dev_box_show_snapshot")
        g.custom_command("list-snapshot", "devcenter_dev_box_list_snapshot")
        g.custom_command("align", "devcenter_dev_box_align", supports_no_wait=True)
        g.custom_command("approve", "devcenter_dev_box_approve", supports_no_wait=True)
        g.custom_command("set-active-hours", "devcenter_dev_box_set_active_hours")

    with self.command_group("devcenter dev environment") as g:
        g.custom_command("list", "devcenter_environment_list")
        g.custom_show_command("show", "devcenter_environment_show")
        g.custom_command(
            "create", "devcenter_environment_create", supports_no_wait=True
        )
        g.custom_command(
            "update", "devcenter_environment_update", supports_no_wait=True
        )
        g.custom_command(
            "deploy", "devcenter_environment_update", supports_no_wait=True
        )
        g.custom_command(
            "delete",
            "devcenter_environment_delete",
            supports_no_wait=True,
            confirmation=True,
        )
        g.custom_command("list-operation", "devcenter_environment_operation_list")
        g.custom_command("show-operation", "devcenter_environment_operation_show")
        g.custom_command(
            "show-logs-by-operation",
            "devcenter_environment_show_logs_by_operation",
        )
        g.custom_command("show-action", "devcenter_environment_show_action")
        g.custom_command("list-action", "devcenter_environment_list_action")
        g.custom_command("delay-action", "devcenter_environment_delay_action")
        g.custom_command("skip-action", "devcenter_environment_skip_action")
        g.custom_command("show-outputs", "devcenter_environment_show_outputs")
        g.custom_command(
            "update-expiration-date",
            "devcenter_environment_update_expiration",
        )

    with self.command_group("devcenter dev catalog") as g:
        g.custom_command("list", "devcenter_catalog_list")
        g.custom_show_command("show", "devcenter_catalog_show")

    with self.command_group(
        "devcenter dev environment-definition"
    ) as g:
        g.custom_command("list", "devcenter_environment_definition_list")
        g.custom_show_command("show", "devcenter_environment_definition_show")

    with self.command_group("devcenter dev environment-type") as g:
        g.custom_command("list", "devcenter_environment_type_list")
        g.custom_show_command("show", "devcenter_environment_type_show")
        g.custom_command("list-abilities", "devcenter_environment_type_list_abilities")

    with self.command_group("devcenter dev image-build") as g:
        g.custom_command("show-log", "devcenter_image_build_show_log")

    with self.command_group("devcenter dev customization-group") as g:
        g.custom_command("list", "devcenter_customization_group_list")
        g.custom_show_command("show", "devcenter_customization_group_show")
        g.custom_command("create", "devcenter_customization_group_create")

    with self.command_group("devcenter dev customization-task") as g:
        g.custom_command("list", "devcenter_customization_task_list")
        g.custom_show_command("show", "devcenter_customization_task_show")
        g.custom_command("validate", "devcenter_customization_task_validate", supports_no_wait=True)
        g.custom_command("show-logs", "devcenter_customization_task_log_show")

    with self.command_group("devcenter dev add-on") as g:
        g.custom_command("create", "devcenter_add_on_create", supports_no_wait=True)
        g.custom_command("delete", "devcenter_add_on_delete", supports_no_wait=True)
        g.custom_command("disable", "devcenter_add_on_disable", supports_no_wait=True)
        g.custom_command("enable", "devcenter_add_on_enable", supports_no_wait=True)
        g.custom_command("list", "devcenter_add_on_list")
        g.custom_show_command("show", "devcenter_add_on_show")
