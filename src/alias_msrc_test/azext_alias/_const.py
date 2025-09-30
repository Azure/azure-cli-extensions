# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.core._environment import get_config_dir

GLOBAL_CONFIG_DIR = get_config_dir()
ALIAS_FILE_NAME = 'alias'
ALIAS_HASH_FILE_NAME = 'alias.sha1'
COLLIDED_ALIAS_FILE_NAME = 'collided_alias'
ALIAS_TAB_COMP_TABLE_FILE_NAME = 'alias_tab_completion'
GLOBAL_ALIAS_TAB_COMP_TABLE_PATH = os.path.join(GLOBAL_CONFIG_DIR, ALIAS_TAB_COMP_TABLE_FILE_NAME)
COLLISION_CHECK_LEVEL_DEPTH = 5

INSUFFICIENT_POS_ARG_ERROR = 'alias: "{}" takes exactly {} positional argument{} ({} given)'
CONFIG_PARSING_ERROR = 'alias: Please ensure you have a valid alias configuration file. Error detail: %s'
DEBUG_MSG = 'Alias Manager: Transforming "%s" to "%s"'
DEBUG_MSG_WITH_TIMING = 'Alias Manager: Transformed args to %s in %.3fms'
POS_ARG_DEBUG_MSG = 'Alias Manager: Transforming "%s" to "%s", with the following positional arguments: %s'
DUPLICATED_PLACEHOLDER_ERROR = 'alias: Duplicated placeholders found when transforming "{}"'
RENDER_TEMPLATE_ERROR = 'alias: Encounted error when injecting positional arguments to "{}". Error detail: {}'
PLACEHOLDER_EVAL_ERROR = 'alias: Encounted error when evaluating "{}". Error detail: {}'
PLACEHOLDER_BRACKETS_ERROR = 'alias: Brackets in "{}" are not enclosed properly'
ALIAS_NOT_FOUND_ERROR = 'alias: "{}" alias not found'
INVALID_ALIAS_COMMAND_ERROR = 'alias: Invalid Azure CLI command "{}"'
EMPTY_ALIAS_ERROR = 'alias: Empty alias name or command is invalid'
INVALID_STARTING_CHAR_ERROR = 'alias: Alias name should not start with "{}"'
INCONSISTENT_ARG_ERROR = 'alias: Positional argument{} {} {} not in both alias name and alias command'
COMMAND_LVL_ERROR = 'alias: "{}" is a reserved command and cannot be used to represent "{}"'
ALIAS_FILE_NOT_FOUND_ERROR = 'alias: File not found'
ALIAS_FILE_DIR_ERROR = 'alias: {} is a directory'
ALIAS_FILE_URL_ERROR = 'alias: Encounted error when retrieving alias file from {}. Error detail: {}'
POST_EXPORT_ALIAS_MSG = 'alias: Exported alias configuration file to %s.'
FILE_ALREADY_EXISTS_ERROR = 'alias: {} already exists.'
