# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access
# pylint: disable=too-many-lines

from datetime import datetime
from azure.cli.core.aaz import register_callback, has_value
from azure.cli.core.azclierror import ResourceNotFoundError
from .utils import get_project_arg, get_earliest_time, get_delayed_time, get_dataplane_endpoint
from .aaz.latest.devcenter.admin.attached_network import (
    Create as _AttachedNetworkCreate,
    Delete as _AttachedNetworkDelete,
    List as _AttachedNetworkList,
    Show as _AttachedNetworkShow,
    Wait as _AttachedNetworkWait,
)
from .aaz.latest.devcenter.admin.catalog import (
    Create as _CatalogCreate,
    Delete as _CatalogDelete,
    List as _CatalogList,
    Show as _CatalogShow,
    Sync as _CatalogSync,
    Update as _CatalogUpdate,
    Wait as _CatalogWait,
    Connect as _CatalogConnect,
    GetSyncErrorDetail as _CatalogGetSyncErrorDetail,
)
from .aaz.latest.devcenter.admin.catalog_task import (
    GetErrorDetail as _CatalogTaskGetErrorDetail,
    List as _CatalogTaskList,
    Show as _CatalogTaskShow,
)
from .aaz.latest.devcenter.admin.check_name_availability import (
    Execute as _CheckNameAvailabilityExecute,
)
from .aaz.latest.devcenter.admin.check_scoped_name_availability import (
    Execute as _CheckScopedNameAvailabilityExecute,
)
from .aaz.latest.devcenter.admin.devbox_definition import (
    Create as _DevBoxDefinitionCreate,
    Delete as _DevBoxDefinitionDelete,
    List as _DevBoxDefinitionList,
    Show as _DevBoxDefinitionShow,
    Update as _DevBoxDefinitionUpdate,
    Wait as _DevBoxDefinitionWait,
)
from .aaz.latest.devcenter.admin.environment_definition import (
    List as _EnvironmentDefinitionList,
    Show as _EnvironmentDefinitionShow,
    GetErrorDetail as _EnvironmentDefinitionGetErrorDetail,
)
from .aaz.latest.devcenter.admin.environment_type import (
    Create as _EnvironmentTypeCreate,
    Delete as _EnvironmentTypeDelete,
    List as _EnvironmentTypeList,
    Show as _EnvironmentTypeShow,
    Update as _EnvironmentTypeUpdate,
)
from .aaz.latest.devcenter.admin.gallery import (
    Create as _GalleryCreate,
    Delete as _GalleryDelete,
    List as _GalleryList,
    Show as _GalleryShow,
    Wait as _GalleryWait,
)
from .aaz.latest.devcenter.admin.image import (
    List as _ImageList,
    Show as _ImageShow,
)
from .aaz.latest.devcenter.admin.image_version import (
    List as _ImageVersionList,
    Show as _ImageVersionShow,
)
from .aaz.latest.devcenter.admin.network_connection import (
    Create as _NetworkConnectionCreate,
)
from .aaz.latest.devcenter.admin.pool import (
    Create as _PoolCreate,
    Delete as _PoolDelete,
    List as _PoolList,
    Show as _PoolShow,
    Update as _PoolUpdate,
    Wait as _PoolWait,
    RunHealthCheck as _PoolRunHealthCheck,
)
from .aaz.latest.devcenter.admin.project import Create as _ProjectCreate
from .aaz.latest.devcenter.admin.project_allowed_environment_type import (
    List as _ProjectAllowedEnvironmentTypeList,
    Show as _ProjectAllowedEnvironmentTypeShow,
)
from .aaz.latest.devcenter.admin.project_catalog import (
    Create as _ProjectCatalogCreate,
    Delete as _ProjectCatalogDelete,
    List as _ProjectCatalogList,
    Show as _ProjectCatalogShow,
    Sync as _ProjectCatalogSync,
    Update as _ProjectCatalogUpdate,
    Wait as _ProjectCatalogWait,
    Connect as _ProjectCatalogConnect,
    GetSyncErrorDetail as _ProjectCatalogGetSyncErrorDetail,
)
from .aaz.latest.devcenter.admin.project_environment_definition import (
    List as _ProjectEnvironmentDefinitionList,
    Show as _ProjectEnvironmentDefinitionShow,
    GetErrorDetail as _ProjectEnvironmentDefinitionGetErrorDetail,
)
from .aaz.latest.devcenter.admin.project_environment_type import (
    Create as _ProjectEnvironmentTypeCreate,
    Delete as _ProjectEnvironmentTypeDelete,
    List as _ProjectEnvironmentTypeList,
    Show as _ProjectEnvironmentTypeShow,
    Update as _ProjectEnvironmentTypeUpdate,
)
from .aaz.latest.devcenter.admin.schedule import (
    Create as _ScheduleCreate,
    Delete as _ScheduleDelete,
    Show as _ScheduleShow,
    Update as _ScheduleUpdate,
    Wait as _ScheduleWait,
)
from .aaz.latest.devcenter.admin.project_image_definition import (
    List as _ProjectImageDefinitionList,
    Show as _ProjectImageDefinitionShow,
    BuildImage as _ProjectImageDefinitionBuildImage,
    GetErrorDetail as _ProjectImageDefinitionGetErrorDetail,
)
from .aaz.latest.devcenter.admin.project_image_definition_build import (
    List as _ProjectImageDefinitionBuildList,
    Show as _ProjectImageDefinitionBuildShow,
    Cancel as _ProjectImageDefinitionBuildCancel,
    GetBuildDetail as _ProjectImageDefinitionBuildGetDetail,
)
from .aaz.latest.devcenter.admin.project_image import (
    List as _ProjectImageList,
    Show as _ProjectImageShow,
)
from .aaz.latest.devcenter.admin.project_image_version import (
    List as _ProjectImageVersionList,
    Show as _ProjectImageVersionShow,
)
from .aaz.latest.devcenter.admin.project_policy import (
    List as _ProjectPolicyList,
    Show as _ProjectPolicyShow,
    Create as _ProjectPolicyCreate,
    Update as _ProjectPolicyUpdate,
    Delete as _ProjectPolicyDelete,
    Wait as _ProjectPolicyWait,
)
from .aaz.latest.devcenter.admin.project_sku import (
    List as _ProjectSkuList,
)
from .aaz.latest.devcenter.dev.project import (
    List as ProjectListDp,
    Show as ProjectShowDp,
    ListAbilities as ProjectListAbilitiesDp,
    ShowOperation as ProjectShowOperationDp,
)
from .aaz.latest.devcenter.dev.pool import (
    List as PoolListDp,
    Show as PoolShowDp,
)
from .aaz.latest.devcenter.dev.schedule import (
    List as ScheduleListDp,
    Show as ScheduleShowDp,
)
from .aaz.latest.devcenter.dev.dev_box import (
    CaptureSnapshot as DevBoxCaptureSnapshot,
    Create as DevBoxCreate,
    DelayAction as DevBoxDelayAction,
    DelayAllActions as DevBoxDelayAllActions,
    Delete as DevBoxDelete,
    ListAction as DevBoxListAction,
    ListAll as DevBoxListAll,
    ListOperation as DevBoxListOperation,
    ListSnapshot as DevBoxListSnapshot,
    List as DevBoxList,
    Repair as DevBoxRepair,
    Restart as DevBoxRestart,
    RestoreSnapshot as DevBoxRestoreSnapshot,
    ShowAction as DevBoxShowAction,
    ShowOperation as DevBoxShowOperation,
    ShowRemoteConnection as DevBoxShowRemoteConnection,
    ShowSnapshot as DevBoxShowSnapshot,
    Show as DevBoxShow,
    SkipAction as DevBoxSkipAction,
    Start as DevBoxStart,
    Stop as DevBoxStop,
    Align as DevBoxAlign,
    Approve as DevBoxApprove,
    SetActiveHours as DevBoxSetActiveHours,
)
from .aaz.latest.devcenter.dev.environment import (
    Create as EnvironmentCreate,
    DelayAction as EnvironmentDelayAction,
    Delete as EnvironmentDelete,
    ListAction as EnvironmentListAction,
    ListOperation as EnvironmentListOperation,
    List as EnvironmentList,
    ShowAction as EnvironmentShowAction,
    ShowLogsByOperation as EnvironmentShowLogsByOperation,
    ShowOperation as EnvironmentShowOperation,
    ShowOutputs as EnvironmentShowOutputs,
    Show as EnvironmentShow,
    SkipAction as EnvironmentSkipAction,
    UpdateExpirationDate as EnvironmentUpdateExpirationDate,
)
from .aaz.latest.devcenter.dev.catalog import (
    List as CatalogListDp,
    Show as CatalogShowDp,
)
from .aaz.latest.devcenter.dev.environment_definition import (
    List as EnvironmentDefinitionListDp,
    Show as EnvironmentDefinitionShowDp,
)
from .aaz.latest.devcenter.dev.environment_type import (
    List as EnvironmentTypeListDp,
    Show as EnvironmentTypeShowDp,
    ListAbilities as EnvironmentTypeListAbilitiesDp,
)
from .aaz.latest.devcenter.dev.image_build import (
    ShowLog as ImageBuildShowLogDp,
)
from .aaz.latest.devcenter.dev.customization_group import (
    Create as CustomizationGroupCreate,
    List as CustomizationGroupList,
    Show as CustomizationGroupShow,
)
from .aaz.latest.devcenter.dev.customization_task import (
    List as CustomizationTaskList,
    ShowLogs as CustomizationTaskShowLogs,
    Show as CustomizationTaskShow,
    Validate as CustomizationTaskValidate,
)
from .aaz.latest.devcenter.dev.approval import (
    List as ApprovalList
)
from .aaz.latest.devcenter.dev.add_on import (
    Create as AddOnCreate,
    Delete as AddOnDelete,
    Disable as AddOnDisable,
    Enable as AddOnEnable,
    List as AddOnList,
    Show as AddOnShow,
)
from ._validators import (
    validate_attached_network_or_dev_box_def,
    validate_env_name_already_exists,
    validate_repo_git,
    validate_pool_create,
)

