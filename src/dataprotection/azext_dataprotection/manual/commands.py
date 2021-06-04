# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
# pylint: disable=line-too-long

from azure.cli.core.commands import CliCommandType
from azext_dataprotection.generated._client_factory import (
    cf_backup_instance, cf_backup_vault
)

from azext_dataprotection.manual._client_factory import cf_resource_graph_client


def load_command_table(self, _):
    with self.command_group('dataprotection backup-instance') as g:
        g.custom_command('initialize', "dataprotection_backup_instance_initialize")
        g.custom_command('update-policy', "dataprotection_backup_instance_update_policy", client_factory=cf_backup_instance, supports_no_wait=True)
        g.custom_command('list-from-resourcegraph', 'dataprotection_backup_instance_list_from_resourcegraph', client_factory=cf_resource_graph_client)

    with self.command_group('dataprotection backup-policy') as g:
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

    dataprotection_backup_instance = CliCommandType(
        operations_tmpl='azext_dataprotection.vendored_sdks.dataprotection.operations._backup_instances_operations#BackupInstancesOperations.{}',
        client_factory=cf_backup_instance
    )

    with self.command_group('dataprotection backup-instance restore', dataprotection_backup_instance, client_factory=cf_backup_instance) as g:
        g.custom_command('initialize-for-data-recovery', 'restore_initialize_for_data_recovery')
        g.custom_command('initialize-for-item-recovery', 'restore_initialize_for_item_recovery')

    with self.command_group('dataprotection backup-vault') as g:
        g.custom_command('list', 'dataprotection_backup_vault_list', client_factory=cf_backup_vault)
