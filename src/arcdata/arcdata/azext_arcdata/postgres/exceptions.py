# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------


from azext_arcdata.core.exceptions import CLIError


class PostgresError(CLIError):
    """All errors related to postgres API calls."""

    pass