# Control plane


def set_configured_defaults(args):
    for arg_name, arg in args:
        if arg_name == "project_name":
            arg.configured_default = "project"
        if arg_name == "dev_center_name":
            arg.configured_default = "dev-center"
    return args


class ProjectSkuList(_ProjectSkuList):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectPolicyList(_ProjectPolicyList):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectPolicyShow(_ProjectPolicyShow):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectPolicyCreate(_ProjectPolicyCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.resource_policies._required = True
        return args_schema

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectPolicyUpdate(_ProjectPolicyUpdate):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectPolicyDelete(_ProjectPolicyDelete):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectPolicyWait(_ProjectPolicyWait):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectImageList(_ProjectImageList):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectImageShow(_ProjectImageShow):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectImageVersionList(_ProjectImageVersionList):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectImageVersionShow(_ProjectImageVersionShow):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectImageDefinitionBuildList(_ProjectImageDefinitionBuildList):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectImageDefinitionBuildShow(_ProjectImageDefinitionBuildShow):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectImageDefinitionBuildCancel(_ProjectImageDefinitionBuildCancel):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectImageDefinitionBuildGetDetail(_ProjectImageDefinitionBuildGetDetail):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectImageDefinitionList(_ProjectImageDefinitionList):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectImageDefinitionShow(_ProjectImageDefinitionShow):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectImageDefinitionBuildImage(_ProjectImageDefinitionBuildImage):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectImageDefinitionGetErrorDetail(_ProjectImageDefinitionGetErrorDetail):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class AttachedNetworkCreate(_AttachedNetworkCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.network_connection_id._required = True
        return args_schema

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class AttachedNetworkDelete(_AttachedNetworkDelete):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class AttachedNetworkList(_AttachedNetworkList):
    @register_callback
    def pre_operations(self):
        validate_attached_network_or_dev_box_def(
            self.ctx.args.dev_center_name, self.ctx.args.project_name
        )

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class AttachedNetworkShow(_AttachedNetworkShow):
    @register_callback
    def pre_operations(self):
        validate_attached_network_or_dev_box_def(
            self.ctx.args.dev_center_name, self.ctx.args.project_name
        )

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class AttachedNetworkWait(_AttachedNetworkWait):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class CheckNameAvailabilityExecute(_CheckNameAvailabilityExecute):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.name._required = True
        args_schema.type._required = True
        return args_schema


class CheckScopedNameAvailabilityExecute(_CheckScopedNameAvailabilityExecute):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.name._required = True
        args_schema.type._required = True
        args_schema.scope._required = True
        return args_schema


class CatalogCreate(_CatalogCreate):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)

    @register_callback
    def pre_operations(self):
        validate_repo_git(self.ctx.args.ado_git, self.ctx.args.git_hub)


class CatalogDelete(_CatalogDelete):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class CatalogList(_CatalogList):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class CatalogShow(_CatalogShow):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class CatalogSync(_CatalogSync):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class CatalogUpdate(_CatalogUpdate):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class CatalogWait(_CatalogWait):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class CatalogConnect(_CatalogConnect):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class CatalogGetSyncErrorDetail(_CatalogGetSyncErrorDetail):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class CatalogTaskGetErrorDetail(_CatalogTaskGetErrorDetail):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class CatalogTaskList(_CatalogTaskList):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class CatalogTaskShow(_CatalogTaskShow):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class DevBoxDefinitionCreate(_DevBoxDefinitionCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.image_reference._required = True
        args_schema.sku._required = True
        args_schema.os_storage_type._required = True
        return args_schema

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class DevBoxDefinitionDelete(_DevBoxDefinitionDelete):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class DevBoxDefinitionList(_DevBoxDefinitionList):
    @register_callback
    def pre_operations(self):
        validate_attached_network_or_dev_box_def(
            self.ctx.args.dev_center_name, self.ctx.args.project_name
        )

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class DevBoxDefinitionShow(_DevBoxDefinitionShow):
    @register_callback
    def pre_operations(self):
        validate_attached_network_or_dev_box_def(
            self.ctx.args.dev_center_name, self.ctx.args.project_name
        )

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class DevBoxDefinitionUpdate(_DevBoxDefinitionUpdate):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class DevBoxDefinitionWait(_DevBoxDefinitionWait):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class EnvironmentDefinitionGetErrorDetail(_EnvironmentDefinitionGetErrorDetail):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class EnvironmentDefinitionList(_EnvironmentDefinitionList):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class EnvironmentDefinitionShow(_EnvironmentDefinitionShow):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class EnvironmentTypeCreate(_EnvironmentTypeCreate):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class EnvironmentTypeDelete(_EnvironmentTypeDelete):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class EnvironmentTypeList(_EnvironmentTypeList):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class EnvironmentTypeShow(_EnvironmentTypeShow):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class EnvironmentTypeUpdate(_EnvironmentTypeUpdate):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class GalleryCreate(_GalleryCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.gallery_resource_id._required = True
        return args_schema

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class GalleryDelete(_GalleryDelete):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class GalleryList(_GalleryList):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class GalleryShow(_GalleryShow):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class GalleryWait(_GalleryWait):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ImageList(_ImageList):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ImageShow(_ImageShow):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ImageVersionList(_ImageVersionList):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ImageVersionShow(_ImageVersionShow):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class NetworkConnectionCreate(_NetworkConnectionCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.subnet_id._required = True
        args_schema.domain_join_type._required = True
        return args_schema


class PoolCreate(_PoolCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.license_type._registered = False
        args_schema.local_administrator._required = True
        return args_schema

    @register_callback
    def pre_operations(self):
        args = self.ctx.args
        args.license_type = "Windows_Client"
        if args.virtual_network_type == "Managed" and not has_value(
            args.network_connection_name
        ):
            args.network_connection_name = "managedNetwork"
        if args.devbox_definition_type == "Value" and has_value(
            args.devbox_definition_image_reference.id
        ):
            args.devbox_definition_name = str(args.devbox_definition_image_reference.id).rstrip('/').rsplit('/', 1)[-1]
        validate_pool_create(
            args.virtual_network_type,
            args.network_connection_name,
            args.managed_virtual_network_regions,
            args.devbox_definition_image_reference,
            args.devbox_definition_sku,
            args.devbox_definition_type,
            args.devbox_definition_name
        )

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class PoolDelete(_PoolDelete):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class PoolList(_PoolList):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class PoolRunHealthCheck(_PoolRunHealthCheck):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class PoolShow(_PoolShow):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class PoolUpdate(_PoolUpdate):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class PoolWait(_PoolWait):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectCreate(_ProjectCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.dev_center_id._required = True
        return args_schema


class ProjectAllowedEnvironmentTypeList(_ProjectAllowedEnvironmentTypeList):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectAllowedEnvironmentTypeShow(_ProjectAllowedEnvironmentTypeShow):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectCatalogCreate(_ProjectCatalogCreate):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)

    @register_callback
    def pre_operations(self):
        validate_repo_git(self.ctx.args.ado_git, self.ctx.args.git_hub)


class ProjectCatalogDelete(_ProjectCatalogDelete):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectCatalogList(_ProjectCatalogList):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectCatalogShow(_ProjectCatalogShow):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectCatalogSync(_ProjectCatalogSync):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectCatalogUpdate(_ProjectCatalogUpdate):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectCatalogWait(_ProjectCatalogWait):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectCatalogConnect(_ProjectCatalogConnect):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectCatalogGetSyncErrorDetail(_ProjectCatalogGetSyncErrorDetail):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectEnvironmentDefinitionGetErrorDetail(
    _ProjectEnvironmentDefinitionGetErrorDetail
):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectEnvironmentDefinitionList(_ProjectEnvironmentDefinitionList):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectEnvironmentDefinitionShow(_ProjectEnvironmentDefinitionShow):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectEnvironmentTypeCreate(_ProjectEnvironmentTypeCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.deployment_target_id._required = True
        args_schema.status._required = True
        args_schema.roles._required = True
        args_schema.identity_type._required = True
        return args_schema

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectEnvironmentTypeDelete(_ProjectEnvironmentTypeDelete):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectEnvironmentTypeList(_ProjectEnvironmentTypeList):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectEnvironmentTypeShow(_ProjectEnvironmentTypeShow):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectEnvironmentTypeUpdate(_ProjectEnvironmentTypeUpdate):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ScheduleCreate(_ScheduleCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.schedule_name._registered = False
        args_schema.schedule_name._required = False
        args_schema.frequency._registered = False
        args_schema.type._registered = False
        args_schema.time_zone._required = True
        args_schema.time._required = True
        return args_schema

    @register_callback
    def pre_operations(self):
        args = self.ctx.args
        args.schedule_name = "default"
        args.frequency = "Daily"
        args.type = "StopDevBox"

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ScheduleDelete(_ScheduleDelete):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.schedule_name._registered = False
        args_schema.schedule_name._required = False
        return args_schema

    @register_callback
    def pre_operations(self):
        args = self.ctx.args
        args.schedule_name = "default"

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ScheduleShow(_ScheduleShow):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.schedule_name._registered = False
        args_schema.schedule_name._required = False
        return args_schema

    @register_callback
    def pre_operations(self):
        args = self.ctx.args
        args.schedule_name = "default"

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ScheduleUpdate(_ScheduleUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.schedule_name._registered = False
        args_schema.schedule_name._required = False
        return args_schema

    @register_callback
    def pre_operations(self):
        args = self.ctx.args
        args.schedule_name = "default"

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ScheduleWait(_ScheduleWait):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.schedule_name._registered = False
        args_schema.schedule_name._required = False
        return args_schema

    @register_callback
    def pre_operations(self):
        args = self.ctx.args
        args.schedule_name = "default"

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


# Data plane

def devcenter_project_list(cmd, dev_center=None, endpoint=None):
    if dev_center is not None and endpoint is None:
        resource_graph_data = get_project_arg(cmd.cli_ctx, dev_center)
        if len(resource_graph_data) == 0:
            return []

    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return ProjectListDp(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
    })


def devcenter_project_show(cmd, project_name, dev_center=None, endpoint=None):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return ProjectShowDp(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "name": project_name
    })


def devcenter_project_list_abilities(cmd, project_name, user_id="me", dev_center=None, endpoint=None):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return ProjectListAbilitiesDp(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "name": project_name,
        "user_id": user_id
    })


def devcenter_project_show_operation(cmd, project_name, operation_id, dev_center=None, endpoint=None):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return ProjectShowOperationDp(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "name": project_name,
        "operation_id": operation_id
    })


def devcenter_pool_list(cmd, project_name, dev_center=None, endpoint=None):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return PoolListDp(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name
    })


def devcenter_pool_show(
    cmd, project_name, pool_name, dev_center=None, endpoint=None
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return PoolShowDp(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "pool_name": pool_name
    })


def devcenter_schedule_list(
    cmd, project_name, pool_name=None, dev_center=None, endpoint=None
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return ScheduleListDp(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "pool_name": pool_name
    })


def devcenter_schedule_show(
    cmd, pool_name, project_name, dev_center=None, endpoint=None
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return ScheduleShowDp(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "pool_name": pool_name,
        "schedule_name": "default"
    })


def devcenter_dev_box_list(cmd, dev_center=None, endpoint=None, project_name=None, user_id=None):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    if user_id is not None:
        return DevBoxList(cli_ctx=cmd.cli_ctx)(command_args={
            "endpoint": updated_endpoint,
            "user_id": user_id,
            "project_name": project_name
        })
    return DevBoxListAll(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint
    })


def devcenter_dev_box_show(
    cmd, dev_box_name, project_name, dev_center=None, endpoint=None, user_id="me"
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return DevBoxShow(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name
    })


def devcenter_dev_box_create(
    cmd,
    dev_box_name,
    pool_name,
    project_name,
    user_id="me",
    no_wait=False,
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return DevBoxCreate(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "pool_name": pool_name,
        "no_wait": no_wait,
    })


def devcenter_dev_box_delete(
    cmd,
    dev_box_name,
    project_name,
    user_id="me",
    no_wait=False,
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return DevBoxDelete(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "no_wait": no_wait
    })


def devcenter_dev_box_start(
    cmd,
    project_name,
    dev_box_name,
    user_id="me",
    no_wait=False,
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return DevBoxStart(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "no_wait": no_wait
    })


def devcenter_dev_box_stop(
    cmd,
    dev_box_name,
    project_name,
    no_wait=False,
    hibernate=None,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return DevBoxStop(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "hibernate": hibernate,
        "no_wait": no_wait
    })


def devcenter_dev_box_align(
    cmd,
    project_name,
    dev_box_name,
    user_id="me",
    no_wait=False,
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return DevBoxAlign(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "no_wait": no_wait,
        "targets": ["NetworkProperties"]
    })


def devcenter_dev_box_approve(
    cmd,
    project_name,
    dev_box_name,
    user_id,
    no_wait=False,
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return DevBoxApprove(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "no_wait": no_wait
    })


def devcenter_dev_box_set_active_hours(
    cmd,
    project_name,
    dev_box_name,
    end_time_hour,
    start_time_hour,
    time_zone,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return DevBoxSetActiveHours(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "end_time_hour": end_time_hour,
        "start_time_hour": start_time_hour,
        "time_zone": time_zone
    })


def devcenter_dev_box_restart(
    cmd,
    project_name,
    dev_box_name,
    user_id="me",
    no_wait=False,
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return DevBoxRestart(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "no_wait": no_wait
    })


def devcenter_dev_box_repair(
    cmd,
    project_name,
    dev_box_name,
    user_id="me",
    no_wait=False,
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return DevBoxRepair(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "no_wait": no_wait
    })


def devcenter_dev_box_get_remote_connection(
    cmd, project_name, dev_box_name, user_id="me", dev_center=None, endpoint=None
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return DevBoxShowRemoteConnection(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name
    })


def devcenter_dev_box_list_action(
    cmd, project_name, dev_box_name, user_id="me", dev_center=None, endpoint=None
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return DevBoxListAction(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name
    })


def devcenter_dev_box_show_action(
    cmd,
    project_name,
    dev_box_name,
    action_name,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return DevBoxShowAction(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "action_name": action_name
    })


def devcenter_dev_box_skip_action(
    cmd,
    project_name,
    dev_box_name,
    action_name,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return DevBoxSkipAction(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "action_name": action_name
    })


def devcenter_dev_box_delay_action(
    cmd,
    project_name,
    dev_box_name,
    delay_time,
    action_name,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)

    upcoming_action = DevBoxShowAction(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "action_name": action_name
    })

    upcoming_action_time = upcoming_action.get("next", {}).get("scheduledTime")
    if not upcoming_action_time:
        raise ResourceNotFoundError("There are no upcoming scheduled times for this action.")
    action_time = datetime.strptime(upcoming_action_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    delayed_time = get_delayed_time(delay_time, action_time)

    return DevBoxDelayAction(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "action_name": action_name,
        "until": delayed_time
    })


def devcenter_dev_box_delay_all_actions(
    cmd,
    project_name,
    dev_box_name,
    delay_time,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    actions = DevBoxListAction(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name
    })

    earliest_time = get_earliest_time(actions)
    if earliest_time is None:
        raise ResourceNotFoundError("There are no scheduled actions for this dev box.")

    delayed_time = get_delayed_time(delay_time, earliest_time)
    return DevBoxDelayAllActions(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "until": delayed_time
    })


