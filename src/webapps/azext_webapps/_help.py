# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


helps['webapp quickstart'] = """
    type: command
    short-summary: Create and deploy a node web app
    examples:
        - name: Create a web app with the default configuration.
          text: >
            az webapp quickstart -n MyUniqueAppName
"""
