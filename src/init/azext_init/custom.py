# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import configparser

from knack.log import get_logger
from knack.prompting import prompt, prompt_y_n, prompt_choice_list
from azure.cli.core.util import ScopedConfig
from azure.cli.core.style import Style, print_styled_text
from azure.cli.core.util import ConfiguredDefaultSetter
from azure.cli.core.commands import DEFAULT_CACHE_TTL
from ._configs import INTERACTIVE_CONFIG_LIST
from ._text import (MSG_WELCOME, MSG_SELECT_STEP, MSG_INPUT_SELECTION, MSG_CURRENT_SETTINGS, MSG_NO_CONFIGURATION,
                    MSG_BUNDLE_SETTING_APPLIED, INIT_STEP_OPTION_LIST, MSG_CUSTOM_SETTING_APPLIED, MSG_MORE_CONFIG_SETTINGS,
                    MSG_MORE_CONFIG_LINK, CONTENT_INDENT_BROADBAND, MSG_MROE_COMMANDS_PROMPT, MSG_MORE_COMMANDS)
from ._utils import prompt_option_list, get_int_option, print_successful_styled_text
from ._bundles import (default_automation_config_bundle, default_interaction_config_bundle)

logger = get_logger(__name__)


def handle_init(cmd):

    print_styled_text((Style.PRIMARY, MSG_WELCOME))

    load_existing_configuration(cmd)

    print_styled_text((Style.PRIMARY, MSG_SELECT_STEP))

    prompt_option_list(INIT_STEP_OPTION_LIST, content_indent=CONTENT_INDENT_BROADBAND)

    selected_option = get_int_option(MSG_INPUT_SELECTION, 1, 3, 3)

    if selected_option == 1:
        set_build_in_bundles(cmd, default_interaction_config_bundle)

    if selected_option == 2:
        set_build_in_bundles(cmd, default_automation_config_bundle)

    if selected_option == 3:
        handle_interactive_mode(cmd, INTERACTIVE_CONFIG_LIST)


def load_existing_configuration(cmd):
    with ScopedConfig(cmd.cli_ctx.config, False):
        sections = cmd.cli_ctx.config.sections()
        if sections:
            print_styled_text((Style.PRIMARY, MSG_CURRENT_SETTINGS))

            for section in sections:
                items = cmd.cli_ctx.config.items(section)
                print_styled_text((Style.ACTION, "\n" + CONTENT_INDENT_BROADBAND + "[" + section + "]"))
                for item in items:
                    print_styled_text((Style.PRIMARY, CONTENT_INDENT_BROADBAND + item['name'] + " = " + item['value']))
        else:
            print_styled_text((Style.PRIMARY, MSG_NO_CONFIGURATION))


def set_build_in_bundles(cmd, bundle):

    config = cmd.cli_ctx.config
    custom_settings = {}

    for config in bundle["config_list"]:
        section, option = config["configuration"].split('.')
        modify_status = None
        original_config_value = None
        from configparser import NoOptionError, NoSectionError
        try:
            original_config_value = cmd.cli_ctx.config.get(section, option)
        except (NoOptionError, NoSectionError):
            pass

        if not original_config_value:
            modify_status = "(added)"
        elif original_config_value != config["value"]:
            modify_status = "(changed)"
        cmd.cli_ctx.config.set_value(section, option, config["value"])

        custom_settings[config["configuration"]] = {
            "desc": config["desc"],
            "modify_status": modify_status
        }
            
    print_successful_styled_text(MSG_BUNDLE_SETTING_APPLIED.format(bundle["bundle_name"]))

    for setting in custom_settings.values():
        new_config_list = [(Style.PRIMARY, setting["desc"])]
        if setting["modify_status"]:
            new_config_list.append((Style.IMPORTANT, setting["modify_status"]))
        print_styled_text(new_config_list)
        print()


def handle_interactive_mode(cmd, config_list):

    custom_settings = {}
    for config in config_list:

        print_styled_text((Style.PRIMARY, "\n{}:\n".format(config["brief"])))
        print_styled_text((Style.PRIMARY, "{}\n".format(config["description"])))
        prompt_option_list(config["options"], content_indent=CONTENT_INDENT_BROADBAND)

        default_value = 1
        for index, option_item in enumerate(config["options"]):
            if "tag" in option_item and option_item["tag"] == "default":
                default_value = index + 1
                break

        selected_option = get_int_option(MSG_INPUT_SELECTION, 1, len(config["options"]), default_value)
        selected_item = config["options"][selected_option - 1]

        section, option = config["configuration"].split('.')
        modify_status = None
        original_config_value = None
        from configparser import NoOptionError, NoSectionError
        try:
            original_config_value = cmd.cli_ctx.config.get(section, option)
        except (NoOptionError, NoSectionError):
            pass

        if not original_config_value:
            modify_status = "(added)"
        elif original_config_value != selected_item["value"]:
            modify_status = "(changed)"

        custom_settings[config["configuration"]] = {
            "brief": config["brief"],
            "option": selected_item["name"],
            "modify_status": modify_status
        }

        cmd.cli_ctx.config.set_value(section, option, selected_item["value"])
        success_prompt_text = [(Style.PRIMARY, "{} set to: ".format(config["brief"])),
                                (Style.IMPORTANT, selected_item["name"])]
        print_successful_styled_text(success_prompt_text)

    print_successful_styled_text(MSG_CUSTOM_SETTING_APPLIED)

    for setting in custom_settings.values():
        new_config_list = [(Style.PRIMARY, "{}: {} ".format(CONTENT_INDENT_BROADBAND + setting["brief"],
                                                            setting["option"]))]
        if setting["modify_status"]:
            new_config_list.append((Style.IMPORTANT, setting["modify_status"]))
        print_styled_text(new_config_list)
        print()

    print_styled_text([(Style.PRIMARY, CONTENT_INDENT_BROADBAND + MSG_MORE_CONFIG_SETTINGS),
                       (Style.HYPERLINK, MSG_MORE_CONFIG_LINK)])

    print_styled_text((Style.PRIMARY, CONTENT_INDENT_BROADBAND + MSG_MROE_COMMANDS_PROMPT))
    for more_commands_item in MSG_MORE_COMMANDS:
        print_styled_text([(Style.PRIMARY, CONTENT_INDENT_BROADBAND + more_commands_item['name'])])
        print_styled_text([(Style.SECONDARY, CONTENT_INDENT_BROADBAND + more_commands_item['desc'])])
        print()
