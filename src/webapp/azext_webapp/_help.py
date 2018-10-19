# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


helps['webapp up'] = """
    type: command
    short-summary: Experimental command to create and deploy a web app.
                   Current supports includes Node on Linux & .NET Core, ASP.NET, staticHtml on Windows.
    examples:
        - name: Create a web app with the default configuration.
          text: >
            az webapp up -n MyUniqueAppName --dryrun \n
            az webapp up -n MyUniqueAppName -l locationName
"""
helps['webapp remote-connection'] = """
    type: group
    short-summary: Create a remote connection using a tcp tunnel to your web app
"""

helps['webapp remote-connection create'] = """
    type: command
    short-summary: Creates a remote connection using a tcp tunnel to your web app
"""
