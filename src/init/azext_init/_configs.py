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

INTERACTIVE_CONFIG_BUNDLE = [
    {
        "configuration": "core.output",
        "brief": "output format",
        "description": "The Azure CLI uses JSON as its default output format. Interactive users usually prefers "
                       "table output, whereas automation users prefer json or yaml",
        "values":{
            "default": "json",
            "options": [
                {
                    "name": "json",
                    "desc": "JSON formatted output that most closely matches API responses."
                },
                {
                    "name": "jsonc",
                    "desc": "Colored JSON formatted output that most closely matches API responses."
                },
                {"name": "table", "desc": "Human-readable output format."},
                {"name": "tsv", "desc": "Tab- and Newline-delimited. Great for GREP, AWK, etc."},
                {"name": "yaml", "desc": "YAML formatted output. An alternative to JSON. Great for configuration files."},
                {"name": "yamlc", "desc": "Colored YAML formatted output. An alternative to JSON. Great for configuration files."},
                {"name": "none", "desc": "No output, except for errors and warnings."}
            ]
        }
    },
    {
        "configuration": "logging.enable_log_file",
        "brief": "enable logging to file",
        "description": "Would you like to enable logging to file?",
        "values":{
            "default": "yes",
            "options": [
                {
                    "value": "yes",
                    "name": "enable logging to file"
                },
                {
                    "value": "no",
                    "name": "not enable logging to file"
                }
            ]
        }
    }
]
