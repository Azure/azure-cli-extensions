# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from knack.log import get_logger

from .raise_error import log_and_raise_error
from .utils import _dump_entity_with_warnings, get_ml_client

module_logger = get_logger(__name__)


def ml_azure_openai_deployment_list(cmd, resource_group_name, workspace_name, connection_name):
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx, resource_group_name=resource_group_name, workspace_name=workspace_name
    )

    try:
        return list(
            map(
                lambda deployment: _dump_entity_with_warnings(deployment),
                ml_client.azure_openai_deployments.list(connection_name),
            )
        )
    except Exception as err:
        log_and_raise_error(err, debug)
