# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access
# pylint: disable=too-many-lines

from datetime import datetime
import json
from azure.cli.core.aaz import has_value
from azure.cli.core.aaz import register_callback
from azure.cli.core.azclierror import ResourceNotFoundError
from azure.cli.core.util import sdk_no_wait
from .utils import get_project_arg, get_earliest_time, get_delayed_time
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
from .aaz.latest.devcenter.admin.plan_member import Create as _PlanMemberCreate
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
from .aaz.latest.devcenter.admin.image_definition import (
    List as _ImageDefinitionList,
    Show as _ImageDefinitionShow,
    BuildImage as _ImageDefinitionBuildImage,
)
from .aaz.latest.devcenter.admin.image_definition_build import (
    List as _ImageDefinitionBuildList,
    Show as _ImageDefinitionBuildShow,
    Cancel as _ImageDefinitionBuildCancel,
    GetBuildDetail as _ImageDefinitionBuildGetDetail,
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
from .aaz.latest.devcenter.dev.dev_box import (
    ListAll as _DevBoxListAll,
    List as _DevBoxList,
)
from .aaz.latest.devcenter.dev.project import (
    List as _ProjectListDp,
    Show as _ProjectShowDp,
    ListAbilities as _ProjectListAbilitiesDp,
    ShowOperation as _ProjectShowOperationDp,
)
from .aaz.latest.devcenter.dev.pool import (
    List as _PoolListDp,
    Show as _PoolShowDp,
)
from .aaz.latest.devcenter.dev.schedule import (
    List as _ScheduleListDp,
    Show as _ScheduleShowDp,
)
from .utils import get_project_data
from ._validators import validate_endpoint

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


class ImageDefinitionBuildList(_ImageDefinitionBuildList):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ImageDefinitionBuildShow(_ImageDefinitionBuildShow):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ImageDefinitionBuildCancel(_ImageDefinitionBuildCancel):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ImageDefinitionBuildGetDetail(_ImageDefinitionBuildGetDetail):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ImageDefinitionList(_ImageDefinitionList):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ImageDefinitionShow(_ImageDefinitionShow):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ImageDefinitionBuildImage(_ImageDefinitionBuildImage):
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


class PlanMemberCreate(_PlanMemberCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.member_id._required = True
        args_schema.member_type._required = True
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


def get_dataplane_endpoint(cli_ctx, endpoint=None, dev_center=None, project_name=None):
    validate_endpoint(endpoint, dev_center)

    if endpoint is None and dev_center is not None:
        project = get_project_data(cli_ctx, dev_center, project_name)
        endpoint = project["devCenterUri"]
    endpoint = endpoint.split('//', 1)[-1]

    return endpoint


def devcenter_project_list(cmd, dev_center=None, endpoint=None):
    if dev_center is not None and endpoint is None:
        resource_graph_data = get_project_arg(cmd.cli_ctx, dev_center)
        if len(resource_graph_data) == 0:
            return []
    
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)
    return _ProjectListDp(cli_ctx=cmd.cli_ctx)(command_args={
            "endpoint": updated_endpoint,
        })


def devcenter_project_show(cmd, project_name, dev_center=None, endpoint=None):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)

    return _ProjectShowDp(cli_ctx=cmd.cli_ctx)(command_args={
            "endpoint": updated_endpoint,
            "name": project_name
        })

def devcenter_project_list_abilities(cmd, project_name,  user_id="me", dev_center=None, endpoint=None):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)

    return _ProjectListAbilitiesDp(cli_ctx=cmd.cli_ctx)(command_args={
            "endpoint": updated_endpoint,
            "name": project_name,
            "user_id": user_id
        })

def devcenter_project_show_operation(cmd, project_name, operation_id, dev_center=None, endpoint=None):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)

    return _ProjectShowOperationDp(cli_ctx=cmd.cli_ctx)(command_args={
            "endpoint": updated_endpoint,
            "name": project_name,
            "operation_id": operation_id
        })

def devcenter_pool_list(cmd, project_name, dev_center=None, endpoint=None):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)

    return _PoolListDp(cli_ctx=cmd.cli_ctx)(command_args={
            "endpoint": updated_endpoint,
            "project_name": project_name
        })

def devcenter_pool_show(
    cmd, project_name, pool_name, dev_center=None, endpoint=None
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)

    return _PoolShowDp(cli_ctx=cmd.cli_ctx)(command_args={
            "endpoint": updated_endpoint,
            "project_name": project_name,
            "pool_name": pool_name
        })

def devcenter_schedule_list(
    cmd, project_name, pool_name=None, dev_center=None, endpoint=None
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)

    return _ScheduleListDp(cli_ctx=cmd.cli_ctx)(command_args={
            "endpoint": updated_endpoint,
            "project_name": project_name,
            "pool_name": pool_name
        })

def devcenter_schedule_show(
    cmd, pool_name, project_name, dev_center=None, endpoint=None
):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)

    return _ScheduleShowDp(cli_ctx=cmd.cli_ctx)(command_args={
            "endpoint": updated_endpoint,
            "project_name": project_name,
            "pool_name": pool_name,
            "schedule_name": "default"
        })


def devcenter_dev_box_list(cmd, dev_center=None, endpoint=None, project_name=None, user_id=None):
    updated_endpoint = get_dataplane_endpoint(cmd.cli_ctx, endpoint, dev_center)

    if user_id is not None:
        return _DevBoxList(cli_ctx=cmd.cli_ctx)(command_args={
            "endpoint": updated_endpoint,
            "user_id": user_id,
            "project_name": project_name
        })
    return _DevBoxListAll(cli_ctx=cmd.cli_ctx)(command_args={
        "endpoint": updated_endpoint
    })
