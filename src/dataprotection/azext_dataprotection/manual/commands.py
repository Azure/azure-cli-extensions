# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
# pylint: disable=line-too-long

from azext_dataprotection.manual._client_factory import cf_resource_graph_client
from ._exception_handler import exception_handler


def load_command_table(self, _):

    # Manual backup-instance commmands
    with self.command_group('dataprotection backup-instance', exception_handler=exception_handler) as g:
        g.custom_command('initialize-backupconfig', "dataprotection_backup_instance_initialize_backupconfig")
        g.custom_command('initialize-restoreconfig', "dataprotection_backup_instance_initialize_restoreconfig")
        g.custom_command('initialize', "dataprotection_backup_instance_initialize")
        g.custom_command('list-from-resourcegraph', 'dataprotection_backup_instance_list_from_resourcegraph', client_factory=cf_resource_graph_client)
        g.custom_command('update-msi-permissions', 'dataprotection_backup_instance_update_msi_permissions')
        g.custom_command('update-policy', "dataprotection_backup_instance_update_policy", supports_no_wait=True)

    # Migrated to AAZ, using a function based override approach. Function-based override uses AAZ arg schema to validate input
    # but is less manageable. Needs manual management of params and help. Find a way to use class-based override without compromising
    # AAZ validation
    with self.command_group('dataprotection backup-instance', exception_handler=exception_handler) as g:
        g.custom_command('validate-for-backup', 'dataprotection_backup_instance_validate_for_backup', supports_no_wait=True)

    with self.command_group('dataprotection backup-instance restore', exception_handler=exception_handler) as g:
        g.custom_command('initialize-for-data-recovery', 'restore_initialize_for_data_recovery')
        g.custom_command('initialize-for-data-recovery-as-files', 'restore_initialize_for_data_recovery_as_files')
        g.custom_command('initialize-for-item-recovery', 'restore_initialize_for_item_recovery')

    with self.command_group('dataprotection backup-policy', exception_handler=exception_handler) as g:
        g.custom_command('get-default-policy-template', "dataprotection_backup_policy_get_default_policy_template")

    with self.command_group('dataprotection backup-policy trigger') as g:
        g.custom_command('create-schedule', "dataprotection_backup_policy_trigger_create_schedule")
        g.custom_command('set', "dataprotection_backup_policy_trigger_set_in_policy")

    with self.command_group('dataprotection backup-policy retention-rule') as g:
        g.custom_command('create-lifecycle', "dataprotection_backup_policy_create_lifecycle")
        g.custom_command('set', "dataprotection_backup_policy_retention_set_in_policy")
        g.custom_command('remove', "dataprotection_backup_policy_retention_remove_in_policy")

    with self.command_group('dataprotection backup-policy tag') as g:
        g.custom_command('create-absolute-criteria', "dataprotection_backup_policy_create_absolute_criteria")
        g.custom_command('create-generic-criteria', "dataprotection_backup_policy_create_generic_criteria")
        g.custom_command('set', "dataprotection_backup_policy_tag_set_in_policy")
        g.custom_command('remove', "dataprotection_backup_policy_tag_remove_in_policy")

    with self.command_group('dataprotection job') as g:
        g.custom_command('list-from-resourcegraph', "dataprotection_job_list_from_resourcegraph", client_factory=cf_resource_graph_client)

    with self.command_group('dataprotection resource-guard', exception_handler=exception_handler) as g:
        g.custom_command('list-protected-operations', 'dataprotection_resource_guard_list_protected_operations')

    from .aaz_operations.backup_instance import (
        ValidateAndCreate as BackupInstanceCreate,
        ValidateForRestore as BackupInstanceValidateRestore,
        RestoreTrigger as BackupInstanceRestoreTrigger,
    )
    self.command_table['dataprotection backup-instance create'] = BackupInstanceCreate(loader=self)
    self.command_table['dataprotection backup-instance validate-for-restore'] = BackupInstanceValidateRestore(loader=self)
    self.command_table['dataprotection backup-instance restore trigger'] = BackupInstanceRestoreTrigger(loader=self)

    from .aaz_operations.backup_policy import Create as BackupPolicyCreate
    self.command_table['dataprotection backup-policy create'] = BackupPolicyCreate(loader=self)

    from .aaz_operations.recovery_point import List as RecoveryPointList
    self.command_table['dataprotection recovery-point list'] = RecoveryPointList(loader=self)

    from .aaz_operations.resource_guard import Update as ResourceGuardUpdate
    self.command_table['dataprotection resource-guard update'] = ResourceGuardUpdate(loader=self)

    from .aaz_operations.resource_guard import Unlock as ResouceGuardMappingUnlock
    self.command_table['dataprotection resource-guard unlock'] = ResouceGuardMappingUnlock(loader=self)
