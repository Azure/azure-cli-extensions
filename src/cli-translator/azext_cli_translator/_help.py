# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['cli-translator'] = """
    type: group
    short-summary: Translate ARM template or REST api to CLI scripts
"""

helps['cli-translator arm'] = """
    type: group
    short-summary: Translate ARM template to CLI scripts
"""

helps['cli-translator arm translate'] = """
    type: command
    short-summary: Translate ARM template to CLI scripts
    examples:
        - name: Translate ARM template.json and parameters.json to CLI scripts
          text: |
            az cli-translator arm translate --subscription 00000000-0000-0000-0000-000000000000 
            --resource-group groupName --template armTemplatePath --parameters armParametersPath
"""
