# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from msrest.exceptions import ValidationError  # pylint: disable=import-error


def netapp_exception_handler(ex):
    from azext_netappfiles_preview.vendored_sdks.models import ErrorException

    if isinstance(ex, ErrorException) or (isinstance(ex) == ValidationError) or (isinstance(ex) == ValueError):
        message = ex
        raise CLIError(message)
    else:
        import sys

        from six import reraise
        reraise(*sys.exc_info())
