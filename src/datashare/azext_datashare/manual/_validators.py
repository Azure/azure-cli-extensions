# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=unused-argument


def invitation_id_validator(cmd, namespace):
    if namespace.invitation_id:
        if namespace.invitation_id.startswith("/providers"):
            namespace.invitation_id = namespace.invitation_id.split("/")[-1]
