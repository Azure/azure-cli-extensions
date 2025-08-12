# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from itertools import islice
from typing import Dict

from azure.ai.ml.entities._assets import Environment
from azure.ai.ml.entities._load_functions import load_environment

from .raise_error import log_and_raise_error
from .utils import _dump_entity_with_warnings, get_list_view_type, get_ml_client


def ml_environment_create(
    cmd,
    resource_group_name=None,
    workspace_name=None,
    registry_name=None,
    file=None,
    name=None,
    version=None,
    tags=None,
    description=None,
    image=None,
    conda_file=None,
    build_context=None,
    dockerfile_path="/Dockerfile",
    os_type=None,
    datastore=None,
    params_override=None,
):
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
        registry_name=registry_name,
    )
    params_override = params_override or []

    if name:
        params_override.append({"name": name})
    if version:
        params_override.append({"version": version})
    if tags:
        params_override.append({"tags": tags})
    if description:
        params_override.append({"description": description})
    if image:
        params_override.append({"image": image})
    if conda_file:
        params_override.append({"conda_file": conda_file})
    if build_context:
        build = {"path": build_context, "dockerfile_path": dockerfile_path}
        params_override.append({"build": build})
    if os_type:
        params_override.append({"os_type": os_type})
    if datastore:
        params_override.append({"datastore": datastore})

    try:
        environment = load_environment(source=file, params_override=params_override)
        environment = ml_client.create_or_update(environment)
        return _dump_entity_with_warnings(environment)
    except Exception as err:  # pylint: disable=broad-exception-caught
        yaml_operation = bool(file)
        log_and_raise_error(err, debug, yaml_operation=yaml_operation)


def ml_environment_show(
    cmd, name, resource_group_name=None, workspace_name=None, registry_name=None,
    version=None, label=None
):
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
        registry_name=registry_name,
    )

    try:
        environment = ml_client.environments.get(name=name, version=version, label=label)
        return _dump_entity_with_warnings(environment)
    except Exception as err:  # pylint: disable=broad-exception-caught
        log_and_raise_error(err, debug)


def ml_environment_list(
    cmd,
    resource_group_name=None,
    workspace_name=None,
    registry_name=None,
    name=None,
    max_results=None,
    include_archived=False,
    archived_only=False,
):
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
        registry_name=registry_name,
    )

    try:
        list_view_type = get_list_view_type(include_archived=include_archived, archived_only=archived_only)
        if max_results:
            results = islice(
                ml_client.environments.list(name=name, list_view_type=list_view_type),
                int(max_results),
            )
        else:
            results = ml_client.environments.list(name=name, list_view_type=list_view_type)
        return [_dump_entity_with_warnings(x) for x in results]
    except Exception as err:  # pylint: disable=broad-exception-caught
        log_and_raise_error(err, debug)


def _ml_environment_update(
    cmd, resource_group_name=None, workspace_name=None, registry_name=None, parameters: Dict = None
):
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
        registry_name=registry_name,
    )

    try:
        # Set unknown to EXCLUDE so that marshallow doesn't raise on dump only fields.
        environment = Environment._load(data=parameters)  # pylint: disable=protected-access
        updated_environment = ml_client.create_or_update(environment)
        return _dump_entity_with_warnings(updated_environment)
    except Exception as err:  # pylint: disable=broad-exception-caught
        log_and_raise_error(err, debug)


def ml_environment_archive(
    cmd, name, resource_group_name=None, workspace_name=None, registry_name=None, version=None, label=None
):
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
        registry_name=registry_name,
    )
    try:
        return ml_client.environments.archive(name=name, version=version, label=label)
    except Exception as err:  # pylint: disable=broad-exception-caught
        log_and_raise_error(err, debug)


def ml_environment_restore(
    cmd, name, resource_group_name=None, workspace_name=None, registry_name=None, version=None, label=None
):
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
        registry_name=registry_name,
    )
    try:
        return ml_client.environments.restore(name=name, version=version, label=label)
    except Exception as err:  # pylint: disable=broad-exception-caught
        log_and_raise_error(err, debug)


def _ml_environment_show(cmd, resource_group_name, name, version=None, label=None,
                         workspace_name=None, registry_name=None):
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
        registry_name=registry_name,
    )

    try:
        environment = ml_client.environments.get(name=name, version=version, label=label)
        return _dump_entity_with_warnings(environment)
    except Exception as err:  # pylint: disable=broad-exception-caught
        log_and_raise_error(err, debug)


def ml_environment_share(
    cmd,
    name,
    version,
    share_with_name,
    share_with_version,
    registry_name,
    resource_group_name=None,
    workspace_name=None,
):
    ml_client, _ = get_ml_client(
        cli_ctx=cmd.cli_ctx, resource_group_name=resource_group_name, workspace_name=workspace_name
    )

    environment = ml_client.environments.share(
        name=name,
        version=version,
        registry_name=registry_name,
        share_with_name=share_with_name,
        share_with_version=share_with_version,
    )
    return _dump_entity_with_warnings(environment)
