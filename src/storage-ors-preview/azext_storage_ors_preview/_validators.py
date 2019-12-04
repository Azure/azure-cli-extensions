# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def validate_ors_policy(namespace):
    if namespace.properties is None:
        if namespace.source_account is None:
            raise ValueError("--source-account is required to create ORS Policy.")
        if namespace.destination_account is None:
            raise ValueError("--destination-account is required to create ORS Policy.")
        validate_ors_rule


def validate_ors_rule(namespace):
    if namespace.source_container is None:
        raise ValueError("--source-container is required to create ORS Policy Rule.")
    if namespace.destination_container is None:
        raise ValueError("--destination-container is required to create ORS Policy Rule.")