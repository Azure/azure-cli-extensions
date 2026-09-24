# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from knack.cli import CLIError


class SqlmidbError(CLIError):
    """All errors related to sqlmidb API calls."""
