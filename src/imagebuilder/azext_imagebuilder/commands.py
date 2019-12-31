# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from ._client_factory import cf_virtual_machine_image_templates
    imagebuilder_virtual_machine_image_templates = CliCommandType(
        operations_tmpl='azext_imagebuilder.vendored_sdks.imagebuilder.operations._virtual_machine_image_templates_operations#VirtualMachineImageTemplatesOperations.{}',
        client_factory=cf_virtual_machine_image_templates)
    with self.command_group('imagebuilder', imagebuilder_virtual_machine_image_templates, client_factory=cf_virtual_machine_image_templates, is_preview=True) as g:
        g.custom_command('create', 'create_imagebuilder')
        g.custom_command('update', 'update_imagebuilder')
        g.custom_command('delete', 'delete_imagebuilder')
        g.custom_command('show', 'get_imagebuilder')
        g.custom_command('list', 'list_imagebuilder')
        g.custom_command('run', 'run_imagebuilder')
        g.custom_command('list-run-outputs', 'list_run_outputs_imagebuilder')
        g.custom_command('get-run-output', 'get_run_output_imagebuilder')

    from ._client_factory import cf_operations
    imagebuilder_operations = CliCommandType(
        operations_tmpl='azext_imagebuilder.vendored_sdks.imagebuilder.operations._operations_operations#OperationsOperations.{}',
        client_factory=cf_operations)
    with self.command_group('imagebuilder', imagebuilder_operations, client_factory=cf_operations) as g:
        g.custom_command('list', 'list_imagebuilder')

    # with self.command_group('imagebuilder distribute create ')
