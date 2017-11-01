# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys
import json

from subprocess import check_output, STDOUT, CalledProcessError
from azure.cli.core.util import CLIError
import azure.cli.core.azlogging as azlogging

logger = azlogging.get_az_logger(__name__)


def run_cli_command(cmd, return_as_json=False):
    try:
        cmd_output = check_output(cmd, stderr=STDOUT, universal_newlines=True)
        logger.debug('command: %s ended with output: %s', cmd, cmd_output)

        if return_as_json is True:
            if cmd_output:
                json_output = json.loads(cmd_output)
                return json_output
            else:
                raise CLIError("Command returned an unexpected empty string.")
        else:
            return cmd_output
    except CalledProcessError as ex:
        logger.error('command failed: %s', cmd)
        logger.error('output: %s', ex.output)
        raise ex
    except:
        logger.error('command ended with an error: %s', cmd)
        raise


def prepare_cli_command(cmd, output_as_json=True):
    full_cmd = [sys.executable, '-m', 'azure.cli'] + cmd

    if output_as_json:
        full_cmd += ['--output', 'json']
    else:
        full_cmd += ['--output', 'tsv']

    # tag newly created resources, containers don't have tags
    if 'create' in cmd and ('container' not in cmd):
        full_cmd += ['--tags', 'created_by=image-copy-extension']

    return full_cmd
