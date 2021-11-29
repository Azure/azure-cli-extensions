# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

BUILD_IN_INTERACTION_BUNDLES = [
    {
        "configuration": "core.output",
        "brief": "Output format",
        "option": "Table",
        "value": "table"
    },
    {
        "configuration": "core.only_show_errors",
        "brief": "Standard error stream (stderr)",
        "option": "All events",
        "value": "false",
    },
    {
        "configuration": "core.error_recommendation",
        "brief": "Error output",
        "option": "Show recommendations",
        "value": "on",
    },
    {
        "configuration": "core.no_color",
        "brief": "Syntax highlighting",
        "option": "On",
        "value": "false",
    },
    {
        "configuration": "core.disable_progress_bar",
        "brief": "Progress Bar",
        "option": "On",
        "value": "false",
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
        "configuration": "core.only_show_errors",
        "brief": "Standard error stream (stderr)",
        "option": "Errors only",
        "value": "true",
    },
    {
        "configuration": "core.error_recommendation",
        "brief": "Error output",
        "option": "Hide recommendations",
        "value": "off",
    },
    {
        "configuration": "core.no_color",
        "brief": "Syntax highlighting",
        "option": "Off",
        "value": "true",
    },
    {
        "configuration": "core.disable_progress_bar",
        "brief": "Progress Bar",
        "option": "Off",
        "value": "true",
    }
]
