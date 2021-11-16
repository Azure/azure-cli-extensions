# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
import json
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.core.exceptions import HttpResponseError


def exception_handler(ex):
    if isinstance(ex, HttpResponseError) and 'application/json' in ex.response.headers['Content-Type'] and ex.status_code == 400:
        message = json.loads(ex.response.text(encoding='utf-8'), strict=False)
        raise InvalidArgumentValueError(message)
    raise ex
