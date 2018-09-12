# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def validate_query_args(namespace):
    if not 1 <= namespace.first <= 5000:
        raise CLIError("Value of --first has to be between 1 and 5000.")

    if not namespace.skip >= 0:
        raise CLIError("Value of --skip cannot be negative.")
