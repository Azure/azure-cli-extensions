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
        - name: Create a simple alias.
          text: >
            az alias create --name rg --command group\n
            az alias create --name ls --command list
        - name: Create a complex alias.
          text: >
            az alias create --name list-vm --command 'vm list --resource-group myResourceGroup'

        - name: Create an alias with positional arguments.
          text: >
            az alias create --name 'list-vm {{ resource_group }}' --command 'vm list --resource-group {{ resource_group }}'

        - name: Create an alias with positional arguments and additional string processing.
          text: >
            az alias create --name 'storage-ls {{ url }}' --command 'storage blob list \n
            --account-name {{ url.replace("https://", "").split(".")[0] }}\n
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
