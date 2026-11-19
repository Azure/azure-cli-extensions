# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.help_files import helps  # pylint: disable=unused-import

helps['validate'] = """
type: command
short-summary: Check Azure CLI commands without running them.
long-summary: >
    Checks command names, parameters and the values the parser can check (choices, types and --query),
    using the installed Azure CLI. Commands from extensions that aren't installed are checked against
    published command metadata. It never runs the checked commands, installs extensions or signs in.
    The result is a JSON document; the exit code is 0 whether or not the commands are valid.
examples:
  - name: Check one command.
    text: az validate --command 'az vm create -g MyResourceGroup -n MyVm --image Ubuntu2204' -o json
  - name: Check several commands.
    text: az validate --command 'az group create -n MyResourceGroup -l westus' 'az group show -n MyResourceGroup' -o json
  - name: Check every az command in a Bash script file.
    text: az validate --file deploy.sh -o json
  - name: Check a PowerShell script file and also write the result to a file.
    text: az validate --file deploy.ps1 --output-file result.json -o json
  - name: Check script text passed directly.
    text: az validate --script 'RG=MyResourceGroup; az group create -n $RG -l westus' -o json
"""
