# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.help_files import helps
from azure.cli.core.sdk.util import ParametersContext

helps['image copy'] = """
    type: command
    short-summary: Allows to copy an image (or vm) to other regions. Keep in mind that it requires the source disk to be available.
"""

def load_params(_):
    with ParametersContext('image copy') as c:
        c.register('source_resource_group_name', '--source-resource-group-name', help='Name of the resource gorup of the source resource')
        c.register('source_object_name', '--source-object-name', help='The name of the image or vm resource')
        c.register('target_location', '--target-location', help='Comma seperated location list to create the image in')
        c.register('source_type', '--source-type', help='image (default) or vm')
        c.register('target_resource_group_name', '--target-resource-group-name', help='Name of the resource group to create images in')
        c.register('parallel_degree', '--parallel-degree', help='Number of parallel copy operations')
        c.register('cleanup', '--cleanup', help='Will delete temporary resources created in process (false by default)')

def load_commands():
    from azure.cli.core.commands import cli_command
    cli_command(__name__, 'image copy', 'azext_imagecopy.custom#imagecopy')
