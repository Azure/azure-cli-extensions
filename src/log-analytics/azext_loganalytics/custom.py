# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger

logger = get_logger(__name__)


def execute_query(client, workspace, analytics_query, timespan=None, workspaces=None):
    """Executes a query against the provided Log Analytics workspace."""
    from .vendored_sdks.loganalytics.models import QueryBody
    return client.query(workspace, QueryBody(query=analytics_query, timespan=timespan, workspaces=workspaces))
