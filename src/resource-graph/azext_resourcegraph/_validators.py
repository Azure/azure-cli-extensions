# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import InvalidArgumentValueError


__ROWS_PER_PAGE = 1000
__FIRST = 100
__SKIP = 0


def validate_query_args(namespace):
    if namespace.first and not 1 <= namespace.first <= 1000:
        raise InvalidArgumentValueError("Value of --first has to be between 1 and 1000.")

    if namespace.skip and not namespace.skip >= 0:
        raise InvalidArgumentValueError("Value of --skip cannot be negative.")

    if namespace.subscriptions is not None and namespace.management_groups is not None:
        error_msg = 'Both --subscriptions and --management-groups cannot be passed together at the same time.'
        recommendation = 'Try to pass --subscriptions param only or --management-groups param only.'
        raise InvalidArgumentValueError(error_msg, recommendation)

    if namespace.first is not None:
        namespace.first = min(namespace.first, __ROWS_PER_PAGE)
    elif namespace.skip_token is None:
        namespace.first = __FIRST

    if namespace.skip is None and namespace.skip_token is None:
        namespace.skip = __SKIP
