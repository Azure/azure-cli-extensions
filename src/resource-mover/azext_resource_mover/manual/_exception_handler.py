# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def resource_dependency_handler(ex):
    from azure.core.exceptions import HttpResponseError
    from knack.util import CLIError

    if isinstance(ex, HttpResponseError):
        try:
            response = ex.response.text(encoding='utf-8')
        except Exception:  # pylint: disable=broad-except
            pass
        raise CLIError(response)

    raise ex
