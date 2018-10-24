# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['mesh'] = """
    type: group
    short-summary: (PREVIEW) Manage Azure Service Fabric Mesh Resources.
"""

helps['mesh deployment'] = """
    type: group
    short-summary: Manage Service Fabric Mesh deployments.
"""

helps['mesh deployment create'] = """
    type: command
    short-summary: Create a Service Fabric Mesh application.
    examples:
        - name: Create a deployment with a template file on the remote.
          text: az mesh deployment create --resource-group mygroup --template-uri https://seabreezequickstart.blob.core.windows.net/templates/quickstart/sbz_rp.linux.json
        - name: Create a deployment with a template file on local disk.
          text: az mesh deployment create --resource-group mygroup --template-file ./appTemplate.json
    parameters:
    - name: --mode
      type: string
      short-summary: The mode for deployment, can be incremental(resources are only added) or
        complete(previous resources will be deleted)
    - name: --parameters
      type: string
      short-summary: json string to supplement parameters of the deployment template
"""

helps['mesh app'] = """
    type: group
    short-summary: Manage Service Fabric Mesh applications.
"""

helps['mesh app delete'] = """
    type: command
    short-summary: Delete a Service Fabric Mesh application.
"""

helps['mesh app list'] = """
    type: command
    short-summary: List Service Fabric Mesh applications.
"""

helps['mesh app show'] = """
    type: command
    short-summary: Get the details of a Service Fabric Mesh application.
"""

helps['mesh service'] = """
    type: group
    short-summary: Manage Service Fabric Mesh services.
"""

helps['mesh service show'] = """
    type: command
    short-summary: Get the details of a service.
"""

helps['mesh service-replica'] = """
    type: group
    short-summary: Manage Service Fabric Mesh service replicas.
"""

helps['mesh service-replica list'] = """
    type: command
    short-summary: List the details of service replicas.
"""

helps['mesh code-package-log'] = """
    type: group
    short-summary: Examine the logs for a codepackage.
"""

helps['mesh code-package-log get'] = """
    type: command
    short-summary: Examine the logs for a codepackage.
"""

helps['mesh network'] = """
    type: group
    short-summary: Manage networks.
"""

helps['mesh network delete'] = """
    type: command
    short-summary: Delete a network.
"""

helps['mesh network list'] = """
    type: command
    short-summary: List networks.
"""

helps['mesh network show'] = """
    type: command
    short-summary: Get the details of a network.
"""

helps['mesh volume'] = """
    type: group
    short-summary: Manage volumes.
"""

helps['mesh volume create'] = """
    type: command
    short-summary: Create a volume.
    examples:
        - name: Create a volume with a template file on a remote URL.
          text: az mesh volume create --location westus --name myvolume --resource-group mygroup --template-uri https://mystorage.blob.core.windows.net/templates/volumeDescription.json
        - name: Create a volume with a template file on local disk.
          text: az mesh volume create --location westus --name myvolume --resource-group mygroup --template-file ./volumeDescription.json
"""

helps['mesh volume delete'] = """
    type: command
    short-summary: Delete a volume.
"""

helps['mesh volume list'] = """
    type: command
    short-summary: List volumes.
"""

helps['mesh volume show'] = """
    type: command
    short-summary: Get the details of a volume.
"""
