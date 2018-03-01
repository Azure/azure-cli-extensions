# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


helps['webapp new'] = """
    type: command
    short-summary: Experimental command to create and deploy a web app.
                   Current supports Node on Linux & .NET Core on Windows.
    examples:
        - name: Create a web app with the default configuration.
          text: >
            az webapp new -n MyUniqueAppName --dryrun \n
            az webapp new -n MyUniqueAppName -l locationName
"""
