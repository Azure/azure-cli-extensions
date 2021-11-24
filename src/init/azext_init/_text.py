# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

CONTENT_INDENT_BROADBAND = "     "

MSG_WELCOME = "\nWelcome to AZ INIT! This command will guide you to set up common config\n"

MSG_SELECT_STEP = "\nSelect an option by typing it's number\n"

MSG_INPUT_SELECTION = "Your selection: "

MSG_CURRENT_SETTINGS = "Your current config settings:"

MSG_NO_CONFIGURATION = "You have no existing config in place. Let's get started!\n"

MSG_BUILD_IN_INTERACTION_BUNDLES = "Optimized fo human readability and interaction!"

MSG_BUILD_IN_AUTOMATION_BUNDLES = "Optimized fo machine scripting and automation!"

MSG_BUNDLE_SETTING_APPLIED = "{} Your new config settings:\n"

MSG_CUSTOM_SETTING_APPLIED = "Custom config settings applied! Your new config settings:\n"

MSG_MORE_CONFIG_SETTINGS = "More config settings: "

MSG_MORE_CONFIG_LINK = "https://aka.ms/config_ref"

MSG_MORE_COMMANDS_PROMPT = "\nCommands to try:\n"

INIT_STEP_OPTION_LIST = [
    {
        "option": "Optimize for humans",
        "desc": "There settings improve the output legibility and optimize for human machine interaction"
    },
    {
        "option": "Optimize for machines",
        "desc": "These settings optimize for machine efficiency"
    },
    {
        "option": "Customize settings",
        "desc": "This is an individual walk through where you could customize a set of common configs"
    }
]

MORE_COMMANDS_LIST = [
    {
        "option": "az config",
        "desc": "Display your config summary.",
    },
    {
        "option": "az config list available",
        "desc": "Show all options that you can configure."
    },
    {
        "option": "az config set <group> <key>=<value>",
        "desc": "Set a config.",
    },
    {
        "option": "az interactive",
        "desc": "Start an interactive mode designed to help you learn.",
    },
    {
        "option": "az next",
        "desc": "Find the next set of commands.",
    },
    {
        "option": "az <sub command> --help",
        "desc": "Display help related to a command or sub-command.",
    }
]
