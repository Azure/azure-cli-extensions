# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.help_files import helps
from azure.cli.core.sdk.util import ParametersContext

helps['image copy'] = """
    type: command
    short-summary: Copy a managed image (or vm) to other regions
    long-summary: >
        Allows to copy a managed image (or vm) to other regions.
        Keep in mind that it requires the source disk to be available.
    examples:
        - name: Copy an image to several regions and cleanup at the end.
          text: >
            az image copy --source-resource-group mySources-rg --source-object-name myImage \\
                --target-location uksouth northeurope --target-resource-group "images-repo-rg" --cleanup
        - name: Use an already generalized vm to create images in other regions.
          text: >
            az image copy --source-resource-group mySources-rg --source-object-name myVm \\
                --source-type vm --target-location uksouth northeurope --target-resource-group "images-repo-rg"
"""


def load_params(_):
    with ParametersContext('image copy') as c:
        c.register('source_resource_group_name', '--source-resource-group',
                   help='Name of the resource group of the source resource')
        c.register('source_object_name', '--source-object-name',
                   help='The name of the image or vm resource')
        c.register('target_location', '--target-location', nargs='+',
                   help='Space separated location list to create the image in (e.g. westeurope etc.)')
        c.register('source_type', '--source-type', default='image', choices=['image', 'vm'], help='image or vm')
        c.register('target_resource_group_name', '--target-resource-group',
                   help='Name of the resource group to create images in')
        c.register('parallel_degree', '--parallel-degree', type=int, default=-1,
                   help='Number of parallel copy operations')
        c.register('cleanup', '--cleanup', action='store_true', default=False,
                   help='Include this switch to delete temporary resources upon completion')


def load_commands():
    from azure.cli.core.commands import cli_command
    cli_command(__name__, 'image copy', 'azext_imagecopy.custom#imagecopy')
