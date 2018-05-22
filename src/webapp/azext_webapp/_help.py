# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


helps['webapp up'] = """
    type: command
    short-summary: Experimental command to create and deploy a web app.
                   Current supports includes Node and Java(needs a .war file) on Linux & .NET Core, ASP.NET, staticHtml on Windows.
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

helps['webapp config snapshot list'] = """
    type: command
    short-summary: List the snapshots available for a web app.
                   Snapshots are automatically managed backups of web app content and configuration.
    examples:
        - name: List the snapshots available for a web app named MyApp.
          text: >
            az webapp config snapshot list -g Default-Web-WestUS -n MyApp
"""

helps['webapp config snapshot restore'] = """
    type: command
    short-summary: Restore a snapshot to a web app.
                   A snapshot from a different web app or slot can be restored by specifying the source.
    examples:
        - name: Overwrite a web app with its own snapshot.
          text: >
            az webapp config snapshot restore -g Default-Web-WestUS -n MyApp -t 2018-04-25T00:09:20.8736381Z
        - name: Overwrite a web app's staging slot with a snapshot from its production slot.
          text: >
            az webapp config snapshot restore -g Default-Web-WestUS -n MyApp -s staging -t 2018-04-25T00:09:20.8736381Z --source-resource-group Default-Web-WestUS --source-name MyApp --restore-config
"""
