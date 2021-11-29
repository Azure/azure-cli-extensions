# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

BUILD_IN_INTERACTION_BUNDLES = [
    {
        "configuration": "core.output",
        "value": "table"
    },
    {
        "configuration": "core.only_show_errors",
        "value": "false",
    },
    {
        "configuration": "core.error_recommendation",
        "value": "on",
    },
    {
        "configuration": "core.no_color",
        "value": "false",
    },
    {
        "configuration": "core.disable_progress_bar",
        "value": "false",
    }
]

BUILD_IN_AUTOMATION_BUNDLES = [
    {
        "configuration": "core.output",
        "value": "json"
    },
    {
        "configuration": "core.only_show_errors",
        "value": "true",
    },
    {
        "configuration": "core.error_recommendation",
        "value": "off",
    },
    {
        "configuration": "core.no_color",
        "value": "true",
    },
    {
        "configuration": "core.disable_progress_bar",
        "value": "true",
    }
]