def devcenter_dev_box_list_operation(
    cmd, project_name, dev_box_name, user_id="me", dev_center=None, endpoint=None
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return DevBoxListOperation(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name
    })


def devcenter_dev_box_show_operation(
    cmd,
    project_name,
    dev_box_name,
    operation_id,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return DevBoxShowOperation(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "operation_id": operation_id
    })


def devcenter_dev_box_capture_snapshot(
    cmd,
    project_name,
    dev_box_name,
    user_id="me",
    no_wait=False,
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return DevBoxCaptureSnapshot(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "no_wait": no_wait
    })


def devcenter_dev_box_restore_snapshot(
    cmd,
    project_name,
    dev_box_name,
    snapshot_id,
    user_id="me",
    no_wait=False,
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return DevBoxRestoreSnapshot(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "snapshot_id": snapshot_id,
        "no_wait": no_wait
    })


def devcenter_dev_box_show_snapshot(
    cmd,
    project_name,
    dev_box_name,
    snapshot_id,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return DevBoxShowSnapshot(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "snapshot_id": snapshot_id,
    })


def devcenter_dev_box_list_snapshot(
    cmd,
    project_name,
    dev_box_name,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return DevBoxListSnapshot(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
    })


def devcenter_environment_list(
    cmd, project_name, user_id=None, dev_center=None, endpoint=None
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return EnvironmentList(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id
    })


