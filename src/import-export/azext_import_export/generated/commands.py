# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from azext_import_export.generated._client_factory import cf_job
    import_export_job = CliCommandType(
        operations_tmpl='azext_import_export.vendored_sdks.storageimportexport.operations._job_operations#JobOperations.{}',
        client_factory=cf_job)
    with self.command_group('import-export', import_export_job, client_factory=cf_job, is_experimental=True) as g:
        g.custom_command('list', 'import_export_job_list')
        g.custom_show_command('show', 'import_export_job_show')
        g.custom_command('create', 'import_export_job_create')
        g.custom_command('update', 'import_export_job_update')
        g.custom_command('delete', 'import_export_job_delete')

    from azext_import_export.generated._client_factory import cf_bit_locker_key
    import_export_bit_locker_key = CliCommandType(
        operations_tmpl='azext_import_export.vendored_sdks.storageimportexport.operations._bit_locker_key_operations#BitLockerKeyOperations.{}',
        client_factory=cf_bit_locker_key)
    with self.command_group('import-export bit-locker-key', import_export_bit_locker_key, client_factory=cf_bit_locker_key) as g:
        g.custom_command('list', 'import_export_bit_locker_key_list')

    from azext_import_export.generated._client_factory import cf_location
    import_export_location = CliCommandType(
        operations_tmpl='azext_import_export.vendored_sdks.storageimportexport.operations._location_operations#LocationOperations.{}',
        client_factory=cf_location)
    with self.command_group('import-export location', import_export_location,
                            client_factory=cf_location) as g:
        g.custom_command('list', 'import_export_location_list')
        g.custom_show_command('show', 'import_export_location_show')
