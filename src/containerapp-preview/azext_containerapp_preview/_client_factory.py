# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import CLIInternalError


# pylint: disable=inconsistent-return-statements
def ex_handler_factory(no_throw=False):
    def _polish_bad_errors(ex):
        import json
        try:
            content = json.loads(ex.response.content)
            if 'message' in content:
                detail = content['message']
            elif 'Message' in content:
                detail = content['Message']

            ex = CLIInternalError(detail)
        except Exception:  # pylint: disable=broad-except
            pass
        if no_throw:
            return ex
        raise ex
    return _polish_bad_errors
