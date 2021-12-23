# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

CONTENT_INDENT_BROADBAND = "     "

MSG_WELCOME = "\nWelcome to AZ INIT! This command will guide you to set up common config\n"

MSG_SELECT_STEP = "\nSelect an option by typing it's number\n"

MSG_INPUT_SELECTION = "Your selection: "

MSG_CURRENT_SETTINGS = "Your current config settings:\n"

MSG_NO_CONFIGURATION = "You have no existing config in place. Let's get started!\n"

MSG_BUILD_IN_INTERACTION_BUNDLES = "human readability and interaction"

MSG_BUILD_IN_AUTOMATION_BUNDLES = "machine scripting and automation"

MSG_BUNDLE_SETTING_APPLIED = "Optimized for {}! Your new config settings:\n"

MSG_RECOMMEND_BUNDLE_SETTINGS = "For {}, we recommend the following settings:\n"

MSG_THANKS_FOR_TRYING = "Thank you for trying it!\n"

MSG_CUSTOM_SETTING_APPLIED = "Custom config settings applied! Your new config settings:\n"

MSG_MORE_CONFIG_SETTINGS = "More config settings: "

MSG_MORE_CONFIG_LINK = "https://aka.ms/config_ref"

MSG_MORE_COMMANDS_PROMPT = "\nCommands to try:\n"

INIT_STEP_OPTION_LIST = [
    {
        "option": "Optimize for interaction",
        "desc": "These settings improve the output legibility and optimize for human interaction"
    },
    {
        "option": "Optimize for automation",
        "desc": "These settings optimize for machine efficiency"
    },
    {
        "option": "Customize settings",
        "desc": "A walk through to customize common configurations"
    },
    {
        "option": "Exit",
        "desc": "Return to the command prompt",
        "tag": "default"
    }
]

MORE_COMMANDS_LIST = [
    {
        "option": "az config set <group>.<key>=<value>",
        "desc": "Set a config.",
    },
    {
        "option": "az config get",
        "desc": "Display your config summary.",
    },
    {
        "option": "az <sub command> --help",
        "desc": "Display help related to a command or sub-command.",
    },
    {
        "option": "az next",
        "desc": "Find the next set of commands.",
    },
    {
        "option": "az interactive",
        "desc": "Start an interactive mode designed to help you learn.",
    }
]
