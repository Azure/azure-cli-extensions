# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from datetime import timedelta
from azure.cli.core.util import sdk_no_wait
from ._client_factory import cf_devcenter_dataplane
from .data_plane_endpoint_helper import get_project_arg
from .aaz.latest.devcenter.admin.attached_network import (
    Create as _AttachedNetworkCreate,
    Delete as _AttachedNetworkDelete,
    List as _AttachedNetworkList,
    ListProject as AttachedNetworkListByProject,
    Show as _AttachedNetworkShow,
    ShowProject as AttachedNetworkShowByProject,
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
)
from .aaz.latest.devcenter.admin.devbox_definition import (
    Create as _DevBoxDefinitionCreate,
    Delete as _DevBoxDefinitionDelete,
    List as _DevBoxDefinitionList,
    ListProject as DevBoxDefinitionListByProject,
    Show as _DevBoxDefinitionShow,
    ShowProject as DevBoxDefinitionShowByProject,
    Update as _DevBoxDefinitionUpdate,
    Wait as _DevBoxDefinitionWait,
)
from .aaz.latest.devcenter.admin.devcenter import List as _DevCenterList
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
    ListGallery as _ImageListByGallery,
    List as _ImageList,
    Show as _ImageShow,
)
from .aaz.latest.devcenter.admin.image_verion import (
    List as _ImageVersionList,
    Show as _ImageVersionShow,
)
from .aaz.latest.devcenter.admin.network_connection import (
    List as _NetworkConnectionList,
    ListHealthDetail as _NetworkConnectionListHealthDetail,
)
from .aaz.latest.devcenter.admin.pool import (
    Create as _PoolCreate,
    Delete as _PoolDelete,
    List as _PoolList,
    Show as _PoolShow,
    Update as _PoolUpdate,
    Wait as _PoolWait,
)
from .aaz.latest.devcenter.admin.project import List as _ProjectList
from .aaz.latest.devcenter.admin.project_allowed_environment_type import (
    List as _ProjectAllowedEnvironmentTypeList,
    Show as _ProjectAllowedEnvironmentTypeShow,
)
from .aaz.latest.devcenter.admin.environment_type import (
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
from .aaz.latest.devcenter.admin.sku import List as _SkuList

from azure.cli.core.aaz import *
from ._validators import validate_attached_network_or_dev_box_def

# Control plane


def set_configured_defaults(args):
    for arg_name, arg in args:
        if arg_name == "project_name":
            arg.configured_default = "project"
        if arg_name == "dev_center_name":
            arg.configured_default = "dev-center"
    return args


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
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.dev_center_name._required = False
        args_schema.project_name = AAZStrArg(
            options=["--project", "--project-name"],
            help="The name of the project. Use az configure -d project=<project_name> to configure a default.",
        )
        args_schema.top._registered = False
        return args_schema

    def _execute_operations(self):
        self.pre_operations()
        condition_0 = has_value(self.ctx.args.dev_center_name)
        condition_1 = has_value(self.ctx.args.project_name)
        if condition_0:
            self.AttachedNetworksListByDevCenter(ctx=self.ctx)()
        elif condition_1:
            AttachedNetworkListByProject.AttachedNetworksListByProject(ctx=self.ctx)()

    @register_callback
    def pre_operations(self):
        validate_attached_network_or_dev_box_def(
            self.ctx.args.dev_center_name, self.ctx.args.project_name
        )
        pass

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class AttachedNetworkShow(_AttachedNetworkShow):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.dev_center_name._required = False
        args_schema.project_name = AAZStrArg(
            options=["--project", "--project-name"],
            help="The name of the project. Use az configure -d project=<project_name> to configure a default.",
        )
        return args_schema

    def _execute_operations(self):
        self.pre_operations()
        condition_0 = has_value(self.ctx.args.dev_center_name)
        condition_1 = has_value(self.ctx.args.project_name)
        if condition_0:
            self.AttachedNetworksGetByDevCenter(ctx=self.ctx)()
        elif condition_1:
            AttachedNetworkShowByProject.AttachedNetworksGetByProject(ctx=self.ctx)()

    @register_callback
    def pre_operations(self):
        validate_attached_network_or_dev_box_def(
            self.ctx.args.dev_center_name, self.ctx.args.project_name
        )
        pass

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class AttachedNetworkWait(_AttachedNetworkWait):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class CatalogCreate(_CatalogCreate):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class CatalogDelete(_CatalogDelete):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class CatalogList(_CatalogList):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.top._registered = False
        return args_schema

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


class DevBoxDefinitionCreate(_DevBoxDefinitionCreate):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class DevBoxDefinitionDelete(_DevBoxDefinitionDelete):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class DevBoxDefinitionList(_DevBoxDefinitionList):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.dev_center_name._required = False
        args_schema.project_name = AAZStrArg(
            options=["--project", "--project-name"],
            help="The name of the project. Use az configure -d project=<project_name> to configure a default.",
        )
        args_schema.top._registered = False
        return args_schema

    def _execute_operations(self):
        self.pre_operations()
        condition_0 = has_value(self.ctx.args.dev_center_name)
        condition_1 = has_value(self.ctx.args.project_name)
        if condition_0:
            self.DevBoxDefinitionsListByDevCenter(ctx=self.ctx)()
        elif condition_1:
            DevBoxDefinitionListByProject.DevBoxDefinitionsListByProject(ctx=self.ctx)()

    @register_callback
    def pre_operations(self):
        validate_attached_network_or_dev_box_def(
            self.ctx.args.dev_center_name, self.ctx.args.project_name
        )
        pass

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class DevBoxDefinitionShow(_DevBoxDefinitionShow):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.dev_center_name._required = False
        args_schema.project_name = AAZStrArg(
            options=["--project", "--project-name"],
            help="The name of the project. Use az configure -d project=<project_name> to configure a default.",
        )
        return args_schema

    def _execute_operations(self):
        self.pre_operations()
        condition_0 = has_value(self.ctx.args.dev_center_name)
        condition_1 = has_value(self.ctx.args.project_name)
        if condition_0:
            self.DevBoxDefinitionsGet(ctx=self.ctx)()
        elif condition_1:
            DevBoxDefinitionShowByProject.DevBoxDefinitionsGetByProject(ctx=self.ctx)()

    @register_callback
    def pre_operations(self):
        validate_attached_network_or_dev_box_def(
            self.ctx.args.dev_center_name, self.ctx.args.project_name
        )
        pass

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


class DevCenterList(_DevCenterList):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.top._registered = False
        return args_schema


class EnvironmentTypeCreate(_EnvironmentTypeCreate):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class EnvironmentTypeDelete(_EnvironmentTypeDelete):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class EnvironmentTypeList(_EnvironmentTypeList):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.top._registered = False
        return args_schema

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
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class GalleryDelete(_GalleryDelete):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class GalleryList(_GalleryList):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.top._registered = False
        return args_schema

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
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.gallery_name = AAZStrArg(
            options=["--gallery-name"],
            help="The name of the gallery.",
        )
        args_schema.top._registered = False
        return args_schema

    def _execute_operations(self):
        self.pre_operations()
        condition_0 = has_value(self.ctx.args.gallery_name)
        if condition_0:
            _ImageListByGallery.ImagesListByGallery(ctx=self.ctx)()
        else:
            self.ImagesListByDevCenter(ctx=self.ctx)()

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


class NetworkConnectionList(_NetworkConnectionList):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.top._registered = False
        return args_schema


class NetworkConnectionListHealthDetail(_NetworkConnectionListHealthDetail):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.top._registered = False
        return args_schema


class PoolCreate(_PoolCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.license_type._registered = False
        return args_schema

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class PoolDelete(_PoolDelete):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class PoolList(_PoolList):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.top._registered = False
        return args_schema

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


class ProjectList(_ProjectList):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.top._registered = False
        return args_schema


class ProjectAllowedEnvironmentTypeList(_ProjectAllowedEnvironmentTypeList):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.top._registered = False
        return args_schema

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectAllowedEnvironmentTypeShow(_ProjectAllowedEnvironmentTypeShow):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectEnvironmentTypeCreate(_ProjectEnvironmentTypeCreate):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectEnvironmentTypeDelete(_ProjectEnvironmentTypeDelete):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ProjectEnvironmentTypeList(_ProjectEnvironmentTypeList):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.top._registered = False
        return args_schema

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
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ScheduleDelete(_ScheduleDelete):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ScheduleShow(_ScheduleShow):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.schedule_name._registered = False
        return args_schema

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ScheduleUpdate(_ScheduleUpdate):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class ScheduleWait(_ScheduleWait):
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class SkuList(_SkuList):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.top._registered = False
        return args_schema


# Data plane


def devcenter_project_list_dp(cmd, dev_center):
    resource_graph_data = get_project_arg(cmd.cli_ctx, dev_center)
    if len(resource_graph_data) == 0:
        return []
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center)
    return cf_dataplane.project.list()


def devcenter_project_show_dp(cmd, dev_center, project_name):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.project.get(project_name=project_name)


def devcenter_pool_list_dp(cmd, dev_center, project_name):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.pool.list()


def devcenter_pool_show_dp(cmd, dev_center, project_name, pool_name):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.pool.get(pool_name=pool_name)


def devcenter_schedule_list_dp(cmd, dev_center, project_name, pool_name):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.schedule.list(pool_name=pool_name)


def devcenter_schedule_show_dp(cmd, dev_center, project_name, pool_name, schedule_name):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.schedule.get(pool_name=pool_name, schedule_name=schedule_name)


def devcenter_dev_box_list(cmd, dev_center, project_name=None, user_id=None):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    if project_name is not None and user_id is not None:
        return cf_dataplane.dev_box.list_by_project(user_id=user_id)
    if user_id is not None:
        return cf_dataplane.dev_box.list_by_user(user_id=user_id)
    return cf_dataplane.dev_box.list()


def devcenter_dev_box_show(cmd, dev_center, project_name, dev_box_name, user_id="me"):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.dev_box.get(user_id=user_id, dev_box_name=dev_box_name)


def devcenter_dev_box_create(
    cmd,
    dev_center,
    project_name,
    dev_box_name,
    pool_name,
    user_id="me",
    no_wait=False,
    local_administrator=None,
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    body = {}
    body["pool_name"] = pool_name
    if local_administrator is not None:
        body["local_administrator"] = local_administrator
    return sdk_no_wait(
        no_wait,
        cf_dataplane.dev_box.begin_create,
        user_id=user_id,
        dev_box_name=dev_box_name,
        body=body,
    )


def devcenter_dev_box_delete(
    cmd, dev_center, project_name, dev_box_name, user_id="me", no_wait=False
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return sdk_no_wait(
        no_wait,
        cf_dataplane.dev_box.begin_delete,
        user_id=user_id,
        dev_box_name=dev_box_name,
    )


def devcenter_dev_box_get_remote_connection(
    cmd, dev_center, project_name, dev_box_name, user_id="me"
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.dev_box.get_remote_connection(
        user_id=user_id, dev_box_name=dev_box_name
    )


def devcenter_dev_box_start(
    cmd, dev_center, project_name, dev_box_name, user_id="me", no_wait=False
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return sdk_no_wait(
        no_wait,
        cf_dataplane.dev_box.begin_start,
        user_id=user_id,
        dev_box_name=dev_box_name,
    )


def devcenter_dev_box_stop(
    cmd,
    dev_center,
    project_name,
    dev_box_name,
    no_wait=False,
    hibernate=None,
    user_id="me",
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return sdk_no_wait(
        no_wait,
        cf_dataplane.dev_box.begin_stop,
        user_id=user_id,
        dev_box_name=dev_box_name,
        hibernate=hibernate,
    )


def devcenter_dev_box_delay_upcoming_action(
    cmd,
    dev_center,
    project_name,
    dev_box_name,
    delay_time,
    upcoming_action_id,
    user_id="me",
):
    split_time = delay_time.split(":")
    hours = int(split_time[0])
    minutes = int(split_time[1])
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    upcoming_action = cf_dataplane.dev_box.get_upcoming_action(
        user_id=user_id,
        dev_box_name=dev_box_name,
        upcoming_action_id=upcoming_action_id,
    )
    delayed_time = upcoming_action.scheduled_time + timedelta(
        hours=hours, minutes=minutes
    )
    return cf_dataplane.dev_box.delay_upcoming_action(
        user_id=user_id,
        dev_box_name=dev_box_name,
        upcoming_action_id=upcoming_action_id,
        delay_until=delayed_time,
    )


def devcenter_dev_box_list_upcoming_action(
    cmd, dev_center, project_name, dev_box_name, user_id="me"
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.dev_box.list_upcoming_actions(
        user_id=user_id, dev_box_name=dev_box_name
    )


def devcenter_dev_box_show_upcoming_action(
    cmd, dev_center, project_name, dev_box_name, upcoming_action_id, user_id="me"
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.dev_box.get_upcoming_action(
        user_id=user_id,
        dev_box_name=dev_box_name,
        upcoming_action_id=upcoming_action_id,
    )


def devcenter_dev_box_skip_upcoming_action(
    cmd, dev_center, project_name, dev_box_name, upcoming_action_id, user_id="me"
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.dev_box.skip_upcoming_action(
        user_id=user_id,
        dev_box_name=dev_box_name,
        upcoming_action_id=upcoming_action_id,
    )


def devcenter_environment_list(cmd, dev_center, project_name, user_id="me"):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    if user_id is not None:
        return cf_dataplane.environments.list_by_project_by_user(user_id=user_id)
    return cf_dataplane.environments.list_by_project()


def devcenter_environment_show(
    cmd, dev_center, project_name, environment_name, user_id="me"
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.environments.get(
        user_id=user_id, environment_name=environment_name
    )


def devcenter_environment_create(
    cmd,
    dev_center,
    project_name,
    environment_name,
    environment_type,
    description=None,
    catalog_name=None,
    catalog_item_name=None,
    parameters=None,
    scheduled_tasks=None,
    tags=None,
    user=None,
    no_wait=False,
    user_id="me",
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    body = {}
    if description is not None:
        body["description"] = description
    if catalog_name is not None:
        body["catalog_name"] = catalog_name
    if catalog_item_name is not None:
        body["catalog_item_name"] = catalog_item_name
    if parameters is not None:
        body["parameters"] = parameters
    if scheduled_tasks is not None:
        body["scheduled_tasks"] = scheduled_tasks
    if tags is not None:
        body["tags"] = tags
    body["environment_type"] = environment_type
    if user is not None:
        body["user"] = user
    return sdk_no_wait(
        no_wait,
        cf_dataplane.environments.begin_create_or_update,
        user_id=user_id,
        environment_name=environment_name,
        body=body,
    )


def devcenter_environment_update(
    cmd,
    dev_center,
    project_name,
    environment_name,
    description=None,
    catalog_name=None,
    catalog_item_name=None,
    parameters=None,
    scheduled_tasks=None,
    tags=None,
    user_id=None,
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    body = {}
    if user_id is None:
        user_id = "me"
    if description is not None:
        body["description"] = description
    if catalog_name is not None:
        body["catalog_name"] = catalog_name
    if catalog_item_name is not None:
        body["catalog_item_name"] = catalog_item_name
    if parameters is not None:
        body["parameters"] = parameters
    if scheduled_tasks is not None:
        body["scheduled_tasks"] = scheduled_tasks
    if tags is not None:
        body["tags"] = tags
    return cf_dataplane.environments.update(
        user_id=user_id, environment_name=environment_name, body=body
    )


def devcenter_environment_delete(
    cmd, dev_center, project_name, environment_name, no_wait=False, user_id="me"
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return sdk_no_wait(
        no_wait,
        cf_dataplane.environments.begin_delete,
        user_id=user_id,
        environment_name=environment_name,
    )


def devcenter_environment_custom_action(
    cmd,
    dev_center,
    project_name,
    environment_name,
    action_id,
    parameters=None,
    no_wait=False,
    user_id="me",
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    body = {}
    body["action_id"] = action_id
    if parameters is not None:
        body["parameters"] = parameters
    return sdk_no_wait(
        no_wait,
        cf_dataplane.environments.begin_custom_action,
        user_id=user_id,
        environment_name=environment_name,
        body=body,
    )


def devcenter_environment_deploy_action(
    cmd,
    dev_center,
    project_name,
    environment_name,
    action_id,
    parameters=None,
    no_wait=False,
    user_id="me",
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    body = {}
    body["action_id"] = action_id
    if parameters is not None:
        body["parameters"] = parameters
    return sdk_no_wait(
        no_wait,
        cf_dataplane.environments.begin_deploy_action,
        user_id=user_id,
        environment_name=environment_name,
        body=body,
    )


def devcenter_catalog_item_list(cmd, dev_center, project_name):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.catalog_items.list()


def devcenter_catalog_item_show(cmd, dev_center, project_name, catalog_item_id):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.catalog_items.get(catalog_item_id=catalog_item_id)


def devcenter_catalog_item_version_list(cmd, dev_center, project_name, catalog_item_id):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.catalog_item_versions.list(catalog_item_id=catalog_item_id)


def devcenter_catalog_item_version_show(
    cmd,
    dev_center,
    project_name,
    catalog_item_id,
    version,
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.catalog_item_versions.get(
        catalog_item_id=catalog_item_id,
        version=version,
    )


def devcenter_environment_type_list_dp(cmd, dev_center, project_name):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.environment_type.list()


def devcenter_notification_setting_show_dp(cmd, dev_center, project_name, user_id="me"):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.notification_setting.get(user_id=user_id)


def devcenter_notification_setting_list_allowed_culture_dp(
    cmd, dev_center, project_name, user_id="me"
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    return cf_dataplane.notification_setting.list_allowed_cultures(user_id=user_id)


def devcenter_notification_setting_create_dp(
    cmd,
    dev_center,
    project_name,
    enabled,
    culture,
    boolean_enabled,
    email_notification,
    webhook_notification,
    user_id="me",
):
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, dev_center, project_name)
    body = {}
    body["name"] = "default"
    body["enabled"] = enabled
    body["culture"] = culture
    body["notification_type"] = {}
    body["notification_type"]["dev_box_provisioning_notification"] = {}
    body["notification_type"]["dev_box_provisioning_notification"][
        "enabled"
    ] = boolean_enabled
    body["notification_type"]["dev_box_provisioning_notification"][
        "notification_channel"
    ] = {}
    body["notification_type"]["dev_box_provisioning_notification"][
        "notification_channel"
    ]["email_notification"] = email_notification
    body["notification_type"]["dev_box_provisioning_notification"][
        "notification_channel"
    ]["webhook_notification"] = webhook_notification
    if (
        len(
            body["notification_type"]["dev_box_provisioning_notification"][
                "notification_channel"
            ]
        )
        == 0
    ):
        del body["notification_type"]["dev_box_provisioning_notification"][
            "notification_channel"
        ]
    return cf_dataplane.notification_setting.create(user_id=user_id, body=body)
