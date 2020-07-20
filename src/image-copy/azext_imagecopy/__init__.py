# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands.parameters import tags_type

import azext_imagecopy._help  # pylint: disable=unused-import


class ImageCopyCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        imagecopy_custom = CliCommandType(
            operations_tmpl='azext_imagecopy.custom#{}')
        super(ImageCopyCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                      custom_command_type=imagecopy_custom)

    def load_command_table(self, _):
        with self.command_group('image') as g:
            g.custom_command('copy', 'imagecopy')

        return self.command_table

    def load_arguments(self, _):
        with self.argument_context('image copy') as c:
            c.argument('source_resource_group_name', options_list=['--source-resource-group'],
                       help='Name of the resource group of the source resource')
            c.argument('source_object_name', options_list=['--source-object-name'],
                       help='The name of the image or vm resource')
            c.argument('target_location', options_list=['--target-location'], nargs='+',
                       help='Space separated location list to create the image in (e.g. westeurope etc.)')
            c.argument('source_type', options_list=[
                '--source-type'], default='image', choices=['image', 'vm'], help='image or vm')
            c.argument('target_resource_group_name', options_list=['--target-resource-group'],
                       help='Name of the resource group to create images in')
            c.argument('parallel_degree', options_list=['--parallel-degree'], type=int, default=-1,
                       help='Number of parallel copy operations')
            c.argument('cleanup', options_list=['--cleanup'], action='store_true', default=False,
                       help='Include this switch to delete temporary resources upon completion')
            c.argument('target_name', options_list=['--target-name'],
                       help='Name of the final image that will be created')
            c.argument('target_subscription', options_list=['--target-subscription'],
                       help='Name or ID of the subscription where the final image should be created.')
            c.argument('timeout', options_list=['--timeout'], type=int, default=3600,
                       help='Time in seconds for the copy operation to finish. Increase this time if '
                       'you are going to copy large images (disks) like 512GB or more.')
            c.argument('temporary_resource_group_name',
                       options_list=['--temporary-resource-group-name', '--temporary_resource_group_name'],
                       default='image-copy-rg',
                       help='Resource Group name where temporary storage account will be created. '
                            '--temporary_resource_group_name will be deprecated in 0.2.7.')
            c.argument('export_as_snapshot', options_list=['--export-as-snapshot'], action='store_true', default=False,
                       help='Include this switch to export the copies as snapshots instead of images.')
            c.argument('tags', tags_type)


COMMAND_LOADER_CLS = ImageCopyCommandsLoader
