# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Completed runtime template validation, shared by inspection and replacement."""

from azure.cli.core.azclierror import ClientRequestError

from ._runtime_client import workflow_validate_path


def validate_runtime_workflow(client, workflow, body):
    receipt = client.post_with_receipt(workflow_validate_path(workflow), body=body)
    if (not isinstance(receipt, dict) or type(receipt.get("statusCode")) is not int  # pylint: disable=unidiomatic-typecheck
            or receipt["statusCode"] not in (200, 204) or "payload" not in receipt):
        raise ClientRequestError(
            "The runtime did not return a completed validation receipt. "
            "No operation URL was followed and no polling or retry was attempted.")
    payload = receipt["payload"]
    if payload is not None and (not isinstance(payload, dict) or "error" in payload):
        raise ClientRequestError("The runtime returned an invalid or failing validation response.")
