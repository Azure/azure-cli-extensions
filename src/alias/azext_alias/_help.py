# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from knack.help_files import helps  # pylint: disable=unused-import


helps['alias'] = """
    type: group
    short-summary: Manage Azure CLI Aliases.
"""


helps['alias create'] = """
    type: command
    short-summary: Create an alias.
    examples:
        - name: Create simple alias commands.
          text: |
            az alias create --name rg --command group

            az alias create --name ls --command list
        - name: Create a complex alias.
          text: |
            az alias create --name list-vm --command 'vm list --resource-group myResourceGroup'

        - name: Create an alias command with arguments.
          text: |
            az alias create --name 'list-vm {{ resource_group }}' \\
              --command 'vm list --resource-group {{ resource_group }}'

        - name: Process arguments using Jinja2 templates.
          text: |
            az alias create --name 'storage-ls {{ url }}' \\
              --command 'storage blob list
                --account-name {{ url.replace("https://", "").split(".")[0] }}
                --container-name {{ url.replace("https://", "").split("/")[1] }}'
"""


helps['alias export'] = """
    type: command
    short-summary: Export all registered aliases to a given path, as an INI configuration file. If no export path is specified, the alias configuration file is exported to the current working directory.
"""


helps['alias import'] = """
    type: command
    short-summary: Import aliases from an INI configuration file or an URL.
"""


helps['alias list'] = """
    type: command
    short-summary: List the registered aliases.
"""


helps['alias remove'] = """
    type: command
    short-summary: Remove one or more aliases. Aliases to be removed are space-delimited.
"""


helps['alias remove-all'] = """
    type: command
    short-summary: Remove all registered aliases.
"""
