# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.core.cli_client import CliClient

__all__ = ["beget"]


def beget(az_cli, kwargs):
    """Client factory"""
    return SqlArcServerClientMixin(az_cli, kwargs)


class SqlArcServerClientMixin(CliClient):
    def __init__(self, az_cli, kwargs):
        super(SqlArcServerClientMixin, self).__init__(
            az_cli, kwargs, check_namespace=None
        )
