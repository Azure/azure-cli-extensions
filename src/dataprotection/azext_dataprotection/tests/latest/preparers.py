# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import CliTestError, ResourceGroupPreparer
from azure.cli.testsdk.preparers import AbstractPreparer, SingleValueReplacer
from azure.cli.testsdk.base import execute
from azure.cli.core.mock import DummyCli


class VaultPreparer(AbstractPreparer, SingleValueReplacer):
    def __init__(self, name_prefix='clitest-dpp-vault', parameter_name='vault_name',
                 resource_group_location_parameter_name='resource_group_location',
                 resource_group_parameter_name='resource_group',
                 datastore_type='VaultStore', storage_type='LocallyRedundant',
                 msi_type="SystemAssigned", soft_delete_state="On",
                 immutability_state="Disabled"):
        raise CliTestError("The Vault Preparer is not ready yet. Please do not use it right now.")
        super(VaultPreparer, self).__init__(name_prefix, 36)
        self.cli_ctx = DummyCli()
        self.parameter_name = parameter_name
        self.resource_group = None
        self.resource_group_parameter_name = resource_group_parameter_name
        self.location = None
        self.resource_group_location_parameter_name = resource_group_location_parameter_name
        self.datastore_type = datastore_type
        self.storage_type = storage_type
        self.msi_type = msi_type
        self.soft_delete_state = soft_delete_state
        self.immutability_state = immutability_state

    def create_resource(self, name, **kwargs):
        self.resource_group = self._get_resource_group(**kwargs)
        self.location = self._get_resource_group_location(**kwargs)

        cmd = ('az dataprotection backup-vault create --vault-name "{}" -g "{}" -l "{}" '
               '--storage-settings datastore-type="{}" type="{}" --type="{}" '
               '--soft-delete-state "{}" --immutability-state "{}"').format(name, self.resource_group, self.location,
                                                                            self.datastore_type, self.storage_type,
                                                                            self.msi_type, self.soft_delete_state,
                                                                            self.immutability_state)
        execute(self.cli_ctx, cmd)

        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        # Should get cleaned up with Resource Group cleanup
        pass

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create a vault, a resource group is required. Please add ' \
                       'decorator @{} in front of this Vault preparer.'
            raise CliTestError(template.format(ResourceGroupPreparer.__name__,
                                               self.resource_group_parameter_name))

    def _get_resource_group_location(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_location_parameter_name)
        except KeyError:
            template = 'To create a vault, a resource group is required. Please add ' \
                       'decorator @{} in front of this Vault preparer.'
            raise CliTestError(template.format(ResourceGroupPreparer.__name__,
                                               self.resource_group_parameter_name))


class ResourceGuardPreparer(AbstractPreparer, SingleValueReplacer):
    def __init__(self):
        raise CliTestError("The Resource Guard Preparer is not ready yet. Please do not use it right now.")

    def create_resource(self, name, **kwargs):
        pass

    def remove_resource(self, name, **kwargs):
        pass
