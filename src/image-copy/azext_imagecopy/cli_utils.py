# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys
import json

from subprocess import check_output, STDOUT, CalledProcessError
from knack.util import CLIError

from knack.log import get_logger
logger = get_logger(__name__)

EXTENSION_TAG_STRING = 'created_by=image-copy-extension'


# pylint: disable=inconsistent-return-statements
def run_cli_command(cmd, return_as_json=False):
    try:
        cmd_output = check_output(cmd, stderr=STDOUT, universal_newlines=True)
        logger.debug('command: %s ended with output: %s', cmd, cmd_output)

        if return_as_json:
            if cmd_output:
                # cleanup to resolve invalid JSON in underlying azure cli  - issue #979
                # Related to: https://github.com/Azure/azure-cli/issues/10687
                json_start_chars = {"{", "["}
                json_start_at = next((i for i, ch in enumerate(str(cmd_output)) if ch in json_start_chars), -1)
                logger.debug('json output starts at position: %i ', json_start_at)
                if json_start_at > 0:
                    logger.debug("json output did not start at position 0, stripping the prefix.")
                    cmd_output = str(cmd_output)[json_start_at:]
                    logger.debug("json output after fix:")
                    logger.debug(cmd_output)

                json_output = json.loads(cmd_output)
                return json_output

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


def prepare_cli_command(cmd, output_as_json=True, tags=None, subscription=None):
    full_cmd = [sys.executable, '-m', 'azure.cli'] + cmd

    if output_as_json:
        full_cmd += ['--output', 'json']
    else:
        full_cmd += ['--output', 'tsv']

    # override the default subscription if needed
    if subscription is not None:
        full_cmd += ['--subscription', subscription]

    # tag newly created resources, containers don't have tags
    if 'create' in cmd and ('container' not in cmd):
        full_cmd += ['--tags', EXTENSION_TAG_STRING]

        if tags is not None:
            full_cmd += tags.split()

    return full_cmd
