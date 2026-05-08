# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
from azure.cli.core.azclierror import ValidationError, ResourceNotFoundError


def _format_alert(title, steps, error_code):
    """Format a polished error alert for CLI output."""
    lines = [title, ""]
    lines.append("Recommendation:")
    for i, step in enumerate(steps, 1):
        lines.append("  {}. {}".format(i, step))
    lines.append("")
    lines.append("Error code: {}".format(error_code))
    return "\n".join(lines)


def handle_sitekey_error(ex):
    """Intercept known sitekey API errors and raise polished alerts.

    Returns None if the error is not recognized (caller should re-raise).
    """
    error_msg = str(ex)

    # Error 1: Token expiry beyond 7 days
    if "ValidationFailed" in error_msg and "Token expiry date cannot be set beyond" in error_msg:
        raise ValidationError(
            _format_alert(
                "Site key token expiry date exceeds the allowed maximum.",
                [
                    "Set the --token-expiry-date value to a date no more than 7 days from the current UTC time.",
                    "Alternatively, remove the --token-expiry-date parameter to use the default (7 days from now).",
                    "Rerun the create command.",
                ],
                "ValidationFailed",
            )
        )

    # Error 2: Only 1 sitekey per site
    if "ValidationFailed" in error_msg and "already has an existing sitekey" in error_msg:
        existing_key = ""
        match = re.search(r"siteKeys/([^\s.]+)", error_msg)
        if match:
            existing_key = match.group(1)

        steps = [
            "Run 'az site key list -g <resource-group>' to identify the existing site key.",
        ]
        if existing_key:
            steps.append(
                "If you need a new key, delete the existing one with "
                "'az site key delete --name {} -g <resource-group> --yes'.".format(existing_key)
            )
        else:
            steps.append(
                "If you need a new key, delete the existing one with "
                "'az site key delete --name <existing-key> -g <resource-group> --yes'."
            )
        steps.append("Create the new site key after the deletion completes.")
        raise ValidationError(
            _format_alert(
                "Site already has an existing site key.",
                steps,
                "ValidationFailed",
            )
        )

    # Error 3: Site does not exist
    if ("ReadResourceDataFailed" in error_msg or "ResourceNotFound" in error_msg) and \
       "Microsoft.Edge/sites/" in error_msg:
        raise ResourceNotFoundError(
            _format_alert(
                "Specified site does not exist in the resource group.",
                [
                    "Run 'az site list -g <resource-group>' to list available sites.",
                    "Verify the --site-name value matches an existing site name exactly.",
                    "Confirm the site is in the same resource group specified with -g.",
                    "Rerun the create command with the correct site name.",
                ],
                "ReadResourceDataFailed, ResourceNotFound",
            )
        )

    # Error 4: Site key does not exist
    if "ResourceNotFound" in error_msg and "siteKeys/" in error_msg:
        raise ResourceNotFoundError(
            _format_alert(
                "Specified site key could not be found.",
                [
                    "Run 'az site key list -g <resource-group>' to list existing site keys.",
                    "Verify the --name value matches an existing site key name exactly.",
                    "Confirm the site key is in the resource group specified with -g.",
                    "Rerun the command with the correct name.",
                ],
                "ResourceNotFound",
            )
        )

    # Not a recognized error — caller should re-raise the original
    return None
