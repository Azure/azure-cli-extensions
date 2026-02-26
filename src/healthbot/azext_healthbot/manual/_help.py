# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from knack.help_files import helps


helps['healthbot update'] = """
    type: command
    short-summary: "Patch a HealthBot."
    examples:
      - name: BotUpdate
        text: |-
               az healthbot update --name "samplebotname" --sku "F0" --resource-group "healthbotClient"
"""