def devcenter_environment_show(
    cmd, project_name, environment_name, user_id="me", dev_center=None, endpoint=None
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return EnvironmentShow(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "environment_name": environment_name
    })


def devcenter_environment_create(
    cmd,
    environment_name,
    environment_type,
    project_name,
    catalog_name,
    environment_definition_name,
    expiration_date=None,
    parameters=None,
    no_wait=False,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)

    environments_iterator = EnvironmentList(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id
    })

    validate_env_name_already_exists(
        environments_iterator, environment_name, user_id, project_name
    )

    return EnvironmentCreate(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "environment_name": environment_name,
        "environment_type": environment_type,
        "catalog_name": catalog_name,
        "environment_definition_name": environment_definition_name,
        "expiration_date": expiration_date,
        "parameters": parameters,
        "no_wait": no_wait
    })


def devcenter_environment_update(
    cmd,
    environment_name,
    project_name,
    parameters=None,
    no_wait=False,
    user_id="me",
    dev_center=None,
    endpoint=None,
    expiration_date=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    environment = EnvironmentShow(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "environment_name": environment_name
    })
    environment_type = environment["environmentType"]
    catalog_name = environment["catalogName"]
    environment_definition_name = environment["environmentDefinitionName"]

    return EnvironmentCreate(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "environment_name": environment_name,
        "environment_type": environment_type,
        "catalog_name": catalog_name,
        "environment_definition_name": environment_definition_name,
        "expiration_date": expiration_date,
        "parameters": parameters,
        "no_wait": no_wait
    })


