# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.log import get_logger
from azure.cli.core.util import ScopedConfig
from azure.cli.core.style import Style, print_styled_text

from ._utils import prompt_option_list, get_int_option, print_successful_styled_text
from ._text import (MSG_WELCOME, MSG_SELECT_STEP, MSG_INPUT_SELECTION, MSG_CURRENT_SETTINGS, MSG_NO_CONFIGURATION,
                    MSG_BUNDLE_SETTING_APPLIED, INIT_STEP_OPTION_LIST, MSG_CUSTOM_SETTING_APPLIED,
                    MSG_MORE_CONFIG_SETTINGS, MSG_MORE_CONFIG_LINK, CONTENT_INDENT_BROADBAND, MSG_MORE_COMMANDS_PROMPT,
                    MORE_COMMANDS_LIST, MSG_BUILD_IN_INTERACTION_BUNDLES, MSG_BUILD_IN_AUTOMATION_BUNDLES)
from ._bundles import BUILD_IN_INTERACTION_BUNDLES, BUILD_IN_AUTOMATION_BUNDLES
from ._configs import WALK_THROUGH_CONFIG_LIST

logger = get_logger(__name__)


def handle_init(cmd):

    print_styled_text((Style.PRIMARY, MSG_WELCOME))

    load_existing_configuration(cmd)

    print_styled_text((Style.PRIMARY, MSG_SELECT_STEP))
    prompt_option_list(INIT_STEP_OPTION_LIST, content_indent=CONTENT_INDENT_BROADBAND)
    selected_option = get_int_option(MSG_INPUT_SELECTION, 1, 4, 4)

    if selected_option == 1:
        set_build_in_bundles(cmd, BUILD_IN_INTERACTION_BUNDLES, MSG_BUILD_IN_INTERACTION_BUNDLES)

    if selected_option == 2:
        set_build_in_bundles(cmd, BUILD_IN_AUTOMATION_BUNDLES, MSG_BUILD_IN_AUTOMATION_BUNDLES)

    if selected_option == 3:
        handle_walk_through(cmd, WALK_THROUGH_CONFIG_LIST)

    if selected_option == 4:
        return


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


def set_build_in_bundles(cmd, bundles, bundle_name):
    bundle_settings = {}

    for bundle_item in bundles:
        section, option = bundle_item["configuration"].split('.')
        original_config_value = _get_existing_config_value(cmd, section, option)

        cmd.cli_ctx.config.set_value(section, option, bundle_item["value"])

        bundle_settings[bundle_item["configuration"]] = {
            "brief": bundle_item["brief"],
            "option": bundle_item["option"],
            "modify_status": _get_modify_status(original_config_value, bundle_item["value"])
        }

    print_successful_styled_text(MSG_BUNDLE_SETTING_APPLIED.format(bundle_name))
    _get_config_setting_status(bundle_settings)

    _get_more_commands()


def handle_walk_through(cmd, config_list):

    custom_settings = {}
    for config_item in config_list:

        print_styled_text((Style.PRIMARY, "\n{}:\n".format(config_item["brief"])))
        print_styled_text((Style.PRIMARY, "{}\n".format(config_item["description"])))
        prompt_option_list(config_item["options"], content_indent=CONTENT_INDENT_BROADBAND)

        default_value = 1
        for index, option_item in enumerate(config_item["options"]):
            if "tag" in option_item and option_item["tag"] == "default":
                default_value = index + 1
                break

        selected_option = get_int_option(MSG_INPUT_SELECTION, 1, len(config_item["options"]), default_value)
        selected_item = config_item["options"][selected_option - 1]

        section, option = config_item["configuration"].split('.')
        original_config_value = _get_existing_config_value(cmd, section, option)

        cmd.cli_ctx.config.set_value(section, option, selected_item["value"])

        print_successful_styled_text([(Style.PRIMARY, "{} set to: ".format(config_item["brief"])),
                                      (Style.IMPORTANT, selected_item["name"])])

        custom_settings[config_item["configuration"]] = {
            "brief": config_item["brief"],
            "option": selected_item["name"],
            "modify_status": _get_modify_status(original_config_value, selected_item["value"])
        }

    print_successful_styled_text(MSG_CUSTOM_SETTING_APPLIED)
    _get_config_setting_status(custom_settings)

    _get_more_commands()


def _get_existing_config_value(cmd, section, option):
    from configparser import NoOptionError, NoSectionError

    try:
        original_config_value = cmd.cli_ctx.config.get(section, option)
    except (NoOptionError, NoSectionError):
        return None

    return original_config_value


def _get_modify_status(original_value, new_value):
    if not original_value:
        return "(added)"

    if original_value != new_value:
        return "(changed)"

    return None


def _get_config_setting_status(custom_settings):
    for setting in custom_settings.values():
        new_config_list = [(Style.PRIMARY, "{}: {} ".format(CONTENT_INDENT_BROADBAND + setting["brief"],
                                                            setting["option"]))]
        if setting["modify_status"]:
            new_config_list.append((Style.IMPORTANT, setting["modify_status"]))
        print_styled_text(new_config_list)
        print()

    print_styled_text([(Style.PRIMARY, CONTENT_INDENT_BROADBAND + MSG_MORE_CONFIG_SETTINGS),
                       (Style.HYPERLINK, MSG_MORE_CONFIG_LINK)])


def _get_more_commands():
    print_styled_text((Style.PRIMARY, CONTENT_INDENT_BROADBAND + MSG_MORE_COMMANDS_PROMPT))

    for more_commands_item in MORE_COMMANDS_LIST:
        print_styled_text([(Style.PRIMARY, CONTENT_INDENT_BROADBAND + more_commands_item['name'])])
        print_styled_text([(Style.SECONDARY, CONTENT_INDENT_BROADBAND + more_commands_item['desc'])])
        print()
