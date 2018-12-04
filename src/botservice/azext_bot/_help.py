# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['bot publish'] = """
    type: command
    short-summary: Publish to a bot's associated app service.
    long-summary: Publish your source code to your bot's associated app service.
    examples:
        - name: Publish source code to your Azure App, from within the bot code folder
          text: |-
            az bot publish -n botName -g MyResourceGroup --verbose
"""
