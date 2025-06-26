# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import logging

from azure.ai.ml.constants._endpoint import EndpointKeyType
from azure.ai.ml.entities import ServerlessEndpoint
from azure.ai.ml.entities._load_functions import load_serverless_endpoint
from azure.cli.core.commands import LongRunningOperation

from .raise_error import log_and_raise_error
from .utils import (
    _dump_entity_with_warnings,
    convert_str_to_dict,
    get_ml_client,
    is_not_found_error,
    open_online_endpoint_in_browser,
    wrap_lro,
)

module_logger = logging.getLogger(__name__)
module_logger.propagate = 0


def ml_serverless_endpoint_show(cmd, resource_group_name, workspace_name, name):
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx, resource_group_name=resource_group_name, workspace_name=workspace_name
    )

    try:
        endpoint = ml_client.serverless_endpoints.get(name=name)
        return endpoint.as_dict()
    except Exception as err:
        log_and_raise_error(err, debug)


def ml_serverless_endpoint_create(
    cmd,
    resource_group_name,
    workspace_name,
    file=None,
    name=None,
    no_wait=False,
    params_override=None,
    **kwargs,
):
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx, resource_group_name=resource_group_name, workspace_name=workspace_name
    )
    params_override = params_override or []
    try:
        if name:
            # MFE is case-insensitive for Name. So convert the name into lower case here.
            params_override.append({"name": name.lower()})

        endpoint = load_serverless_endpoint(source=file, params_override=params_override)
        endpoint_name = endpoint.name
        endpoint = ml_client.begin_create_or_update(endpoint)
        if no_wait:
            module_logger.warning(
                "Endpoint create request initiated. "
                f"Status can be checked using `az ml serverless-endpoint show -n {endpoint_name}`\n"
            )
        else:
            endpoint = wrap_lro(cmd.cli_ctx, endpoint)
            return endpoint.as_dict()
    except Exception as err:
        yaml_operation = True if file else False
        log_and_raise_error(err, debug, yaml_operation=yaml_operation)


def ml_serverless_endpoint_delete(
    cmd,
    resource_group_name,
    workspace_name,
    name,
    no_wait=False,
):
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx, resource_group_name=resource_group_name, workspace_name=workspace_name
    )
    try:
        ml_client.serverless_endpoints.get(name=name)
    except Exception as err:
        if is_not_found_error(err):
            raise Exception(f"Serverless endpoint {name} does not exist.")

    try:
        delete_result = ml_client.serverless_endpoints.begin_delete(name=name)
        if not no_wait:
            delete_result = wrap_lro(cmd.cli_ctx, delete_result)
        return _dump_entity_with_warnings(delete_result)
    except Exception as err:
        log_and_raise_error(err, debug)


def ml_serverless_endpoint_get_credentials(cmd, resource_group_name, workspace_name, name):
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx, resource_group_name=resource_group_name, workspace_name=workspace_name
    )
    try:
        return ml_client.serverless_endpoints.get_keys(name=name)
    except Exception as err:
        log_and_raise_error(err, debug)


def ml_serverless_endpoint_list(cmd, resource_group_name, workspace_name):
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx, resource_group_name=resource_group_name, workspace_name=workspace_name
    )
    try:
        results = ml_client.serverless_endpoints.list()
        return list(map(lambda x: _dump_entity_with_warnings(x), results))
    except Exception as err:
        log_and_raise_error(err, debug)


def _ml_serverless_endpoint_update(
    cmd,
    resource_group_name,
    workspace_name,
    parameters=None,
    no_wait=False,
    **kwargs,
) -> None:
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx, resource_group_name=resource_group_name, workspace_name=workspace_name
    )
    try:
        endpoint = ServerlessEndpoint(parameters)
        endpoint._validate()
        ml_client.serverless_endpoints.begin_create_or_update(endpoint)
        if no_wait:
            module_logger.warning(
                "Endpoint update request initiated. "
                f"Status can be checked using `az ml serverless-endpoint show -n {parameters.name}`\n"
            )
        else:
            endpoint_return = wrap_lro(cmd.cli_ctx, endpoint_return)
            return endpoint_return.as_dict()

    except Exception as err:
        log_and_raise_error(err, debug)


def ml_serverless_endpoint_regenerate_keys(
    cmd, resource_group_name, workspace_name, name, key_type=EndpointKeyType.PRIMARY_KEY_TYPE, no_wait: bool = False
):
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx, resource_group_name=resource_group_name, workspace_name=workspace_name
    )

    try:
        keys = ml_client.serverless_endpoints.begin_regenerate_keys(name=name)
        if not no_wait:
            keys = LongRunningOperation(cmd.cli_ctx)(keys)
        return keys
    except Exception as err:
        log_and_raise_error(err, debug)
