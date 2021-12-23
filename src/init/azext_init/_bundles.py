# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

BUILD_IN_INTERACTION_BUNDLES = [
    {
        "brief": "Set the default output style to table",
        "configuration": "core.output",
        "value": "table"
    },
    {
        "brief": "Return all outputs, not just errors",
        "configuration": "core.only_show_errors",
        "value": "false",
    },
    {
        "brief": "Provide recommendations based on the type of error returned",
        "configuration": "core.error_recommendation",
        "value": "on",
    },
    {
        "brief": "Increase readability with CLI syntax highlighting",
        "configuration": "core.no_color",
        "value": "false",
    },
    {
        "brief": "Display a progress bar for long running commands",
        "configuration": "core.disable_progress_bar",
        "value": "false",
    }
]

BUILD_IN_AUTOMATION_BUNDLES = [
    {
        "brief": "Set the default output style to json",
        "configuration": "core.output",
        "value": "json"
    },
    {
        "brief": "Only return errors",
        "configuration": "core.only_show_errors",
        "value": "true",
    },
    {
        "brief": "Disable error recommendations",
        "configuration": "core.error_recommendation",
        "value": "off",
    },
    {
        "brief": "Disable CLI syntax highlighting",
        "configuration": "core.no_color",
        "value": "true",
    },
    {
        "brief": "Display progress bar for long running commands",
        "configuration": "core.disable_progress_bar",
        "value": "true",
    }
]
