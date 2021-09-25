# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from unittest import mock


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

class Cosmosdb_previewIdentityTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_managed_service_identity')
    @KeyVaultPreparer(name_prefix='cli', name_len=15, location='eastus2', additional_params='--enable-purge-protection')
    def test_cosmosdb_preview_identity(self, resource_group, key_vault):
        key_name = self.create_random_name(prefix='cli', length=15)
        key_uri = "https://{}.vault.azure.net/keys/{}".format(key_vault, key_name)

        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15),
            'acc2': self.create_random_name(prefix='cli', length=15),
            'kv_name': key_vault,
            'key_name': key_name,
            'key_uri': key_uri,
            'location': "eastus2",
            'id1': self.create_random_name(prefix='cli', length=15),
            'id2': self.create_random_name(prefix='cli', length=15)
        })

        self.cmd('az keyvault set-policy -n {kv_name} -g {rg} --spn a232010e-820c-4083-83bb-3ace5fc29d0b --key-permissions get unwrapKey wrapKey')
        self.cmd('az keyvault key create -n {key_name} --kty RSA --size 3072 --vault-name {kv_name}')

        cmk_account = self.cmd('az cosmosdb create -n {acc} -g {rg} --locations regionName={location} failoverPriority=0 --key-uri {key_uri} --assign-identity [system] --default-identity FirstPartyIdentity').get_output_in_json()

        assert cmk_account["keyVaultKeyUri"] == key_uri
        assert cmk_account["defaultIdentity"] == 'FirstPartyIdentity'
        assert cmk_account["identity"]['type'] == 'SystemAssigned'

        identity_output = self.cmd('az cosmosdb identity remove -n {acc} -g {rg}').get_output_in_json()
        assert identity_output["type"] == "None"

        identity_output = self.cmd('az cosmosdb identity assign -n {acc} -g {rg}').get_output_in_json()
        assert identity_output["type"] == "SystemAssigned"

        identity_principal_id = identity_output["principalId"]
        self.kwargs.update({
            'identity_principal_id': identity_principal_id
        })
        self.cmd('az keyvault set-policy -n {kv_name} -g {rg} --object-id {identity_principal_id} --key-permissions get unwrapKey wrapKey')
        
        # System assigned identity tests
        cmk_account = self.cmd('az cosmosdb update -n {acc} -g {rg} --default-identity SystemAssignedIdentity').get_output_in_json()
        assert cmk_account["defaultIdentity"] == 'SystemAssignedIdentity'

        identity_output = self.cmd('az cosmosdb identity remove -n {acc} -g {rg}').get_output_in_json()
        assert identity_output["type"] == "None"

        identity_output = self.cmd('az cosmosdb identity assign -n {acc} -g {rg}').get_output_in_json()
        assert identity_output["type"] == "SystemAssigned"

        # User assigned identity tests
        user_identity1 = self.cmd('az identity create -n {id1} -g {rg}').get_output_in_json()
        user_identity2 = self.cmd('az identity create -n {id2} -g {rg}').get_output_in_json()
        id1 = user_identity1["id"]
        id1principal = user_identity1["principalId"]
        id2 = user_identity2["id"]
        self.kwargs.update({
            'id1': id1,
            'id2': id2,
            'id1principal': id1principal
        })

        identity_output = self.cmd('az cosmosdb identity assign -n {acc} -g {rg} --identities {id1}').get_output_in_json()
        assert identity_output["type"] == "SystemAssigned,UserAssigned"
        assert list(identity_output["userAssignedIdentities"])[0] == id1
        assert len(identity_output["userAssignedIdentities"]) == 1

        identity_output = self.cmd('az cosmosdb identity assign -n {acc} -g {rg} --identities {id2}').get_output_in_json()
        assert identity_output["type"] == "SystemAssigned,UserAssigned"
        assert (list(identity_output["userAssignedIdentities"])[0] == id2 or list(identity_output["userAssignedIdentities"])[1] == id2)
        assert len(identity_output["userAssignedIdentities"]) == 2

        identity_output = self.cmd('az cosmosdb identity remove -n {acc} -g {rg}').get_output_in_json()
        assert identity_output["type"] == "UserAssigned"
        assert len(identity_output["userAssignedIdentities"]) == 2

        identity_output = self.cmd('az cosmosdb identity remove -n {acc} -g {rg} --identities {id2}').get_output_in_json()
        assert identity_output["type"] == "UserAssigned"
        assert list(identity_output["userAssignedIdentities"])[0] == id1
        assert len(identity_output["userAssignedIdentities"]) == 1

        identity_output = self.cmd('az cosmosdb identity assign -n {acc} -g {rg} --identities {id2}').get_output_in_json()
        assert identity_output["type"] == "UserAssigned"
        assert (list(identity_output["userAssignedIdentities"])[0] == id2 or list(identity_output["userAssignedIdentities"])[1] == id2)
        assert len(identity_output["userAssignedIdentities"]) == 2

        identity_output = self.cmd('az cosmosdb identity remove -n {acc} -g {rg} --identities {id1} {id2}').get_output_in_json()
        assert identity_output["type"] == "None"

        identity_output = self.cmd('az cosmosdb identity assign -n {acc} -g {rg} --identities {id1} {id2} [system]').get_output_in_json()
        assert identity_output["type"] == "SystemAssigned,UserAssigned"
        assert len(identity_output["userAssignedIdentities"]) == 2
        
        identity_output = self.cmd('az cosmosdb identity remove -n {acc} -g {rg} --identities {id2}').get_output_in_json()
        assert identity_output["type"] == "SystemAssigned,UserAssigned"
        assert len(identity_output["userAssignedIdentities"]) == 1
        
        identity_output = self.cmd('az cosmosdb identity remove -n {acc} -g {rg} --identities {id1}').get_output_in_json()
        assert identity_output["type"] == "SystemAssigned"
        
        identity_output = self.cmd('az cosmosdb identity assign -n {acc} -g {rg} --identities {id1} {id2} [system]').get_output_in_json()
        assert identity_output["type"] == "SystemAssigned,UserAssigned"
        assert len(identity_output["userAssignedIdentities"]) == 2
        identity_output = self.cmd('az cosmosdb identity remove -n {acc} -g {rg} --identities {id1} {id2} [system]').get_output_in_json()
        assert identity_output["type"] == "None"
        
        # Default identity tests
        self.cmd('az keyvault set-policy --name {kv_name} --object-id {id1principal} --key-permissions get unwrapKey wrapKey')
        default_id_acct = self.cmd('az cosmosdb create -n {acc2} -g {rg} --locations regionName={location} failoverPriority=0 --key-uri {key_uri} --assign-identity {id1} --default-identity "UserAssignedIdentity={id1}"').get_output_in_json()
        assert default_id_acct["identity"]["type"] == "UserAssigned"
        assert list(default_id_acct["identity"]["userAssignedIdentities"])[0] == id1
        assert default_id_acct["defaultIdentity"] == "UserAssignedIdentity=" + id1