def devcenter_environment_delete(
    cmd,
    environment_name,
    project_name,
    no_wait=False,
    user_id="me",
    force=None,
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return EnvironmentDelete(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "environment_name": environment_name,
        "no_wait": no_wait,
        "force": force
    })


def devcenter_environment_operation_list(
    cmd, project_name, environment_name, user_id="me", dev_center=None, endpoint=None
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return EnvironmentListOperation(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "environment_name": environment_name
    })


def devcenter_environment_operation_show(
    cmd,
    project_name,
    environment_name,
    operation_id,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return EnvironmentShowOperation(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "operation_id": operation_id,
        "user_id": user_id,
        "environment_name": environment_name
    })


def devcenter_environment_show_logs_by_operation(
    cmd,
    project_name,
    environment_name,
    operation_id,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    logs = EnvironmentShowLogsByOperation(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "operation_id": operation_id,
        "user_id": user_id,
        "environment_name": environment_name
    })

    print(logs)


def devcenter_environment_show_action(
    cmd,
    project_name,
    environment_name,
    action_name,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return EnvironmentShowAction(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "environment_name": environment_name,
        "action_name": action_name
    })


def devcenter_environment_list_action(
    cmd, project_name, environment_name, user_id="me", dev_center=None, endpoint=None
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return EnvironmentListAction(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "environment_name": environment_name
    })


