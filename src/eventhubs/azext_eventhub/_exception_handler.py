# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def eventhubs_exception_handler(ex):
    from azext_eventhub.eventhub.models import ErrorResponseException
    if isinstance(ex, ErrorResponseException):
        raise CLIError(ex.message)
    else:
        import sys
        from six import reraise
        reraise(*sys.exc_info())
