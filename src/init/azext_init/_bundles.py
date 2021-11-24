# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import DEFAULT_CACHE_TTL

# TODO Distinguish between automation and interaction
default_interaction_config_bundle = {
    "bundle_name": "Interaction bundle",
    "config_list": [
        {
            "configuration": "core.output",
            "desc": "Output format: json",
            "value": "json"
        },
        {
            "configuration": "core.errors_only",
            "desc": "Standard error stream (stderr): All events",
            "value": "false",
        },
        {
            "configuration": "core.error_recommendations",
            "desc": "Error output: Show recommendations",
            "value": "on",
        },
        {
            "configuration": "core.syntax_highlighting",
            "desc": "Syntax highlighting: On",
            "value": "on",
        },
        {
            "configuration": "core.updates",
            "desc": "Updates: Ask first",
            "value": "propmt",
        }
    ]
}

default_automation_config_bundle = {
    "bundle_name": "Automation bundle",
    "config_list": [
        {
            "configuration": "core.output",
            "desc": "Output format: json",
            "value": "json"
        },
        {
            "configuration": "core.errors_only",
            "desc": "Standard error stream (stderr): Errors only",
            "value": "true",
        },
        {
            "configuration": "core.error_recommendations",
            "desc": "Error output: Hide recommendations",
            "value": "off",
        },
        {
            "configuration": "core.syntax_highlighting",
            "desc": "Syntax highlighting: On",
            "value": "on",
        },
        {
            "configuration": "core.updates",
            "desc": "Updates: Automatic",
            "value": "auto",
        }
    ]
}
