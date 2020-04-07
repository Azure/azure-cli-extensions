# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azext_databox._validators import validate_create_input_parameters
from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from azext_databox._client_factory import cf_jobs
    databox_jobs = CliCommandType(
        operations_tmpl='azext_databox.vendored_sdks.databox.operations._jobs_operations#JobsOperations.{}',
        client_factory=cf_jobs)
    with self.command_group('databox job', databox_jobs, client_factory=cf_jobs, is_experimental=True) as g:
        g.custom_command('create', 'create_databox_job', validator=validate_create_input_parameters)
        g.custom_command('update', 'update_databox_job')
        g.custom_command('delete', 'delete_databox_job', confirmation=True)
        g.custom_show_command('show', 'get_databox_job')
        g.custom_command('list', 'list_databox_job')
        g.custom_command('cancel', 'cancel_databox_job', confirmation=True)
        g.custom_command('list-credentials', 'list_credentials_databox_job')
