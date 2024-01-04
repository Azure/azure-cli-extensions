# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.log import get_logger
from azure.cli.core.style import Style, print_styled_text

from ._utils import prompt_option_list, get_int_option, print_successful_styled_text, get_yes_or_no_option
from ._text import (MSG_WELCOME, MSG_SELECT_STEP, MSG_INPUT_SELECTION, MSG_CURRENT_SETTINGS, MSG_NO_CONFIGURATION,
                    MSG_BUNDLE_SETTING_APPLIED, INIT_STEP_OPTION_LIST, MSG_CUSTOM_SETTING_APPLIED,
                    MSG_MORE_CONFIG_SETTINGS, MSG_MORE_CONFIG_LINK, CONTENT_INDENT_BROADBAND, MSG_MORE_COMMANDS_PROMPT,
                    MORE_COMMANDS_LIST, MSG_BUILD_IN_INTERACTION_BUNDLES, MSG_BUILD_IN_AUTOMATION_BUNDLES,
                    MSG_RECOMMEND_BUNDLE_SETTINGS, MSG_THANKS_FOR_TRYING)
from ._bundles import BUILD_IN_INTERACTION_BUNDLES, BUILD_IN_AUTOMATION_BUNDLES
from ._configs import WALK_THROUGH_CONFIG_LIST

logger = get_logger(__name__)


def handle_init(cmd):

    print_styled_text((Style.PRIMARY, MSG_WELCOME))

    load_existing_configuration(cmd)

    print_styled_text((Style.PRIMARY, MSG_SELECT_STEP))
    prompt_option_list(INIT_STEP_OPTION_LIST, content_indent=CONTENT_INDENT_BROADBAND)
    selected_option = get_int_option(MSG_INPUT_SELECTION, 1, 4, 4)
    print()

    if selected_option == 1:
        set_build_in_bundles(cmd, BUILD_IN_INTERACTION_BUNDLES, MSG_BUILD_IN_INTERACTION_BUNDLES)

    if selected_option == 2:
        set_build_in_bundles(cmd, BUILD_IN_AUTOMATION_BUNDLES, MSG_BUILD_IN_AUTOMATION_BUNDLES)

    if selected_option == 3:
        handle_walk_through(cmd, WALK_THROUGH_CONFIG_LIST)

    if selected_option == 4:
        print_styled_text((Style.PRIMARY, CONTENT_INDENT_BROADBAND + MSG_THANKS_FOR_TRYING))


def load_existing_configuration(cmd):
    has_existing_configs = False
    for config_item in WALK_THROUGH_CONFIG_LIST:
        section, option = config_item["configuration"].split('.')
        exists_config_value = _get_existing_config_value(cmd, section, option)
        if exists_config_value is None:
            continue

        if not has_existing_configs:
            print_styled_text((Style.PRIMARY, MSG_CURRENT_SETTINGS))
            has_existing_configs = True

        option_meaning = _get_option_meaning(exists_config_value, config_item["options"])
        print_styled_text([(Style.PRIMARY, "{}: {} ".format(CONTENT_INDENT_BROADBAND + config_item["brief"],
                                                            option_meaning))])
        print_styled_text((Style.SECONDARY, CONTENT_INDENT_BROADBAND + "[{} = {}]".format(config_item["configuration"],
                                                                                          exists_config_value)))
        print()

    if not has_existing_configs:
        print_styled_text((Style.PRIMARY, MSG_NO_CONFIGURATION))