def devcenter_environment_delay_action(
    cmd,
    project_name,
    environment_name,
    action_name,
    delay_time,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    upcoming_action = EnvironmentShowAction(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "environment_name": environment_name,
        "action_name": action_name
    })

    upcoming_action_time = upcoming_action.get("next", {}).get("scheduledTime")
    if not upcoming_action_time:
        raise ResourceNotFoundError("There are no upcoming scheduled times for this action.")
    action_time = datetime.strptime(upcoming_action_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    delayed_time = get_delayed_time(delay_time, action_time)

    return EnvironmentDelayAction(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "environment_name": environment_name,
        "action_name": action_name,
        "until": delayed_time
    })


def devcenter_environment_skip_action(
    cmd,
    project_name,
    environment_name,
    action_name,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return EnvironmentSkipAction(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "environment_name": environment_name,
        "action_name": action_name
    })


def devcenter_environment_show_outputs(
    cmd, project_name, environment_name, user_id="me", dev_center=None, endpoint=None
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return EnvironmentShowOutputs(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "environment_name": environment_name
    })


def devcenter_environment_update_expiration(
    cmd,
    project_name,
    environment_name,
    user_id="me",
    dev_center=None,
    endpoint=None,
    expiration_date=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return EnvironmentUpdateExpirationDate(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "environment_name": environment_name,
        "expiration_date": expiration_date
    })


