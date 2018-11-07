# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_subscription_id
from knack.util import CLIError


def validate_applications(namespace):
    if namespace.resource_group:
        if len(namespace.apps != 1):
            raise CLIError("Resource group only allowed with a single application name.")
