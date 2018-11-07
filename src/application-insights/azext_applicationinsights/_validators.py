# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=len-as-condition
from knack.util import CLIError


def validate_applications(namespace):
    if namespace.resource_group_name:
        if isinstance(namespace.application, list) and len(namespace.application) != 1:
            raise CLIError("Resource group only allowed with a single application name.")