def devcenter_catalog_list(cmd, project_name, dev_center=None, endpoint=None):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return CatalogListDp(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name
    })


def devcenter_catalog_show(
    cmd, project_name, catalog_name, dev_center=None, endpoint=None
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return CatalogShowDp(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "catalog_name": catalog_name
    })


def devcenter_environment_definition_list(
    cmd, project_name, dev_center=None, endpoint=None, catalog_name=None
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return EnvironmentDefinitionListDp(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "catalog_name": catalog_name
    })


def devcenter_environment_definition_show(
    cmd, catalog_name, definition_name, project_name, dev_center=None, endpoint=None
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return EnvironmentDefinitionShowDp(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "catalog_name": catalog_name,
        "definition_name": definition_name
    })


def devcenter_environment_type_list(
    cmd, project_name, dev_center=None, endpoint=None
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return EnvironmentTypeListDp(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name
    })


def devcenter_environment_type_show(
    cmd, project_name, environment_type_name, dev_center=None, endpoint=None
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return EnvironmentTypeShowDp(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "environment_type_name": environment_type_name
    })


def devcenter_environment_type_list_abilities(
    cmd, project_name, environment_type_name, user_id="me", dev_center=None, endpoint=None
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return EnvironmentTypeListAbilitiesDp(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "environment_type_name": environment_type_name,
        "user_id": user_id
    })


