# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

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


helps['alias list'] = """
    type: command
    short-summary: List the registered aliases.
"""


helps['alias remove'] = """
    type: command
    short-summary: Remove an alias.
"""
