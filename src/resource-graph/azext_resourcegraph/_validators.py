# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def validate_query_args(namespace):
    if namespace.first and not 1 <= namespace.first <= 1000:
        raise CLIError("Value of --first has to be between 1 and 1000.")

    if namespace.skip and not namespace.skip >= 0:
        raise CLIError("Value of --skip cannot be negative.")

    if namespace.subscriptions is not None and namespace.management_groups is not None:
        raise CLIError("Both --subscriptions and --management-groups cannot be passed together at the same time.")
