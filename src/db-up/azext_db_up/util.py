# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import random
import os
from knack.config import CLIConfig
from azure.cli.core.commands import LongRunningOperation, _is_poller

CONFIG_DIR = os.path.expanduser(os.path.join('~', '.azext_db_up'))
ENV_VAR_PREFIX = 'AZEXT'
MYSQL_CONFIG_SECTION = 'mysql_up'
POSTGRES_CONFIG_SECTION = 'postgres_up'
SQL_CONFIG_SECTION = 'sql_up'
CONFIG_MAP = {
    'mysql': MYSQL_CONFIG_SECTION,
    'postgres': POSTGRES_CONFIG_SECTION,
    'sql': SQL_CONFIG_SECTION
}
DB_CONFIG = CLIConfig(config_dir=CONFIG_DIR, config_env_var_prefix=ENV_VAR_PREFIX)


def create_random_resource_name(prefix='azure', length=15):
    append_length = length - len(prefix)
    digits = [str(random.randrange(10)) for i in range(append_length)]
    return prefix + ''.join(digits)


def get_config_value(db_type, option, fallback='_fallback_none'):
    config_section = CONFIG_MAP[db_type]
    if fallback == '_fallback_none':
        result = DB_CONFIG.get(config_section, option)
    else:
        result = DB_CONFIG.get(config_section, option, fallback=fallback)
    if result:
        return result
    return None


def set_config_value(db_type, option, value):
    config_section = CONFIG_MAP[db_type]
    DB_CONFIG.set_value(config_section, option, value)


def update_kwargs(kwargs, key, value):
    if value is not None:
        kwargs[key] = value


def resolve_poller(result, cli_ctx, name):
    if _is_poller(result):
        return LongRunningOperation(cli_ctx, 'Starting {}'.format(name))(result)
    return result
