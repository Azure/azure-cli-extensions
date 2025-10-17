# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import unicode_literals

import os
import os.path

import yaml
from azext_aks_agent._consts import CONST_AGENT_CONFIG_FILE_NAME
from azure.cli.core.api import get_config_dir
from azure.cli.core.azclierror import InvalidArgumentValueError
from knack.log import get_logger

logger = get_logger(__name__)


def _validate_param_yaml_file(yaml_path, param_name):
    if not yaml_path:
        return
    if not os.path.exists(yaml_path):
        raise InvalidArgumentValueError(
            f"--{param_name}={yaml_path}: file is not found."
        )
    if not os.access(yaml_path, os.R_OK):
        raise InvalidArgumentValueError(
            f"--{param_name}={yaml_path}: file is not readable."
        )
    try:
        with open(yaml_path, "r") as file:
            yaml.safe_load(file)
    except yaml.YAMLError as e:
        raise InvalidArgumentValueError(
            f"--{param_name}={yaml_path}: file is not a valid YAML file: {e}"
        )
    except Exception as e:
        raise InvalidArgumentValueError(
            f"--{param_name}={yaml_path}: An error occurred while reading the config file: {e}"
        )


def validate_agent_config_file(namespace):
    config_file = namespace.config_file
    if not config_file:
        return
    # default config file path can be empty
    default_config_path = os.path.join(get_config_dir(), CONST_AGENT_CONFIG_FILE_NAME)
    if config_file == default_config_path and not os.path.exists(config_file):
        return

    _validate_param_yaml_file(config_file, "config-file")