def devcenter_image_build_show_log(cmd, project_name, image_build_log_id, dev_center=None, endpoint=None):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return ImageBuildShowLogDp(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "image_build_log_id": image_build_log_id
    })


def devcenter_customization_group_create(
    cmd,
    project_name,
    dev_box_name,
    customization_group_name,
    user_id="me",
    tasks=None,
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)

    return CustomizationGroupCreate(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "dev_box_name": dev_box_name,
        "customization_group_name": customization_group_name,
        "user_id": user_id,
        "tasks": tasks
    })


def devcenter_customization_group_show(
    cmd,
    project_name,
    dev_box_name,
    customization_group_name,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return CustomizationGroupShow(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "dev_box_name": dev_box_name,
        "customization_group_name": customization_group_name,
        "user_id": user_id
    })


def devcenter_customization_group_list(
    cmd,
    project_name,
    dev_box_name,
    user_id="me",
    include_tasks=None,
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)

    include = None
    if include_tasks:
        include = "tasks"

    return CustomizationGroupList(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "dev_box_name": dev_box_name,
        "user_id": user_id,
        "include": include
    })


def devcenter_customization_task_show(
    cmd,
    project_name,
    catalog_name,
    task_name,
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return CustomizationTaskShow(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "catalog_name": catalog_name,
        "task_name": task_name
    })


def devcenter_customization_task_list(
    cmd,
    project_name,
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return CustomizationTaskList(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name
    })


def devcenter_customization_task_validate(
    cmd,
    project_name,
    tasks,
    no_wait=False,
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return CustomizationTaskValidate(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "tasks": tasks,
        "no_wait": no_wait
    })


def devcenter_customization_task_log_show(
    cmd,
    project_name,
    dev_box_name,
    customization_group_name,
    customization_task_id,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return CustomizationTaskShowLogs(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "dev_box_name": dev_box_name,
        "customization_group_name": customization_group_name,
        "customization_task_id": customization_task_id,
        "user_id": user_id
    })


def devcenter_approval_list(
    cmd,
    project_name,
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return ApprovalList(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
    })


def devcenter_add_on_create(
    cmd,
    dev_box_name,
    project_name,
    add_on_name,
    hosting_resource_name="Default",
    user_id="me",
    no_wait=False,
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return AddOnCreate(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "no_wait": no_wait,
        "add_on_name": add_on_name,
        "dev_box_tunnel": {
            "hosting_resource_name": hosting_resource_name,
        }
    })


def devcenter_add_on_delete(
    cmd,
    dev_box_name,
    project_name,
    add_on_name,
    user_id="me",
    no_wait=False,
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return AddOnDelete(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "no_wait": no_wait,
        "add_on_name": add_on_name
    })


def devcenter_add_on_disable(
    cmd,
    dev_box_name,
    project_name,
    add_on_name,
    user_id="me",
    no_wait=False,
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return AddOnDisable(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "no_wait": no_wait,
        "add_on_name": add_on_name
    })


def devcenter_add_on_enable(
    cmd,
    dev_box_name,
    project_name,
    add_on_name,
    user_id="me",
    no_wait=False,
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return AddOnEnable(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "no_wait": no_wait,
        "add_on_name": add_on_name
    })


def devcenter_add_on_show(
    cmd,
    dev_box_name,
    project_name,
    add_on_name,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return AddOnShow(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
        "add_on_name": add_on_name
    })


def devcenter_add_on_list(
    cmd,
    dev_box_name,
    project_name,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return AddOnList(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint,
        "project_name": project_name,
        "user_id": user_id,
        "dev_box_name": dev_box_name,
    })
