# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

BUILD_IN_INTERACTION_BUNDLES = [
    {
        "configuration": "core.output",
        "brief": "Output format",
        "option": "JSON",
        "value": "json"
    },
    {
        "configuration": "core.errors_only",
        "brief": "Standard error stream (stderr)",
        "option": "All events",
        "value": "false",
    },
    {
        "configuration": "core.error_recommendations",
        "brief": "Error output",
        "option": "Show recommendations",
        "value": "on",
    },
    {
        "configuration": "core.syntax_highlighting",
        "brief": "Syntax highlighting",
        "option": "On",
        "value": "on",
    },
    {
        "configuration": "core.updates",
        "brief": "Auto Upgrade",
        "option": "Ask first",
        "value": "prompt",
    }
]

BUILD_IN_AUTOMATION_BUNDLES = [
    {
        "configuration": "core.output",
        "brief": "Output format",
        "option": "JSON",
        "value": "json"
    },
    {
        "configuration": "core.errors_only",
        "brief": "Standard error stream (stderr)",
        "option": "Errors only",
        "value": "true",
    },
    {
        "configuration": "core.error_recommendations",
        "brief": "Error output",
        "option": "Hide recommendations",
        "value": "off",
    },
    {
        "configuration": "core.syntax_highlighting",
        "brief": "Syntax highlighting",
        "option": "On",
        "value": "on",
    },
    {
        "configuration": "core.updates",
        "brief": "Auto Upgrade",
        "option": "Automatic",
        "value": "auto",
    }
]
