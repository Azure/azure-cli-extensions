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
from ._configs import OUTPUT_LIST, INTERACTIVE_CONFIG_LIST
from ._text import (MSG_WELCOME, MSG_SELECT_STEP, MSG_INPUT_SELECTION, MSG_PROMPT_MANAGE_GLOBAL, MSG_NO_CONFIGURATION,
                    MSG_CURRENT_SETTINGS, MSG_PROMPT_GLOBAL_OUTPUT, MSG_PROMPT_TELEMETRY, MSG_PROMPT_FILE_LOGGING,
                    MSG_PROMPT_CACHE_TTL, INIT_STEP_OPTION_LIST, MSG_CUSTOM_SETTING_APPLIED)
from ._utils import prompt_option_list, get_int_option, print_successful_styled_text


logger = get_logger(__name__)


def handle_init(cmd):

    print_styled_text((Style.PRIMARY, MSG_WELCOME))

    load_existing_configuration(cmd)

    print_styled_text((Style.PRIMARY, MSG_SELECT_STEP))

    prompt_option_list(INIT_STEP_OPTION_LIST)

    selected_option = get_int_option(MSG_INPUT_SELECTION, 1, 3, 3)

    if selected_option in [1, 2]:
        set_build_in_bundles(cmd)

    if selected_option == 3:
        handle_interactive_mode(cmd, INTERACTIVE_CONFIG_LIST)


def load_existing_configuration(cmd):
    with ScopedConfig(cmd.cli_ctx.config, False):
        sections = cmd.cli_ctx.config.sections()
        if sections:
            print_styled_text((Style.PRIMARY, MSG_CURRENT_SETTINGS))

            for section in sections:
                items = cmd.cli_ctx.config.items(section)
                print_styled_text((Style.PRIMARY, "\n[" + section + "]"))
                for item in items:
                    print_styled_text((Style.PRIMARY, item['name'] + " = " + item['value']))
        else:
            print_styled_text((Style.PRIMARY, MSG_NO_CONFIGURATION))


def set_build_in_bundles(cmd):

    from azure.cli.core.cloud import cloud_forbid_telemetry

    cloud_forbid_telemetry = cloud_forbid_telemetry(cmd.cli_ctx)
    config = cmd.cli_ctx.config
    # print location of global configuration
    print_styled_text((Style.PRIMARY, 'Your settings can be found at {}'.format(config.config_path)))
    # set up the config parsers
    file_config = configparser.ConfigParser()
    config_exists = file_config.read([config.config_path])
    should_modify_global_config = False
    answers = {}
    if config_exists:
        # print current config and prompt to allow global config modification
        should_modify_global_config = prompt_y_n(MSG_PROMPT_MANAGE_GLOBAL, default='n')
        answers['modify_global_prompt'] = should_modify_global_config

    if not config_exists or should_modify_global_config:
        # no config exists yet so configure global config or user wants to modify global config
        with ConfiguredDefaultSetter(config, False):
            output_index = prompt_choice_list(MSG_PROMPT_GLOBAL_OUTPUT, OUTPUT_LIST,
                                              default=get_default_from_config(config, 'core', 'output', OUTPUT_LIST))
            answers['output_type_prompt'] = output_index
            answers['output_type_options'] = str(OUTPUT_LIST)
            enable_file_logging = prompt_y_n(MSG_PROMPT_FILE_LOGGING, default='n')
            if cloud_forbid_telemetry:
                allow_telemetry = False
            else:
                allow_telemetry = prompt_y_n(MSG_PROMPT_TELEMETRY, default='y')
            answers['telemetry_prompt'] = allow_telemetry
            cache_ttl = None
            while not cache_ttl:
                try:
                    cache_ttl = prompt(MSG_PROMPT_CACHE_TTL) or DEFAULT_CACHE_TTL
                    # ensure valid int by casting
                    cache_value = int(cache_ttl)
                    if cache_value < 1:
                        raise ValueError
                except ValueError:
                    logger.error('TTL must be a positive integer')
                    cache_ttl = None
            # save the global config
            config.set_value('core', 'output', OUTPUT_LIST[output_index]['name'])
            config.set_value('core', 'collect_telemetry', 'yes' if allow_telemetry else 'no')
            config.set_value('core', 'cache_ttl', cache_ttl)
            config.set_value('logging', 'enable_log_file', 'yes' if enable_file_logging else 'no')


def get_default_from_config(config, section, option, choice_list, fallback=1):
    try:
        config_val = config.get(section, option)
        return [i for i, x in enumerate(choice_list)
                if 'name' in x and x['name'] == config_val][0] + 1
    except (IndexError, configparser.NoSectionError, configparser.NoOptionError):
        return fallback


def handle_interactive_mode(cmd, config_list):

    custom_settings = {}
    for config in config_list:

        print_styled_text((Style.PRIMARY, "\n{}:\n".format(config["brief"])))
        print_styled_text((Style.PRIMARY, "{}\n".format(config["description"])))
        prompt_option_list(config["options"])

        default_value = 1
        for index, option_item in enumerate(config["options"]):
            if "tag" in option_item and option_item["tag"] == "default":
                default_value = index + 1
                break

        selected_option = get_int_option(MSG_INPUT_SELECTION, 1, len(config["options"]), default_value)
        selected_item = config["options"][selected_option - 1]
        selected_value = selected_item["value"] if "value" in selected_item and selected_item["value"] \
            else selected_item["option"]

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
        elif original_config_value != selected_value:
            modify_status = "(changed)"

        custom_settings[config["configuration"]] = {
            "brief": config["brief"],
            "selected": selected_item["name"],
            "modify_status": modify_status
        }

        cmd.cli_ctx.config.set_value(section, option, selected_value)
        print_successful_styled_text("{} set to: {}\n".format(config["brief"], selected_item["name"]))

    print_successful_styled_text(MSG_CUSTOM_SETTING_APPLIED)

    for setting in custom_settings.values():
        new_config_list = [(Style.PRIMARY, "{}: {} ".format(setting["brief"], setting["selected"]))]
        if setting["modify_status"]:
            new_config_list.append((Style.IMPORTANT, setting["modify_status"]))
        print_styled_text(new_config_list)
        print()
