# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from knack.cli import CLIError
from requests.exceptions import HTTPError


class ClusterLogError(CLIError):
    """All errors related to log collection calls."""

    pass
