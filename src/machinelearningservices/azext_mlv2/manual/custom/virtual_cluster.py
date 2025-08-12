# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from .raise_error import log_and_raise_error
from .utils import get_ml_client


def ml_virtual_cluster_list(cmd):

    ml_client, debug = get_ml_client(cli_ctx=cmd.cli_ctx)

    try:
        return ml_client._virtual_clusters.list()  # pylint: disable=protected-access
    except Exception as err:  # pylint: disable=broad-exception-caught
        log_and_raise_error(err, debug)


def ml_virtual_cluster_show(cmd, name, resource_group_name=None):
    ml_client, debug = get_ml_client(
        cli_ctx=cmd.cli_ctx,
        resource_group_name=resource_group_name
    )

    try:
        return ml_client._virtual_clusters.get(name=name)  # pylint: disable=protected-access
    except Exception as err:  # pylint: disable=broad-exception-caught
        log_and_raise_error(err, debug)
