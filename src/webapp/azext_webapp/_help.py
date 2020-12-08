# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['webapp remote-connection'] = """
    type: group
    short-summary: Create a remote connection using a tcp tunnel to your web app
"""

helps['webapp remote-connection create'] = """
    type: command
    short-summary: Creates a remote connection using a tcp tunnel to your web app
"""

helps['webapp scan'] = """
    type: group
    short-summary: Holds group of commands which cater to webapp scans. Currently available only for Linux based webapps.
"""

helps['webapp scan start'] = """
    type: command
    short-summary: Starts the scan on the specified webapp files in the wwwroot directory. It returns a JSON containing the ScanID, traking and results URL.
"""

helps['webapp scan show-result'] = """
    type: command
    short-summary: Get results of specified scan-id. This will fetch you the Scan log results of the specified scan-id.
"""

helps['webapp scan track'] = """
    type: command
    short-summary: Track status of scan by providing scan-id. You can track the status of the scan from [Starting, Success, Failed, TimeoutFailure, Executing]
"""

helps['webapp scan list-result'] = """
    type: command
    short-summary: Get details of all scans conducted on webapp, upto max scan limit set on the webapp This will get you the scan log results in addition to the scan status of each scan conducted on the webapp.
"""

helps['webapp scan stop'] = """
    type: command
    short-summary: Stops the current executing scan. Does nothing if no scan is executing.
"""

helps['webapp container'] = """
    type: group
    short-summary: Group of commands related to webapp container operations
"""

helps['webapp container up'] = """
    type: command
    short-summary: Experimental command to create and deploy a container webapp.
    examples:
        - name: Deploy a container using an image from DockerHub. This example uses nginx.
          text: az webapp container up -n AppName -i nginx
        - name: Upload files from the current directory to an Azure Container Registry, then build a container image and deploy it to a web app. The Azure Container Registry must already exist.
          text: az webapp container up -n AppName --registry-rg ContainerRegistryResourceGroup --registry-name ContainerRegistryName
"""

helps['webapp deploy'] = """
    type: command
    short-summary: Deploys a provided artifact to Azure Web Apps.
    examples:
    - name: Deploy a war file asynchronously.
      text: az webapp deploy --resource-group ResouceGroup --name AppName --src-path SourcePath --type war --async IsAsync
    - name: Deploy a static text file to wwwroot/staticfiles/test.txt
      text: az webapp deploy --resource-group ResouceGroup --name AppName --src-path SourcePath --type static --target-path staticfiles/test.txt
"""
