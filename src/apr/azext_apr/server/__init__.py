# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Data-plane server communication: HTTP client, polling, uploads."""

from azext_apr.server._data_plane import (
    DataPlaneClient,
    is_dev_extension,
    raise_if_dev_extension,
    resolve_api_endpoint,
)
from azext_apr.server._paging import iter_results, list_all
from azext_apr.server._polling import poll_task, wait_for_task
from azext_apr.server._resolve import (
    resolve_id_or_name,
    resolve_release,
    resolve_release_component,
    resolve_release_name,
)

__all__ = [
    "DataPlaneClient",
    "is_dev_extension",
    "raise_if_dev_extension",
    "resolve_api_endpoint",
    "iter_results",
    "list_all",
    "poll_task",
    "wait_for_task",
    "resolve_id_or_name",
    "resolve_release",
    "resolve_release_component",
    "resolve_release_name",
]
