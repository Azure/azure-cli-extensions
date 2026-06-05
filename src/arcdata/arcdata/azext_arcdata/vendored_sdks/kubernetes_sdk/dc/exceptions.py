# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from knack.cli import CLIError
from requests.exceptions import HTTPError


class ArcError(CLIError):
    """All errors related to arc API calls."""

    pass


class RequestTimeoutError(HTTPError):
    """HTTP 408 Requet Timeout error while calling APIs."""

    pass


class ServerError(HTTPError):
    """HTTP 5xx errors while calling APIs."""

    pass
