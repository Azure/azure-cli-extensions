# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def validate_cert_file(namespace):
    """Validate the give cert file existing"""
    try:
        if namespace.apns_certificate is not None:
            with open(namespace.apns_certificate, "rb"):
                pass
    except EnvironmentError:
        raise ValueError("Cannot access certificate file: " + namespace.apns_certificate)


def validate_notification_message(namespace):
    """Validate message or payload to send"""
    from knack.util import CLIError
    if namespace.message is None and namespace.payload is None:
        raise CLIError('usage error: --message | --payload')
