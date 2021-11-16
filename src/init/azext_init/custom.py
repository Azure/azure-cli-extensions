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
from ._configs import (OUTPUT_LIST, INTERACTIVE_CONFIG_BUNDLE)
from ._text import (MSG_WELCOME, MSG_SELECT_STEP, MSG_PROMPT_MANAGE_GLOBAL, MSG_NO_CONFIGURATION,
                    MSG_PROMPT_GLOBAL_OUTPUT, MSG_PROMPT_TELEMETRY, MSG_PROMPT_FILE_LOGGING, MSG_PROMPT_CACHE_TTL,
                    INIT_STEP_OPTION_LIST)
from ._utils import prompt_option_list


logger = get_logger(__name__)


def handle_init(cmd):

    print_styled_text((Style.PRIMARY, MSG_WELCOME))

    load_existing_configuration(cmd)

    print_styled_text((Style.PRIMARY, MSG_SELECT_STEP))

    choose_value = prompt_option_list(INIT_STEP_OPTION_LIST)

    if choose_value in [0, 1]:
        set_build_in_bundles(cmd)

    if choose_value == 2:
        handle_interactive_mode(cmd, INTERACTIVE_CONFIG_BUNDLE)


def load_existing_configuration(cmd):
    with ScopedConfig(cmd.cli_ctx.config, False):
        sections = cmd.cli_ctx.config.sections()
        if sections:
            print_styled_text((Style.PRIMARY, "Your current config settings:\n"))

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


def split_section_from_option(full_option):
    split_option=full_option.split('.')
    return split_option[0],split_option[1]


def get_value_in_option_block(block):
    return block["value"] if "value" in block else block["name"]


def handle_interactive_mode(cmd, config_list):
    changed = {}
    for config in config_list:
        section, option = split_section_from_option(config["configuration"])
        values = config["values"]
        option_list = values["options"]
        default_value = [get_value_in_option_block(x) for x in option_list].index(values["default"])
        selected_option = prompt_choice_list("\n{}{}".format(
            (config["brief"]+":\n") if "brief" in config else "",
            (config["description"]+"\n" if "description" in config else "")
        ), option_list, default_value + 1)

        selected_value = option_list[selected_option]
        choice_value = get_value_in_option_block(selected_value)

        config_original_value = None
        from configparser import NoOptionError, NoSectionError
        try:
            config_original_value = cmd.cli_ctx.config.get(section, option)
        except (NoOptionError, NoSectionError):
            pass

        if not config_original_value:
            changed[(section,option)] = "added"
        elif config_original_value == choice_value:
            changed[(section,option)] = "unchanged"
        else:
            changed[(section,option)] = "changed"
        cmd.cli_ctx.config.set_value(section,option,choice_value)

    sections = cmd.cli_ctx.config.sections()

    for section in sections:
        items = cmd.cli_ctx.config.items(section)
        print_styled_text((Style.PRIMARY, "\n[{}]".format(section)))
        for item in items:
            x = (section, item['name'])
            print_styled_text(
                (Style.PRIMARY, "{}={} {}".format(item['name'], item['value'],
                                                  "({})".format(changed[x]) if x in changed else "")))


def set_config_from_bundles(config, bundles):

    for (section, option) in bundles:
        config_original_value = config.get(section, option)
        config_new_value = bundles[(section, option)]
        if not config_original_value:
            print_styled_text((Style.PRIMARY, 'Add new option in section[{0}] : {1}={2}'.
                               format(section, option, config_new_value)))
        elif config_original_value != config_new_value:
            print_styled_text((Style.PRIMARY, 'Change option in section[{0}] : from {1}={2} to {1}={3}'.
                               format(section, option, config_original_value, config_new_value)))
        else:
            print_styled_text((Style.PRIMARY, 'Option in section[{0}] : {1}={2} not changed'.
                               format(section, option, config_new_value)))
