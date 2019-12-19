# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
from azure.cli.core.util import get_file_json, shell_safe_json_parse


def validate_ors_policy(namespace):
    error_elements = []
    if namespace.properties is None:
        error_msg = "Please provide --properties in JSON format or the following arguments: "
        if namespace.source_account is None:
            error_elements.append("--source-account")
        if namespace.destination_account is None:
            error_elements.append("--destination-account")

        if error_elements:
            error_msg += ", ".join(error_elements)
            error_msg += " to initialize ORS Policy for storage account."
            raise ValueError(error_msg)
    else:
        if os.path.exists(namespace.properties):
            ors_policy = get_file_json(namespace.properties)
        else:
            ors_policy = shell_safe_json_parse(namespace.properties)

        try:
            namespace.source_account = ors_policy["sourceAccount"]
        except KeyError:
            namespace.source_account = ors_policy["source_account"]
        except KeyError:
            error_elements.append("source_account")

        try:
            namespace.destination_account = ors_policy["destinationAccount"]
        except KeyError:
            namespace.destination_account = ors_policy["destination_account"]
        except KeyError:
            error_elements.append("destination_account")

        if "rules" not in ors_policy.keys() or not ors_policy["rules"]:
            error_elements.append("rules")
        error_msg = "Missing input parameters: "
        if error_elements:
            error_msg += ", ".join(error_elements)
            error_msg += " in properties to initialize ORS Policy for storage account."
            raise ValueError(error_msg)
        namespace.properties = ors_policy

        if "policyId" in ors_policy.keys() and ors_policy["policyId"]:
            namespace.policy_id = ors_policy['policyId']




