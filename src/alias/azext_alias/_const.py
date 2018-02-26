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

PLACEHOLDER_REGEX = r'\s+{\d+}'

INCONSISTENT_INDEXING_ERROR = 'alias: Placeholder indexing should be zero-indexed, but {} is missing in "{}"'
INSUFFICIENT_POS_ARG_ERROR = 'alias: "{}" takes exactly {} argument(s) ({} given)'
CONFIG_PARSING_ERROR = 'alias: Error parsing the configuration file - %s. Please fix the problem manually.'
DEBUG_MSG = 'Alias Manager: Transforming "%s" to "%s"'
DEBUG_MSG_WITH_TIMING = 'Alias Manager: Transformed args to %s in %.3fms'
POS_ARG_DEBUG_MSG = 'Alias Manager: Transforming "{}" to "{}", with the following positional arguments: '
