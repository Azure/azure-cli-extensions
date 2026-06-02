# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
#
# NOTE: After regenerating aaz commands with aaz-dev-tools, re-add the following to each
# command file in aaz/latest/site/key/ (_create.py, _delete.py, _download.py, _list.py, _show.py):
#
#   1. Import: from azext_site._error_handler import handle_sitekey_error
#   2. Override _handler to wrap _execute_operations() in try/except:
#        def _handler(self, command_args):
#            super()._handler(command_args)
#            try:
#                self._execute_operations()
#            except Exception as ex:
#                handle_sitekey_error(ex)
#                raise
#            return self._output()
#

import re
from azure.cli.core.azclierror import ValidationError, ResourceNotFoundError


def _format_alert(options, error_code):
    """Format a polished error alert for CLI output.

    Args:
        options: list of (title, steps) tuples. Each is an Option in the alert.
        error_code: error code string appended at the end.
    """
    lines = []
    for idx, (title, steps) in enumerate(options, 1):
        lines.append("Option {}".format(idx))
        lines.append("  Title: {}".format(title))
        lines.append("  Recommendation:")
        for i, step in enumerate(steps, 1):
            lines.append("    {}. {}".format(i, step))
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
                [
                    (
                        "Site key token expiry date exceeds the allowed maximum.",
                        [
                            "Set the --token-expiry-date value to a date no more than "
                            "7 days from the current UTC time.",
                            "Alternatively, remove the --token-expiry-date parameter "
                            "to use the default (7 days from now).",
                            "Rerun the create command.",
                        ],
                    ),
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

        delete_cmd = "'az site key delete --name {} -g <resource-group> --yes'".format(
            existing_key if existing_key else "<existing-key>"
        )
        raise ValidationError(
            _format_alert(
                [
                    (
                        "Site already has an existing site key.",
                        [
                            "Run 'az site key list -g <resource-group>' to identify the existing site key.",
                            "Delete the existing key with {}.".format(delete_cmd),
                            "Create the new site key after the deletion completes.",
                        ],
                    ),
                ],
                "ValidationFailed",
            )
        )

    # Error 3: Site does not exist
    if ("ReadResourceDataFailed" in error_msg or "ResourceNotFound" in error_msg) and \
       "Microsoft.Edge/sites/" in error_msg:
        raise ResourceNotFoundError(
            _format_alert(
                [
                    (
                        "Specified site does not exist in the resource group.",
                        [
                            "Run 'az site list -g <resource-group>' to list available sites.",
                            "Verify the --site-name value matches an existing site name exactly.",
                            "Confirm the site is in the same resource group specified with -g.",
                            "Rerun the create command with the correct site name.",
                        ],
                    ),
                ],
                "ReadResourceDataFailed, ResourceNotFound",
            )
        )

    # Error 4: Site key does not exist
    if "ResourceNotFound" in error_msg and "siteKeys/" in error_msg:
        raise ResourceNotFoundError(
            _format_alert(
                [
                    (
                        "Specified site key could not be found.",
                        [
                            "Run 'az site key list -g <resource-group>' to list existing site keys.",
                            "Verify the --name value matches an existing site key name exactly.",
                            "Confirm the site key is in the resource group specified with -g.",
                            "Rerun the command with the correct name.",
                        ],
                    ),
                ],
                "ResourceNotFound",
            )
        )

    # Not a recognized error — caller should re-raise the original
