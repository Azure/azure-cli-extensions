# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access

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
        args_schema.dev_box_definition_name._required = True
        args_schema.local_administrator._required = True
        args_schema.network_connection_name._required = True
        return args_schema

    @register_callback
    def pre_operations(self):
        args = self.ctx.args
        args.license_type = "Windows_Client"

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

    return cf_dataplane.project.list()


def devcenter_project_show_dp(cmd, project_name, dev_center=None, endpoint=None):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.project.get(project_name=project_name)


def devcenter_pool_list_dp(cmd, project_name, dev_center=None, endpoint=None):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.pool.list()


def devcenter_pool_show_dp(
    cmd, project_name, pool_name, dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.pool.get(pool_name=pool_name)


def devcenter_schedule_list_dp(
    cmd, pool_name, project_name, dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.schedule.list(pool_name=pool_name)


def devcenter_schedule_show_dp(
    cmd, pool_name, project_name, dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.schedule.get(pool_name=pool_name, schedule_name="default")


def devcenter_dev_box_list(
    cmd, dev_center=None, endpoint=None, project_name=None, user_id=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    if project_name is not None and user_id is not None:
        return cf_dataplane.dev_box.list_by_project(user_id=user_id)
    if user_id is not None:
        return cf_dataplane.dev_box.list_by_user(user_id=user_id)
    return cf_dataplane.dev_box.list()


def devcenter_dev_box_show(
    cmd, dev_box_name, project_name, dev_center=None, endpoint=None, user_id="me"
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.dev_box.get(user_id=user_id, dev_box_name=dev_box_name)


def devcenter_dev_box_create(
    cmd,
    dev_box_name,
    pool_name,
    project_name,
    user_id="me",
    no_wait=False,
    local_administrator=None,
    dev_center=None,
    endpoint=None,
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
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
        cf_dataplane.dev_box.begin_delete,
        user_id=user_id,
        dev_box_name=dev_box_name,
    )


def devcenter_dev_box_get_remote_connection(
    cmd, project_name, dev_box_name, user_id="me", dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.dev_box.get_remote_connection(
        user_id=user_id, dev_box_name=dev_box_name
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
        cf_dataplane.dev_box.begin_start,
        user_id=user_id,
        dev_box_name=dev_box_name,
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
        cf_dataplane.dev_box.begin_restart,
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
        cf_dataplane.dev_box.begin_stop,
        user_id=user_id,
        dev_box_name=dev_box_name,
        hibernate=hibernate,
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
    upcoming_action = cf_dataplane.dev_box.get_action(
        user_id=user_id,
        dev_box_name=dev_box_name,
        action_name=action_name,
    )

    delayed_time = get_delayed_time(delay_time, upcoming_action.next.scheduled_time)

    return cf_dataplane.dev_box.delay_action(
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

    actions = cf_dataplane.dev_box.list_actions(
        user_id=user_id, dev_box_name=dev_box_name
    )
    earliest_time = get_earliest_time(actions)
    if earliest_time is None:
        raise ResourceNotFoundError("There are no scheduled actions for this dev box.")

    delayed_time = get_delayed_time(delay_time, earliest_time)

    return cf_dataplane.dev_box.delay_actions(
        user_id=user_id,
        dev_box_name=dev_box_name,
        until=delayed_time,
    )


def devcenter_dev_box_list_action(
    cmd, project_name, dev_box_name, user_id="me", dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.dev_box.list_actions(user_id=user_id, dev_box_name=dev_box_name)


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
    return cf_dataplane.dev_box.get_action(
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
    return cf_dataplane.dev_box.skip_action(
        user_id=user_id,
        dev_box_name=dev_box_name,
        action_name=action_name,
    )


def devcenter_environment_list(
    cmd, project_name, user_id=None, dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    if user_id is not None:
        return cf_dataplane.environments.list_by_project_by_user(user_id=user_id)
    return cf_dataplane.environments.list_by_project()


def devcenter_environment_show(
    cmd, project_name, environment_name, user_id="me", dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.environments.get(
        user_id=user_id, environment_name=environment_name
    )


def devcenter_environment_create(
    cmd,
    environment_name,
    environment_type,
    project_name,
    catalog_name,
    environment_definition_name,
    parameters=None,
    no_wait=False,
    user_id="me",
    dev_center=None,
    endpoint=None,
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    environments_iterator = cf_dataplane.environments.list_by_project_by_user(
        user_id=user_id
    )
    validate_env_name_already_exists(
        environments_iterator, environment_name, user_id, project_name
    )
    body = {}
    if parameters is not None:
        body["parameters"] = parameters
    body["environment_type"] = environment_type
    body["catalog_name"] = catalog_name
    body["environment_definition_name"] = environment_definition_name
    return sdk_no_wait(
        no_wait,
        cf_dataplane.environments.begin_create_or_replace,
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
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    environment = cf_dataplane.environments.get(
        user_id=user_id, environment_name=environment_name
    )
    body = {}
    if parameters is not None:
        body["parameters"] = parameters
    body["environment_type"] = environment.environment_type
    body["catalog_name"] = environment.catalog_name
    body["environment_definition_name"] = environment.environment_definition_name
    return sdk_no_wait(
        no_wait,
        cf_dataplane.environments.begin_create_or_replace,
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
        cf_dataplane.environments.begin_delete,
        user_id=user_id,
        environment_name=environment_name,
    )


def devcenter_environment_type_list_dp(
    cmd, project_name, dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.environment_type.list()


def devcenter_catalog_list_dp(cmd, project_name, dev_center=None, endpoint=None):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.catalogs.list()


def devcenter_catalog_show_dp(
    cmd, project_name, catalog_name, dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.catalogs.get(catalog_name=catalog_name)


def devcenter_environment_definition_list_dp(
    cmd, project_name, dev_center=None, endpoint=None, catalog_name=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    if catalog_name is not None:
        return cf_dataplane.environment_definitions.list_by_catalog(
            catalog_name=catalog_name
        )
    return cf_dataplane.environment_definitions.list()


def devcenter_environment_definition_show_dp(
    cmd, catalog_name, definition_name, project_name, dev_center=None, endpoint=None
):
    cf_dataplane = cf_devcenter_dataplane(
        cmd.cli_ctx, endpoint, dev_center, project_name
    )
    return cf_dataplane.environment_definitions.get(
        catalog_name=catalog_name, definition_name=definition_name
    )
