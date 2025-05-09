# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from msrest.exceptions import ValidationError  # pylint: disable=import-error
from msrestazure.azure_exceptions import CloudError


def netapp_exception_handler(ex):
    if isinstance(ex, (CloudError, ValidationError, ValueError)):
        message = ex
        raise CLIError(message)

    raise ex
