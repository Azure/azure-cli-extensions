# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=len-as-condition
from knack.util import CLIError
from msrestazure.tools import is_valid_resource_id


def validate_applications(namespace):
    if namespace.resource_group_name:
        if isinstance(namespace.application, list):
            if len(namespace.application) == 1:
                if is_valid_resource_id(namespace.application[0]):
                    raise CLIError("Specify either a full resource id or an application name and resource group.")
            else:
                raise CLIError("Resource group only allowed with a single application name.")
