# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from knack.help_files import helps

helps['ssh'] = """
    type: group
    short-summary: SSH into Azure VMs
"""

helps['ssh vm'] = """
    type: command
    short-summary: SSH into Azure VMs
    examples:
        - name: Give a resource group and VM to SSH to
          text: |
            az ssh vm --resource-group [group] --name [vmName] : az ssh vm --resource-group mygroup --name myvm
        - name: Give the public IP of a VM to SSH to
          text: |
            az ssh vm --ip [ip] : az ssh vm --ip 1.2.3.4
"""

helps['ssh config'] = """
    type: command
    short-summary: Create an SSH config for Azure VMs which can then be imported to 3rd party SSH clients
    examples:
        - name: Give a resource group and VM for which to create a config, and save in a local file
          text: |
            az ssh config --resource-group [group] --name [vmName] --file [filename] : az ssh config --resource-group mygroup --name myvm --file ./sshconfig
        - name: Give the public IP of a VM for which to create a config
          text: |
            az ssh config --ip [ip] --file [filename] : az ssh config --ip 1.2.3.4 --file ./sshconfig
"""


class SshCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        ssh_vm_custom = CliCommandType(
            operations_tmpl='azext_ssh.custom#{}')
        super(SshCommandsLoader, self).__init__(
            cli_ctx=cli_ctx, custom_command_type=ssh_vm_custom)

    def load_command_table(self, _):
        with self.command_group('ssh') as g:
            g.custom_command('vm', 'ssh_vm')
            g.custom_command('config', 'ssh_config')
        return self.command_table

    def load_arguments(self, _):
        with self.argument_context('ssh vm') as c:
            c.extra('resource_group', options_list=['--resource-group'])
            c.extra('vm_name', options_list=['--name'])
            c.extra('ssh_ip', options_list=['--ip'])
            c.extra('public_key_file', options_list=['--public-key-file'])
            c.extra('private_key_file', options_list=['--private-key-file'])

        with self.argument_context('ssh config') as c:
            c.argument('config_path', options_list=['--file'])
            c.extra('resource_group', options_list=['--resource-group'])
            c.extra('vm_name', options_list=['--name'])
            c.extra('ssh_ip', options_list=['--ip'])
            c.extra('public_key_file', options_list=['--public-key-file'])
            c.extra('private_key_file', options_list=['--private-key-file'])


COMMAND_LOADER_CLS = SshCommandsLoader
