import sys
import json

from subprocess import check_output, STDOUT, CalledProcessError

import azure.cli.core.azlogging as azlogging

logger = azlogging.get_az_logger(__name__)


def run_cli_command(cmd, return_as_json=False):
    try:
        cmd_output = check_output(cmd, stderr=STDOUT, universal_newlines=True)
        logger.debug(cmd_output)

        if return_as_json is True:
            if cmd_output:
                json_output = json.loads(cmd_output)
                return json_output
            else:
                raise Exception("Command returned an unexpected empty string.")
        else:
            return cmd_output
    except CalledProcessError as ex:
        print('command failed: ', cmd)
        print('output: ', ex.output)
        raise ex
    except:
        print('command: ', cmd)
        raise

def prepare_cli_command(cmd, output_as_json=True):
    full_cmd = [sys.executable, '-m', 'azure.cli'] + cmd

    if output_as_json:
        full_cmd += ['--output', 'json']
    else:
        full_cmd += ['--output', 'tsv']

    # tag newly created resources
    if 'create' in cmd and ('container' not in cmd):
        full_cmd += ['--tags', 'created_by=image-copy-extension']

    return full_cmd
