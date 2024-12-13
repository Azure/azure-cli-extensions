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
    PlanMemberCreate,
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
    ImageDefinitionList,
    ImageDefinitionShow,
    ImageDefinitionBuildImage,
    ImageDefinitionBuildList,
    ImageDefinitionBuildShow,
    ImageDefinitionBuildCancel,
    ImageDefinitionBuildGetDetail,
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
)


def load_command_table(self, _):
    # Control plane
    self.command_table["devcenter admin image-definition list"] = (
        ImageDefinitionList(loader=self)
    )
    self.command_table["devcenter admin image-definition show"] = (
        ImageDefinitionShow(loader=self)
    )
    self.command_table["devcenter admin image-definition build-image"] = (
        ImageDefinitionBuildImage(loader=self)
    )

    self.command_table["devcenter admin image-definition-build list"] = (
        ImageDefinitionBuildList(loader=self)
    )
    self.command_table["devcenter admin image-definition-build show"] = (
        ImageDefinitionBuildShow(loader=self)
    )
    self.command_table["devcenter admin image-definition-build cancel"] = (
        ImageDefinitionBuildCancel(loader=self)
    )
    self.command_table["devcenter admin image-definition-build get-build-detail"] = (
        ImageDefinitionBuildGetDetail(loader=self)
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

    self.command_table["devcenter admin plan-member create"] = PlanMemberCreate(
        loader=self
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
    with self.command_group("devcenter dev dev-box") as g:
        g.custom_command("list", "devcenter_dev_box_list")
    