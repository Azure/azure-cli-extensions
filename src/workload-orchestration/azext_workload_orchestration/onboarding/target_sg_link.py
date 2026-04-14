# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Service Group link helper — links a target to a service group after creation.

After creating the ServiceGroupMember relationship, a target update (PUT) is
mandatory to refresh the target's hierarchy info. Without this, the target
appears unlinked in portal. (Confirmed from BVT code LinkServiceGroup().)

Usage (called internally by target create --service-group):
    link_target_to_service_group(cmd, target_id, service_group_name)
"""

# pylint: disable=broad-exception-caught

import json
import logging

from azure.cli.core.azclierror import CLIInternalError

from azext_workload_orchestration.onboarding.consts import (
    ARM_ENDPOINT,
    SG_MEMBER_API_VERSION,
    TARGET_API_VERSION,
)
from azext_workload_orchestration.onboarding.utils import (
    invoke_cli_command,
)

logger = logging.getLogger(__name__)


def link_target_to_service_group(cmd, target_id, service_group_name):
    """Link a target to a service group and refresh hierarchy.

    Two REST calls:
    1. PUT {targetId}/providers/Microsoft.Relationships/serviceGroupMember/{sgName}
    2. PUT {targetId} (update target to refresh hierarchy — MANDATORY)
    """
    sg_member_url = (
        f"{ARM_ENDPOINT}{target_id}"
        f"/providers/Microsoft.Relationships/serviceGroupMember/{service_group_name}"
    )

    # Step 1: Create ServiceGroupMember relationship
    try:
        invoke_cli_command(cmd, [
            "rest",
            "--method", "put",
            "--url", f"{sg_member_url}?api-version={SG_MEMBER_API_VERSION}",
            "--body", json.dumps({
                "properties": {
                    "targetId": f"/providers/Microsoft.Management/serviceGroups/{service_group_name}"
                }
            }),
            "--resource", ARM_ENDPOINT,
            "--header", "Content-Type=application/json",
        ], expect_json=False)
        logger.info("ServiceGroupMember created: %s -> %s", target_id, service_group_name)
    except Exception as exc:
        raise CLIInternalError(
            f"Failed to link target to service group '{service_group_name}': {exc}",
            recommendation=(
                f"Try manually:\n"
                f"  az rest --method put "
                f"--url \"{sg_member_url}?api-version={SG_MEMBER_API_VERSION}\" "
                f"--body \"{{\\\"properties\\\":{{\\\"targetId\\\":\\\""
                f"/providers/Microsoft.Management/serviceGroups/{service_group_name}"
                f"\\\"}}}}\" "
                f"--resource {ARM_ENDPOINT} --header Content-Type=application/json"
            )
        )

    # Step 2: Update target to refresh hierarchy (MANDATORY)
    try:
        # GET current target
        target_data = invoke_cli_command(cmd, [
            "rest",
            "--method", "get",
            "--url", f"{ARM_ENDPOINT}{target_id}?api-version={TARGET_API_VERSION}",
            "--resource", ARM_ENDPOINT,
        ])

        # PUT target (update to refresh hierarchy)
        if target_data and isinstance(target_data, dict):
            # Strip read-only fields, preserve writable top-level fields
            body = {
                "location": target_data.get("location", ""),
                "properties": target_data.get("properties", {}),
            }
            if "extendedLocation" in target_data:
                body["extendedLocation"] = target_data["extendedLocation"]
            if "tags" in target_data:
                body["tags"] = target_data["tags"]

            invoke_cli_command(cmd, [
                "rest",
                "--method", "put",
                "--url", f"{ARM_ENDPOINT}{target_id}?api-version={TARGET_API_VERSION}",
                "--body", json.dumps(body),
                "--resource", ARM_ENDPOINT,
                "--header", "Content-Type=application/json",
            ], expect_json=False)
            logger.info("Target hierarchy refreshed after SG link")

    except Exception as exc:
        logger.warning(
            "Target hierarchy refresh after SG link may have failed: %s. "
            "Target may appear unlinked until next update.", exc
        )
