# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def resource_dependency_handler(ex):
    import json
    from azure.core.exceptions import HttpResponseError
    from knack.util import CLIError

    if isinstance(ex, HttpResponseError):
        format_response = None
        try:
            response = ex.response.text(encoding='utf-8')
            parsed = json.loads(response, strict=False)
            format_response = json.dumps(parsed, indent=4)
        except Exception:  # pylint: disable=broad-except
            pass

        if format_response and 'MoveCollectionMissingRequiredDependentResources' in str(ex):
            raise CLIError(format_response)

    raise ex
