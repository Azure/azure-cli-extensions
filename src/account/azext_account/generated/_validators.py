# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def alias_validator(namespace):
    if namespace.subscription_id:
        if namespace.billing_scope or namespace.display_name:
            raise CLIError('--billing-scope or --display-name is not allowed when --subscription-id is provided.')
    else:
        if not namespace.billing_scope or not namespace.display_name or not namespace.workload:
            raise CLIError('--billing-scope, --display-name and --workload are required when creating '
                           'an alias with a new susbcription.')
