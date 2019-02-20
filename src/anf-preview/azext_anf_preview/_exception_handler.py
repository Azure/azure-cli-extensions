# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def netapp_exception_handler(ex):
    from azext_anf_preview.vendored_sdks.models import ErrorException
    if isinstance(ex, ErrorException):
        message = ex
        raise CLIError(message)
    else:
        import sys
        from six import reraise
        reraise(*sys.exc_info())
