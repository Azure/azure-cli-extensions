# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


OUTPUT_LIST = [
    {"name": "json", "desc": "JSON formatted output that most closely matches API responses."},
    {"name": "jsonc",
     "desc": "Colored JSON formatted output that most closely matches API responses."},
    {"name": "table", "desc": "Human-readable output format."},
    {"name": "tsv", "desc": "Tab- and Newline-delimited. Great for GREP, AWK, etc."},
    {"name": "yaml", "desc": "YAML formatted output. An alternative to JSON. Great for configuration files."},
    {"name": "yamlc", "desc": "Colored YAML formatted output. An alternative to JSON. Great for configuration files."},
    {"name": "none", "desc": "No output, except for errors and warnings."}
]

LOGIN_METHOD_LIST = [
    "Device code authentication, we will provide a code you enter into a web page and log into",
    "Username and password (MFA enforced accounts or MSA accounts such as live-id not supported)",
    "Service Principal with secret",
    "Skip this step (login is available with the \'az login\' command)"
]

INTERACTIVE_CONFIG_LIST = [
    {
        "configuration": "core.output",
        "brief": "Output format",
        "description": "The Azure CLI uses JSON as its default output format. Interactive users usually prefers "
                       "table output, whereas automation users prefer json or yaml",
        "options": [
            {
                "name": "json",
                "option": "json",
                "desc": "JSON formatted output that most closely matches API responses.",
                "tag": "default"
            },
            {
                "name": "jsonc",
                "option": "jsonc",
                "desc": "Colored JSON formatted output that most closely matches API responses."
            },
            {
                "name": "table",
                "option": "table",
                "desc": "Human-readable output format."
            },
            {
                "name": "tsv",
                "option": "tsv",
                "desc": "Tab- and Newline-delimited. Great for GREP, AWK, etc."
            },
            {
                "name": "yaml",
                "option": "yaml",
                "desc": "YAML formatted output. An alternative to JSON. Great for configuration files."
            },
            {
                "name": "yamlc",
                "option": "yamlc",
                "desc": "Colored YAML formatted output. An alternative to JSON. Great for configuration files."
            },
            {
                "name": "none",
                "option": "none",
                "desc": "No output, except for errors and warnings."
            }
        ]
    },
    {
        "configuration": "core.errors_only",
        "brief": "Standard error stream (stderr)",
        "description": "",
        "options": [
            {
                "name": "All events",
                "option": "false",
                "desc": "The stderr stream shows all events, including errors and system messages",
                "tag": "default"
            },
            {
                "name": "Errors only",
                "option": "true",
                "desc": "The stderr stream shows error messages only"
            }
        ]
    },
    {
        "configuration": "core.error_recommendations",
        "brief": "Error output",
        "description": "",
        "options": [
            {
                "name": "Show recommendations",
                "option": "on",
                "desc": "Error message might include recommendations or Help links",
                "tag": "default"
            },
            {
                "name": "Hide recommendations",
                "option": "off",
                "desc": "Error messages will only show the error"
            }
        ]
    },
    {
        "configuration": "core.syntax_highlighting",
        "brief": "Syntax highlighting",
        "description": "",
        "options": [
            {
                "name": "On",
                "option": "on",
                "desc": "Colored syntax highlighting. Easier for humans to read",
                "tag": "default"
            },
            {
                "name": "Off",
                "option": "off",
                "desc": "Monochrome text. Harder for humans to read"
            }
        ]
    },
    {
        "configuration": "core.updates",
        "brief": "Updates",
        "description": "",
        "options": [
            {
                "name": "Ask first",
                "option": "prompt",
                "desc": "Azure CLI will ask you before installing available updates",
                "tag": "default"
            },
            {
                "name": "Automatic",
                "option": "auto",
                "desc": "Azure CLI will automatically install all available updates"
            },
            {
                "name": "None",
                "option": "none",
                "desc": "Azure CLI will not notify you about available updates"
            }
        ]
    },
    {
        "configuration": "logging.enable_log_file",
        "brief": "Enable logging to file",
        "description": "Would you like to enable logging to file?",
        "options": [
            {
                "name": "yes",
                "option": "true",
                "desc": "enable logging to file",
                "tag": "default"
            },
            {
                "name": "no",
                "option": "false",
                "desc": "not enable logging to file"
            }
        ]
    }
]