def set_build_in_bundles(cmd, bundles, bundle_name):
    config_info_map = {}
    for config_item in WALK_THROUGH_CONFIG_LIST:
        config_info_map[config_item["configuration"]] = config_item

    print_styled_text((Style.PRIMARY, CONTENT_INDENT_BROADBAND + MSG_RECOMMEND_BUNDLE_SETTINGS.format(bundle_name)))
    for bundle_item in bundles:
        config_info = config_info_map[bundle_item["configuration"]]
        option_meaning = _get_option_meaning(bundle_item["value"], config_info["options"])
        print_styled_text([(Style.PRIMARY, "{}{}: ".format(CONTENT_INDENT_BROADBAND, config_info["brief"])),
                           (Style.IMPORTANT, option_meaning)])
        print_styled_text((Style.PRIMARY, CONTENT_INDENT_BROADBAND + bundle_item["brief"]))
        print_styled_text((Style.SECONDARY, CONTENT_INDENT_BROADBAND + "[{} = {}]".format(bundle_item["configuration"],
                                                                                          bundle_item["value"])))
        print()

    confirmation = get_yes_or_no_option("Are you sure to apply these settings? (y/n): ")
    if not confirmation:
        print_styled_text((Style.PRIMARY, "\n" + CONTENT_INDENT_BROADBAND + MSG_THANKS_FOR_TRYING))
        return

    bundle_settings = {}
    for bundle_item in bundles:
        section, option = bundle_item["configuration"].split('.')
        original_config_value = _get_existing_config_value(cmd, section, option)

        cmd.cli_ctx.config.set_value(section, option, bundle_item["value"])

        config_info = config_info_map[bundle_item["configuration"]]
        option_meaning = _get_option_meaning(bundle_item["value"], config_info["options"])
        bundle_settings[bundle_item["configuration"]] = {
            "brief": config_info["brief"],
            "option": option_meaning,
            "configuration": bundle_item["configuration"],
            "value": bundle_item["value"],
            "modify_status": _get_modify_status(original_config_value, bundle_item["value"])
        }

    print_successful_styled_text(MSG_BUNDLE_SETTING_APPLIED.format(bundle_name))
    _get_config_setting_status(bundle_settings)

    _get_more_commands()


def handle_walk_through(cmd, config_list):

    custom_settings = {}
    for config_item in config_list:
        print_styled_text((Style.PRIMARY, "{}:\n".format(config_item["brief"])))
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
                                      (Style.IMPORTANT, selected_item["option"])])

        custom_settings[config_item["configuration"]] = {
            "brief": config_item["brief"],
            "option": selected_item["option"],
            "configuration": config_item["configuration"],
            "value": selected_item["value"],
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


def _get_option_meaning(option_value, option_list):
    option_meaning = option_value
    for option_item in option_list:
        if option_item['value'] == option_value:
            option_meaning = option_item['option']
            break
    return option_meaning


def _get_modify_status(original_value, new_value):
    if not original_value:
        return "(added)"

    if original_value != new_value:
        return "(changed)"

    return None


def _get_config_setting_status(custom_settings):
    for setting_item in custom_settings.values():
        setting_status = [(Style.PRIMARY, "{}: {} ".format(CONTENT_INDENT_BROADBAND + setting_item["brief"],
                                                           setting_item["option"]))]
        if setting_item["modify_status"]:
            setting_status.append((Style.IMPORTANT, setting_item["modify_status"]))
        print_styled_text(setting_status)

        print_styled_text((Style.SECONDARY, CONTENT_INDENT_BROADBAND +
                           "[{} = {}]".format(setting_item["configuration"], setting_item["value"])))
        print()

    print_styled_text([(Style.PRIMARY, CONTENT_INDENT_BROADBAND + MSG_MORE_CONFIG_SETTINGS),
                       (Style.HYPERLINK, MSG_MORE_CONFIG_LINK)])


def _get_more_commands():
    print_styled_text((Style.PRIMARY, CONTENT_INDENT_BROADBAND + MSG_MORE_COMMANDS_PROMPT))

    for more_commands_item in MORE_COMMANDS_LIST:
        print_styled_text([(Style.PRIMARY, CONTENT_INDENT_BROADBAND + more_commands_item['option'])])
        print_styled_text([(Style.SECONDARY, CONTENT_INDENT_BROADBAND + more_commands_item['desc'])])
        print()
