# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def validate_notification_message(namespace):
    """Validate message or payload to send"""
    from knack.util import CLIError
    if namespace.message is None and namespace.payload is None:
        raise CLIError('usage error: --message | --payload')
