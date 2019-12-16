# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def validate_ors_policy(namespace):
    if namespace.properties is None:
        error_msg = "Please provide --properties in JSON format or the following arguments: "
        error_elements = []
        if namespace.source_account is None:
            error_elements.append("--source-account")
        if namespace.destination_account is None:
            error_elements.append("--destination-account")

        if error_elements:
            error_msg += ", ".join(error_elements)
            error_msg += " to initialize ORS Policy for storage account."
            raise ValueError(error_msg)


def validate_ors_rule(namespace):
    if namespace.source_container is None:
        raise ValueError("--source-container is required to create ORS Policy Rule.")
    if namespace.destination_container is None:
        raise ValueError("--destination-container is required to create ORS Policy Rule.")