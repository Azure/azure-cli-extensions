# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['imagebuilder'] = """
    type: group
    short-summary: Commands to manage imagebuilder.
"""

helps['imagebuilder create'] = """
    type: command
    short-summary: Create or update a virtual machine image template
    examples:
      - name: Create an Image Template.
        text: |-
               az imagebuilder create --resource-group "myResourceGroup" --name \\
               "myImageTemplate" --location "westus" --source-type "PlatformImage" \\
               --source-urn "Canonical:UbuntuServer:18.04-LTS:18.04.201903060" \\
               --customize "@cus.json" --distribute-type "ManagedImage" \\
               --distribute-location "westus" --distribute-image "myImage"
      - name: Create an Image Template.
        text: |-
               az imagebuilder create --resource-group "myResourceGroup" --name \\
               "myImageTemplate" --location "westus" --source-type "PlatformImage" \\
               --source-urn "Canonical:UbuntuServer:18.04-LTS:18.04.201903060" \\
               --customize "@cus.json" --distribute-type "SharedImage" \\
               --distribute-location "westus" --distribute-image "imageDefinitionID"
"""

helps['imagebuilder update'] = """
    type: command
    short-summary: Create or update a virtual machine image template
    examples:
      - name: Update the tags for an Image Template.
        text: |-
               az imagebuilder update --resource-group "myResourceGroup" --name \\
               "myImageTemplate"
      - name: Remove identities for an Image Template.
        text: |-
               az imagebuilder update --resource-group "myResourceGroup" --name \\
               "myImageTemplate" --type "None"
"""

helps['imagebuilder delete'] = """
    type: command
    short-summary: Delete a virtual machine image template
    examples:
      - name: Delete an Image Template.
        text: |-
               az imagebuilder delete --resource-group "myResourceGroup" --name \\
               "myImageTemplate"
"""

helps['imagebuilder show'] = """
    type: command
    short-summary: Get information about a virtual machine image template
    examples:
      - name: Retrieve an Image Template.
        text: |-
               az imagebuilder show --resource-group "myResourceGroup" --name \\
               "myImageTemplate"
"""

helps['imagebuilder list'] = """
    type: command
    short-summary: Gets information about the VM image templates associated with the specified resource group.
    examples:
      - name: List images by subscription.
        text: |-
               az imagebuilder list
      - name: List images by resource group
        text: |-
               az imagebuilder list --resource-group "myResourceGroup"
"""

helps['imagebuilder run'] = """
    type: command
    short-summary: Create artifacts from a existing image template
    examples:
      - name: Create image(s) from existing imageTemplate.
        text: |-
               az imagebuilder run --resource-group "myResourceGroup" --name \\
               "myImageTemplate"
"""

helps['imagebuilder list_run_outputs'] = """
    type: command
    short-summary: List all run outputs for the specified Image Template resource
    examples:
      - name: Retrieve a list of all outputs created by the last run of an Image Template
        text: |-
               az imagebuilder list_run_outputs --resource-group "myResourceGroup" --name \\
               "myImageTemplate"
"""

helps['imagebuilder get_run_output'] = """
    type: command
    short-summary: Get the specified run output for the specified image template resource
    examples:
      - name: Retrieve single runOutput
        text: |-
               az imagebuilder get_run_output --resource-group "myResourceGroup" --image-template-name \\
               "myImageTemplate" --name "myManagedImageOutput"
"""

helps['imagebuilder'] = """
    type: group
    short-summary: Commands to manage imagebuilder.
"""

helps['imagebuilder list'] = """
    type: command
    short-summary: Lists available operations for the Microsoft.VirtualMachineImages provider
"""
