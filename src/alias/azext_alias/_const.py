# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core._environment import get_config_dir

GLOBAL_CONFIG_DIR = get_config_dir()
ALIAS_FILE_NAME = 'alias'
ALIAS_HASH_FILE_NAME = 'alias.sha1'
COLLIDED_ALIAS_FILE_NAME = 'collided_alias'
COLLISION_CHECK_LEVEL_DEPTH = 4

INSUFFICIENT_POS_ARG_ERROR = 'alias: "{}" takes exactly {} positional argument{} ({} given)'
CONFIG_PARSING_ERROR = 'alias: Error parsing the configuration file - {}. Please fix the problem manually.'
DEBUG_MSG = 'Alias Manager: Transforming "%s" to "%s"'
DEBUG_MSG_WITH_TIMING = 'Alias Manager: Transformed args to %s in %.3fms'
POS_ARG_DEBUG_MSG = 'Alias Manager: Transforming "%s" to "%s", with the following positional arguments: %s'
DUPLICATED_PLACEHOLDER_ERROR = 'alias: Duplicated placeholders found when transforming "{}"'
RENDER_TEMPLATE_ERROR = 'alias: Encounted the following error when injecting positional arguments to "{}" - {}'
PLACEHOLDER_EVAL_ERROR = 'alias: Encounted the following error when evaluating "{}" - {}'
PLACEHOLDER_BRACKETS_ERROR = 'alias: Brackets in "{}" are not enclosed properly'
