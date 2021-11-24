# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import DEFAULT_CACHE_TTL

MSG_WELCOME = "\nWelcome to AZ INIT! This command will guide you to set up common config\n"

MSG_SELECT_STEP = "\nSelect an option by typing it's number\n"

MSG_INPUT_SELECTION = "Your selection: "

MSG_CURRENT_SETTINGS = "Your current config settings:"

MSG_BUNDLE_SETTING_APPLIED = "{} settings applied! Your new config settings:\n"

MSG_CUSTOM_SETTING_APPLIED = "Custom config settings applied! Your new config settings:\n"

MSG_NO_CONFIGURATION = "You have no existing config in place. Let's get started!\n"

MSG_MORE_CONFIG_SETTINGS = "More config settings: "

MSG_MORE_CONFIG_LINK = "https://aka.ms/config_ref"

CONTENT_INDENT_BROADBAND = "     "

MSG_PROMPT_MANAGE_GLOBAL = "\nDo you wish to change your settings?"

MSG_PROMPT_GLOBAL_OUTPUT = "\nWhat default output format would you like?"

MSG_PROMPT_TELEMETRY = "\nMicrosoft would like to collect anonymous Azure CLI usage data to " \
                       "improve our CLI.  Participation is voluntary and when you choose to " \
                       "participate, your device automatically sends information to Microsoft " \
                       "about how you use Azure CLI.  To update your choice, run \"az init\" " \
                       "again.\nSelect y to enable data collection."

MSG_PROMPT_FILE_LOGGING = "\nWould you like to enable logging to file?"

MSG_PROMPT_CACHE_TTL = "\nCLI object cache time-to-live (TTL) in minutes [Default: {}]: ".format(DEFAULT_CACHE_TTL)

INIT_STEP_OPTION_LIST = [
    {
        "name": "Optimize for humans",
        "desc": "There settings improve the output legibility and optimize for human machine interaction"
    },
    {
        "name": "Optimize for machines",
        "desc": "These settings optimize for machine efficiency"
    },
    {
        "name": "Customize settings",
        "desc": "This is an individual walk through where you could customize a set of common configs"
    }
]

MSG_MROE_COMMANDS_PROMPT = "\nCommands to try:\n"

MSG_MORE_COMMANDS = [
    {
        "name": "az config",
        "desc": "Display your config summary.",
    },
    {
        "name": "az config list available",
        "desc": "Show all options that you can configure."
    },
    {
        "name": "az config set <group> <key>=<value>",
        "desc": "Set a config.",
    },
    {
        "name": "az interactive",
        "desc": "Start an interactive mode designed to help you learn.",
    },
    {
        "name": "az next",
        "desc": "Find the next set of commands.",
    },
    {
        "name": "az <sub command> --help",
        "desc": "Display help related to a command or sub-command.",
    }
]
