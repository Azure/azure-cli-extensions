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
from ._client_factory import cf_devcenter_dataplane
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
)
from .aaz.latest.devcenter.admin.check_name_availability import (
    Execute as _CheckNameAvailabilityExecute,
)
from .aaz.latest.devcenter.admin.devbox_definition import (
    Create as _DevBoxDefinitionCreate,
    Delete as _DevBoxDefinitionDelete,
    List as _DevBoxDefinitionList,
    Show as _DevBoxDefinitionShow,
    Update as _DevBoxDefinitionUpdate,
    Wait as _DevBoxDefinitionWait,
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
        args_schema.devbox_definition_name._required = True
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
        validate_pool_create(
            args.virtual_network_type,
            args.network_connection_name,
            args.managed_virtual_network_regions,
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


def devcenter_project_list_dp(cmd, dev_center=None, endpoint=None):
    if dev_center is not None and endpoint is None:
        resource_graph_data = get_project_arg(cmd.cli_ctx, dev_center)
        if len(resource_graph_data) == 0:
            return []
    cf_dataplane = cf_devcenter_dataplane(cmd.cli_ctx, endpoint, dev_center)

    return cf_dataplane.dev_center.list_projects()


def devcenter_project_show_dp(cmd, project_name, dev_center=None, endpoint=None):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.dev_center.get_project(project_name=project_name)


def devcenter_pool_list_dp(cmd, project_name, dev_center=None, endpoint=None):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.dev_boxes.list_pools(project_name=project_name)


def devcenter_pool_show_dp(
    cmd, project_name, pool_name, dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.dev_boxes.get_pool(
        project_name=project_name, pool_name=pool_name
    )


def devcenter_schedule_list_dp(
    cmd, project_name, pool_name=None, dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    if pool_name is None:
        return cf_dataplane.dev_boxes.list_schedules_by_project(
            project_name=project_name
        )
    return cf_dataplane.dev_boxes.list_schedules(
        project_name=project_name, pool_name=pool_name
    )


def devcenter_schedule_show_dp(
    cmd, pool_name, project_name, dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.dev_boxes.get_schedule(
        project_name=project_name, pool_name=pool_name, schedule_name="default"
    )


def devcenter_dev_box_list(
    cmd, dev_center=None, endpoint=None, project_name=None, user_id=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    if project_name is not None and user_id is not None:
        return cf_dataplane.dev_boxes.list_dev_boxes(
            project_name=project_name, user_id=user_id
        )
    if user_id is not None:
        return cf_dataplane.dev_boxes.list_all_dev_boxes_by_user(user_id=user_id)
    return cf_dataplane.dev_boxes.list_all_dev_boxes()


def devcenter_dev_box_show(
    cmd, dev_box_name, project_name, dev_center=None, endpoint=None, user_id="me"
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.dev_boxes.get_dev_box(
        project_name=project_name, user_id=user_id, dev_box_name=dev_box_name
    )


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
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    body = {}
    body["poolName"] = pool_name
    return sdk_no_wait(
        no_wait,
        cf_dataplane.dev_boxes.begin_create_dev_box,
        project_name=project_name,
        user_id=user_id,
        dev_box_name=dev_box_name,
        body=body,
    )


def devcenter_dev_box_delete(
    cmd,
    dev_box_name,
    project_name,
    user_id="me",
    no_wait=False,
    dev_center=None,
    endpoint=None,
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return sdk_no_wait(
        no_wait,
        cf_dataplane.dev_boxes.begin_delete_dev_box,
        project_name=project_name,
        user_id=user_id,
        dev_box_name=dev_box_name,
    )


def devcenter_dev_box_start(
    cmd,
    project_name,
    dev_box_name,
    user_id="me",
    no_wait=False,
    dev_center=None,
    endpoint=None,
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return sdk_no_wait(
        no_wait,
        cf_dataplane.dev_boxes.begin_start_dev_box,
        project_name=project_name,
        user_id=user_id,
        dev_box_name=dev_box_name,
    )


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
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return sdk_no_wait(
        no_wait,
        cf_dataplane.dev_boxes.begin_stop_dev_box,
        project_name=project_name,
        user_id=user_id,
        dev_box_name=dev_box_name,
        hibernate=hibernate,
    )


def devcenter_dev_box_restart(
    cmd,
    project_name,
    dev_box_name,
    user_id="me",
    no_wait=False,
    dev_center=None,
    endpoint=None,
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return sdk_no_wait(
        no_wait,
        cf_dataplane.dev_boxes.begin_restart_dev_box,
        project_name=project_name,
        user_id=user_id,
        dev_box_name=dev_box_name,
    )


def devcenter_dev_box_repair(
    cmd,
    project_name,
    dev_box_name,
    user_id="me",
    no_wait=False,
    dev_center=None,
    endpoint=None,
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return sdk_no_wait(
        no_wait,
        cf_dataplane.dev_boxes.begin_repair_dev_box,
        project_name=project_name,
        user_id=user_id,
        dev_box_name=dev_box_name,
    )


def devcenter_dev_box_get_remote_connection(
    cmd, project_name, dev_box_name, user_id="me", dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.dev_boxes.get_remote_connection(
        project_name=project_name, user_id=user_id, dev_box_name=dev_box_name
    )


def devcenter_dev_box_list_action(
    cmd, project_name, dev_box_name, user_id="me", dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.dev_boxes.list_actions(
        project_name=project_name, user_id=user_id, dev_box_name=dev_box_name
    )


def devcenter_dev_box_show_action(
    cmd,
    project_name,
    dev_box_name,
    action_name,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )

    return cf_dataplane.dev_boxes.get_action(
        project_name=project_name,
        user_id=user_id,
        dev_box_name=dev_box_name,
        action_name=action_name,
    )


def devcenter_dev_box_skip_action(
    cmd,
    project_name,
    dev_box_name,
    action_name,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.dev_boxes.skip_action(
        project_name=project_name,
        user_id=user_id,
        dev_box_name=dev_box_name,
        action_name=action_name,
    )


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
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    upcoming_action = cf_dataplane.dev_boxes.get_action(
        project_name=project_name,
        user_id=user_id,
        dev_box_name=dev_box_name,
        action_name=action_name,
    )

    upcoming_action_time = upcoming_action["next"]["scheduledTime"]
    action_time = datetime.strptime(upcoming_action_time, "%Y-%m-%dT%H:%M:%S.%fZ")

    delayed_time = get_delayed_time(delay_time, action_time)

    return cf_dataplane.dev_boxes.delay_action(
        project_name=project_name,
        user_id=user_id,
        dev_box_name=dev_box_name,
        action_name=action_name,
        until=delayed_time,
    )


def devcenter_dev_box_delay_all_actions(
    cmd,
    project_name,
    dev_box_name,
    delay_time,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )

    actions = cf_dataplane.dev_boxes.list_actions(
        project_name=project_name, user_id=user_id, dev_box_name=dev_box_name
    )
    earliest_time = get_earliest_time(actions)
    if earliest_time is None:
        raise ResourceNotFoundError("There are no scheduled actions for this dev box.")

    delayed_time = get_delayed_time(delay_time, earliest_time)

    return cf_dataplane.dev_boxes.delay_all_actions(
        project_name=project_name,
        user_id=user_id,
        dev_box_name=dev_box_name,
        until=delayed_time,
    )


def devcenter_dev_box_list_operation(
    cmd, project_name, dev_box_name, user_id="me", dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.dev_boxes.list_operations(
        project_name=project_name, user_id=user_id, dev_box_name=dev_box_name
    )


def devcenter_dev_box_show_operation(
    cmd,
    project_name,
    dev_box_name,
    operation_id,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.dev_boxes.get_operation(
        project_name=project_name,
        user_id=user_id,
        dev_box_name=dev_box_name,
        operation_id=operation_id,
    )


def devcenter_environment_list(
    cmd, project_name, user_id=None, dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )

    if user_id is not None:
        return cf_dataplane.deployment_environments.list_environments(
            project_name=project_name, user_id=user_id
        )
    return cf_dataplane.deployment_environments.list_all_environments(
        project_name=project_name
    )


def devcenter_environment_show(
    cmd, project_name, environment_name, user_id="me", dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )

    return cf_dataplane.deployment_environments.get_environment(
        project_name=project_name, user_id=user_id, environment_name=environment_name
    )


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
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    environments_iterator = cf_dataplane.deployment_environments.list_environments(
        project_name=project_name, user_id=user_id
    )
    validate_env_name_already_exists(
        environments_iterator, environment_name, user_id, project_name
    )
    body = {}
    if parameters is not None:
        body["parameters"] = parameters
    body["environmentType"] = environment_type
    body["catalogName"] = catalog_name
    body["environmentDefinitionName"] = environment_definition_name
    if expiration_date is not None:
        body["expirationDate"] = datetime.fromisoformat(expiration_date)
    return sdk_no_wait(
        no_wait,
        cf_dataplane.deployment_environments.begin_create_or_update_environment,
        project_name=project_name,
        user_id=user_id,
        environment_name=environment_name,
        body=body,
    )


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
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    environment = cf_dataplane.deployment_environments.get_environment(
        project_name=project_name, user_id=user_id, environment_name=environment_name
    )
    body = {}
    if parameters is not None:
        body["parameters"] = parameters
    body["environmentType"] = environment["environmentType"]
    body["catalogName"] = environment["catalogName"]
    body["environmentDefinitionName"] = environment["environmentDefinitionName"]
    if expiration_date is not None:
        body["expirationDate"] = datetime.fromisoformat(expiration_date)
    return sdk_no_wait(
        no_wait,
        cf_dataplane.deployment_environments.begin_create_or_update_environment,
        project_name=project_name,
        user_id=user_id,
        environment_name=environment_name,
        body=body,
    )


def devcenter_environment_delete(
    cmd,
    environment_name,
    project_name,
    no_wait=False,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return sdk_no_wait(
        no_wait,
        cf_dataplane.deployment_environments.begin_delete_environment,
        project_name=project_name,
        user_id=user_id,
        environment_name=environment_name,
    )


def devcenter_catalog_list_dp(cmd, project_name, dev_center=None, endpoint=None):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.deployment_environments.list_catalogs(project_name=project_name)


def devcenter_catalog_show_dp(
    cmd, project_name, catalog_name, dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.deployment_environments.get_catalog(
        project_name=project_name, catalog_name=catalog_name
    )


def devcenter_environment_definition_list_dp(
    cmd, project_name, dev_center=None, endpoint=None, catalog_name=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    if catalog_name is not None:
        return cf_dataplane.deployment_environments.list_environment_definitions_by_catalog(
            project_name=project_name, catalog_name=catalog_name
        )
    return cf_dataplane.deployment_environments.list_environment_definitions(
        project_name=project_name
    )


def devcenter_environment_definition_show_dp(
    cmd, catalog_name, definition_name, project_name, dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.deployment_environments.get_environment_definition(
        project_name=project_name,
        catalog_name=catalog_name,
        definition_name=definition_name,
    )


def devcenter_environment_type_list_dp(
    cmd, project_name, dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.deployment_environments.list_environment_types(
        project_name=project_name
    )


def devcenter_environment_operation_list(
    cmd, project_name, environment_name, user_id="me", dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )

    return cf_dataplane.environments.list_operations(
        project_name=project_name, environment_name=environment_name, user_id=user_id
    )


def devcenter_environment_operation_show(
    cmd,
    project_name,
    environment_name,
    operation_id,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )

    return cf_dataplane.environments.get_operation(
        project_name=project_name,
        operation_id=operation_id,
        user_id=user_id,
        environment_name=environment_name,
    )


def devcenter_environment_operation_show_logs_by_operation(
    cmd,
    project_name,
    environment_name,
    operation_id,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )

    logs = cf_dataplane.environments.get_logs_by_operation(
        project_name=project_name,
        operation_id=operation_id,
        user_id=user_id,
        environment_name=environment_name,
    )
    logs_array = []
    for log in logs:
        logs_string = json.loads(log)
        logs_array.append(logs_string)
    return logs_array


def devcenter_environment_operation_show_action(
    cmd,
    project_name,
    environment_name,
    action_name,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )

    return cf_dataplane.environments.get_action(
        project_name=project_name,
        user_id=user_id,
        action_name=action_name,
        environment_name=environment_name,
    )


def devcenter_environment_operation_list_action(
    cmd, project_name, environment_name, user_id="me", dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )

    return cf_dataplane.environments.list_actions(
        project_name=project_name, user_id=user_id, environment_name=environment_name
    )


def devcenter_environment_operation_delay_action(
    cmd,
    project_name,
    environment_name,
    action_name,
    delay_time,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )

    upcoming_action = cf_dataplane.environments.get_action(
        project_name=project_name,
        user_id=user_id,
        action_name=action_name,
        environment_name=environment_name,
    )

    upcoming_action_time = upcoming_action["next"]["scheduledTime"]
    action_time = datetime.strptime(upcoming_action_time, "%Y-%m-%dT%H:%M:%S.%fZ")

    delayed_time = get_delayed_time(delay_time, action_time)

    return cf_dataplane.environments.delay_action(
        project_name=project_name,
        action_name=action_name,
        user_id=user_id,
        until=delayed_time,
        environment_name=environment_name,
    )


def devcenter_environment_operation_skip_action(
    cmd,
    project_name,
    environment_name,
    action_name,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )

    return cf_dataplane.environments.skip_action(
        project_name=project_name,
        action_name=action_name,
        user_id=user_id,
        environment_name=environment_name,
    )


def devcenter_environment_operation_show_outputs(
    cmd, project_name, environment_name, user_id="me", dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )

    return cf_dataplane.environments.get_outputs(
        project_name=project_name, user_id=user_id, environment_name=environment_name
    )


def devcenter_environment_operation_update_environment(
    cmd,
    project_name,
    environment_name,
    user_id="me",
    dev_center=None,
    endpoint=None,
    expiration_date=None,
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    body = {}
    if expiration_date is not None:
        body["expirationDate"] = datetime.fromisoformat(expiration_date)

    return cf_dataplane.environments.patch_environment(
        project_name=project_name,
        user_id=user_id,
        environment_name=environment_name,
        body=body,
    )
