# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-few-public-methods, unused-argument, redefined-builtin

from re import match
from azure.cli.core.util import CLIError
from knack.log import get_logger

logger = get_logger(__name__)


def validate_config_file_patterns(namespace):
    if not namespace.config_file_patterns:
        return
    pattern_list = namespace.config_file_patterns.split(',')
    invalid_list = [p for p in pattern_list if not _is_valid_pattern(p)]
    if invalid_list:
        logger.warning('Config file patterns "%s" are invalid.', ','.join(invalid_list))
        raise CLIError('--config-file-patterns should be the collection of patterns separated by comma, each pattern in the format of \'application\' or \'application/profile\'')


def _is_valid_pattern(pattern):
    return _is_valid_app_name(pattern) or _is_valid_app_and_profile_name(pattern)


def _is_valid_app_name(pattern):
    return match(r"^[a-zA-Z][-_a-zA-Z0-9]*$", pattern) is not None


def _is_valid_profile_name(profile):
    return profile == "*" or _is_valid_app_name(profile)


def _is_valid_app_and_profile_name(pattern):
    parts = pattern.split('/')
    return len(parts) == 2 and _is_valid_app_name(parts[0]) and _is_valid_profile_name(parts[1])
