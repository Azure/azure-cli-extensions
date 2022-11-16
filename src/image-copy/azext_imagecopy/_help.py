# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

# pylint: disable=line-too-long, too-many-lines

# todo need confirm
helps['image copy'] = """
    type: command
    short-summary: Copy a managed image (or vm) to other regions. It requires the source disk to be available. It is recommended to specify --only-show-errors to run the command.
    examples:
        - name: Copy an image to several regions and cleanup at the end.
          text: >
            az image copy --source-resource-group mySources-rg --source-object-name myImage \\
                --target-location uksouth northeurope --target-resource-group "images-repo-rg" --cleanup --only-show-errors
        - name: Use an already generalized vm to create images in other regions.
          text: >
            az image copy --source-resource-group mySources-rg --source-object-name myVm \\
                --source-type vm --target-location uksouth northeurope --target-resource-group "images-repo-rg" --only-show-errors
"""
