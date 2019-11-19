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
               az imagebuilder create --resource-group "myResourceGroup" --image-template-name \\
               "myImageTemplate" --location "westus" --customize-name "Shell Customizer Example" \\
               --distribute-run-output-name "image_it_pir_1" --vm-profile-vm-size "Standard_D2s_v3"
      - name: Create an Image Template with a user assigned identity configured
        text: |-
               az imagebuilder create --resource-group "myResourceGroup" --image-template-name \\
               "myImageTemplate" --location "westus" --customize-name "Shell Customizer Example" \\
               --distribute-run-output-name "image_it_pir_1" --vm-profile-vm-size "Standard_D2s_v3" \\
               --type "UserAssigned"
"""

helps['imagebuilder update'] = """
    type: command
    short-summary: Create or update a virtual machine image template
    examples:
      - name: Update the tags for an Image Template.
        text: |-
               az imagebuilder update --resource-group "myResourceGroup" --image-template-name \\
               "myImageTemplate"
      - name: Remove identities for an Image Template.
        text: |-
               az imagebuilder update --resource-group "myResourceGroup" --image-template-name \\
               "myImageTemplate" --type "None"
"""

helps['imagebuilder delete'] = """
    type: command
    short-summary: Delete a virtual machine image template
    examples:
      - name: Delete an Image Template.
        text: |-
               az imagebuilder delete --resource-group "myResourceGroup" --image-template-name \\
               "myImageTemplate"
"""

helps['imagebuilder list'] = """
    type: command
    short-summary: List all run outputs for the specified Image Template resource
    examples:
      - name: List images by subscription.
        text: |-
               az imagebuilder list
      - name: List images by resource group
        text: |-
               az imagebuilder list --resource-group "myResourceGroup"
      - name: Retrieve a list of all outputs created by the last run of an Image Template
        text: |-
               az imagebuilder list --resource-group "myResourceGroup" --image-template-name \\
               "myImageTemplate"
"""

helps['imagebuilder show'] = """
    type: command
    short-summary: Get information about a virtual machine image template
    examples:
      - name: Retrieve an Image Template.
        text: |-
               az imagebuilder show --resource-group "myResourceGroup" --image-template-name \\
               "myImageTemplate"
      - name: Retrieve single runOutput
        text: |-
               az imagebuilder show --resource-group "myResourceGroup" --image-template-name \\
               "myImageTemplate"
"""

helps['imagebuilder'] = """
    type: group
    short-summary: Commands to manage imagebuilder.
"""

helps['imagebuilder list'] = """
    type: command
    short-summary: Lists available operations for the Microsoft.VirtualMachineImages provider
"""
