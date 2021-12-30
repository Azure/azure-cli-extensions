# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-few-public-methods, unused-argument, redefined-builtin

from azure.cli.core.util import CLIError
from ._util_enterprise import is_enterprise_tier


def only_support_enterprise(cmd, namespace):
    if namespace.resource_group and namespace.service and not is_enterprise_tier(cmd, namespace.resource_group, namespace.service):
        raise CLIError("'{}' only supports for Enterprise tier Spring instance.".format(namespace.command))


def not_support_enterprise(cmd, namespace):
    if namespace.resource_group and namespace.service and is_enterprise_tier(cmd, namespace.resource_group, namespace.service):
        raise CLIError("'{}' doesn't support for Enterprise tier Spring instance.".format(namespace.command))
