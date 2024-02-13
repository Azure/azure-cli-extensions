# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


WALK_THROUGH_CONFIG_LIST = [
    {
        "configuration": "core.output",
        "brief": "Output format",
        "description": "The Azure CLI uses JSON as its default output format. Interactive users usually prefers "
                       "table output, whereas automation users prefer json or yaml",
        "options": [
            {
                "option": "JSON",
                "value": "json",
                "desc": "JSON formatted output that most closely matches API responses.",
                "tag": "default"
            },
            {
                "option": "JSONC",
                "value": "jsonc",
                "desc": "Colored JSON formatted output that most closely matches API responses."
            },
            {
                "option": "Table",
                "value": "table",
                "desc": "Human-readable output format."
            },
            {
                "option": "TSV",
                "value": "tsv",
                "desc": "Tab- and Newline-delimited. Great for GREP, AWK, etc."
            },
            {
                "option": "YAML",
                "value": "yaml",
                "desc": "YAML formatted output. An alternative to JSON. Great for configuration files."
            },
            {
                "option": "YAMLC",
                "value": "yamlc",
                "desc": "Colored YAML formatted output. An alternative to JSON. Great for configuration files."
            },
            {
                "option": "None",
                "value": "none",
                "desc": "No output, except for errors and warnings."
            }
        ]
    },
    {
        "configuration": "core.only_show_errors",
        "brief": "Standard error stream (stderr)",
        "description": "This options to control whether only error messages are showed in stderr stream",
        "options": [
            {
                "option": "All events",
                "value": "false",
                "desc": "The stderr stream shows all events, including errors and system messages",
                "tag": "default"
            },
            {
                "option": "Errors only",
                "value": "true",
                "desc": "The stderr stream shows error messages only"
            }
        ]
    },
    {
        "configuration": "core.error_recommendation",
        "brief": "Error output",
        "description": "This options to enable/disable message recommendations which ease your error recovery",
        "options": [
            {
                "option": "Show recommendations",
                "value": "on",
                "desc": "Error message might include recommendations or Help links",
                "tag": "default"
            },
            {
                "option": "Hide recommendations",
                "value": "off",
                "desc": "Error messages will only show the error"
            }
        ]
    },
    {
        "configuration": "core.no_color",
        "brief": "Syntax highlighting",
        "description": "This options to enable/disable colored syntax highlighting",
        "options": [
            {
                "option": "On",
                "value": "false",
                "desc": "Colored syntax highlighting. Easier for humans to read",
                "tag": "default"
            },
            {
                "option": "Off",
                "value": "true",
                "desc": "Monochrome text. Harder for humans to read"
            }
        ]
    },
    {
        "configuration": "core.disable_progress_bar",
        "brief": "Progress Bar",
        "description": "This option is used to enable/disable the progress bar for long running commands",
        "options": [
            {
                "option": "On",
                "value": "false",
                "desc": "The progress bar will be displayed in stderr during long running commands",
                "tag": "default"
            },
            {
                "option": "Off",
                "value": "true",
                "desc": "Disable the progress bar during long running commands"
            }
        ]
    }
]
