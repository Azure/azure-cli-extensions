# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def resource_exception_handler(exception):
    from knack.util import CLIError

    if exception.response.status_code == 404:
        raise CLIError('Can\'t find the resource.')
    else:
        raise CLIError(exception.message)
