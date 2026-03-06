# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer


class AcrTransferPipelineScenarioTest(ScenarioTest):
    """Test cases for ACR import/export pipelines with different authentication modes."""

    @ResourceGroupPreparer(name_prefix='cli_test_acr_transfer_export_mi_')
    @StorageAccountPreparer(name_prefix='acrtransfer', kind='StorageV2', sku='Standard_LRS')
    def test_acr_export_pipeline_entra_mi_auth_no_identity(self, resource_group, storage_account):
        """
        Test Case 1: Create export pipeline with entra-mi-auth mode, no identity specified.
        Expected: System-assigned managed identity should be automatically provisioned.
        """
        self.kwargs.update({
            'registry': self.create_random_name('acrtest', 20),
            'pipeline': self.create_random_name('pipeline', 20),
            'storage_account': storage_account,
            'container': 'export-container'
        })

        # Create registry
        self.cmd('acr create -g {rg} -n {registry} --sku Premium')

        # Create storage container
        self.cmd('storage container create -n {container} --account-name {storage_account}')

        # Create export pipeline with entra-mi-auth, no identity specified
        result = self.cmd('acr export-pipeline create -g {rg} -r {registry} -n {pipeline} '
                         '--storage-access-mode entra-mi-auth '
                         '--storage-container-uri https://{storage_account}.blob.core.windows.net/{container}',
                         checks=[
                             self.check('name', '{pipeline}'),
                             self.check('provisioningState', 'Succeeded'),
                             self.check('target.storageAccessMode', 'ManagedIdentity'),
                             self.check('identity.type', 'systemAssigned'),
                             self.exists('identity.principalId'),
                             self.check('target.keyVaultUri', None)
                         ]).get_output_in_json()

        # Verify system-assigned identity was created
        self.assertIsNotNone(result['identity']['principalId'])
        self.assertEqual(result['identity']['type'], 'systemAssigned')

        # Clean up
        self.cmd('acr export-pipeline delete -g {rg} -r {registry} -n {pipeline}')
        self.cmd('acr delete -g {rg} -n {registry} --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_acr_transfer_export_sas_')
    @StorageAccountPreparer(name_prefix='acrtransfer', kind='StorageV2', sku='Standard_LRS')
    def test_acr_export_pipeline_sas_token(self, resource_group, storage_account):
        """
        Test Case 2: Create export pipeline with storage-sas-token mode.
        Expected: Pipeline should be created with SasToken mode and keyVaultUri set.
        """
        self.kwargs.update({
            'registry': self.create_random_name('acrtest', 20),
            'pipeline': self.create_random_name('pipeline', 20),
            'storage_account': storage_account,
            'container': 'export-container',
            'keyvault': self.create_random_name('kv', 20),
            'secret': 'sas-token-secret'
        })

        # Create registry
        self.cmd('acr create -g {rg} -n {registry} --sku Premium')

        # Create key vault with access policies (not RBAC)
        self.cmd('keyvault create -g {rg} -n {keyvault} --enable-rbac-authorization false')
        
        # Generate SAS token and store in Key Vault
        from datetime import datetime, timedelta
        expiry = (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%dT%H:%MZ')
        sas_token = self.cmd('storage container generate-sas '
                            '--account-name {storage_account} '
                            '--name {container} '
                            '--permissions racwdl '
                            f'--expiry {expiry} '
                            '-o tsv').output.strip()
        
        self.kwargs['sas_token'] = sas_token
        self.cmd('keyvault secret set --vault-name {keyvault} -n {secret} --value "{sas_token}"')

        # Create storage container
        self.cmd('storage container create -n {container} --account-name {storage_account}')

        # Create export pipeline with storage-sas-token
        self.cmd('acr export-pipeline create -g {rg} -r {registry} -n {pipeline} '
                '--storage-access-mode storage-sas-token '
                '--secret-uri https://{keyvault}.vault.azure.net/secrets/{secret} '
                '--storage-container-uri https://{storage_account}.blob.core.windows.net/{container}',
                checks=[
                    self.check('name', '{pipeline}'),
                    self.check('provisioningState', 'Succeeded'),
                    self.check('target.storageAccessMode', 'SasToken'),
                    self.check('target.keyVaultUri', 'https://{keyvault}.vault.azure.net/secrets/{secret}'),
                    self.check('identity.type', 'systemAssigned')
                ])

        # Clean up
        self.cmd('acr export-pipeline delete -g {rg} -r {registry} -n {pipeline}')
        self.cmd('acr delete -g {rg} -n {registry} --yes')
        self.cmd('keyvault delete -g {rg} -n {keyvault}')

    @ResourceGroupPreparer(name_prefix='cli_test_acr_transfer_export_uai_')
    @StorageAccountPreparer(name_prefix='acrtransfer', kind='StorageV2', sku='Standard_LRS')
    def test_acr_export_pipeline_entra_mi_auth_user_assigned(self, resource_group, storage_account):
        """
        Test Case 3: Create export pipeline with entra-mi-auth mode and user-assigned identity.
        Expected: Pipeline should use the provided user-assigned managed identity.
        """
        self.kwargs.update({
            'registry': self.create_random_name('acrtest', 20),
            'pipeline': self.create_random_name('pipeline', 20),
            'storage_account': storage_account,
            'container': 'export-container',
            'identity': self.create_random_name('identity', 20)
        })

        # Create registry
        self.cmd('acr create -g {rg} -n {registry} --sku Premium')

        # Create user-assigned managed identity
        identity_result = self.cmd('identity create -g {rg} -n {identity}').get_output_in_json()
        identity_id = identity_result['id']
        self.kwargs['identity_id'] = identity_id

        # Create storage container
        self.cmd('storage container create -n {container} --account-name {storage_account}')

        # Create export pipeline with user-assigned identity
        self.cmd('acr export-pipeline create -g {rg} -r {registry} -n {pipeline} '
                '--storage-access-mode entra-mi-auth '
                '--storage-container-uri https://{storage_account}.blob.core.windows.net/{container} '
                '--assign-identity {identity_id}',
                checks=[
                    self.check('name', '{pipeline}'),
                    self.check('provisioningState', 'Succeeded'),
                    self.check('target.storageAccessMode', 'ManagedIdentity'),
                    self.check('identity.type', 'userAssigned'),
                    self.exists(f'identity.userAssignedIdentities."{identity_id}"'),
                    self.check('target.keyVaultUri', None)
                ])

        # Clean up
        self.cmd('acr export-pipeline delete -g {rg} -r {registry} -n {pipeline}')
        self.cmd('acr delete -g {rg} -n {registry} --yes')
        self.cmd('identity delete -g {rg} -n {identity}')

    @ResourceGroupPreparer(name_prefix='cli_test_acr_transfer_import_mi_')
    @StorageAccountPreparer(name_prefix='acrtransfer', kind='StorageV2', sku='Standard_LRS')
    def test_acr_import_pipeline_entra_mi_auth_no_identity(self, resource_group, storage_account):
        """
        Test Case 4: Create import pipeline with entra-mi-auth mode, no identity specified.
        Expected: System-assigned managed identity should be automatically provisioned.
        """
        self.kwargs.update({
            'registry': self.create_random_name('acrtest', 20),
            'pipeline': self.create_random_name('pipeline', 20),
            'storage_account': storage_account,
            'container': 'import-container'
        })

        # Create registry
        self.cmd('acr create -g {rg} -n {registry} --sku Premium')

        # Create storage container
        self.cmd('storage container create -n {container} --account-name {storage_account}')

        # Create import pipeline with entra-mi-auth, no identity specified
        result = self.cmd('acr import-pipeline create -g {rg} -r {registry} -n {pipeline} '
                         '--storage-access-mode entra-mi-auth '
                         '--storage-container-uri https://{storage_account}.blob.core.windows.net/{container}',
                         checks=[
                             self.check('name', '{pipeline}'),
                             self.check('provisioningState', 'Succeeded'),
                             self.check('source.storageAccessMode', 'ManagedIdentity'),
                             self.check('identity.type', 'systemAssigned'),
                             self.exists('identity.principalId'),
                             self.check('source.keyVaultUri', None)
                         ]).get_output_in_json()

        # Verify system-assigned identity was created
        self.assertIsNotNone(result['identity']['principalId'])
        self.assertEqual(result['identity']['type'], 'systemAssigned')

        # Clean up
        self.cmd('acr import-pipeline delete -g {rg} -r {registry} -n {pipeline}')
        self.cmd('acr delete -g {rg} -n {registry} --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_acr_transfer_import_sas_')
    @StorageAccountPreparer(name_prefix='acrtransfer', kind='StorageV2', sku='Standard_LRS')
    def test_acr_import_pipeline_sas_token(self, resource_group, storage_account):
        """
        Test Case 5: Create import pipeline with storage-sas-token mode.
        Expected: Pipeline should be created with SasToken mode and keyVaultUri set.
        """
        self.kwargs.update({
            'registry': self.create_random_name('acrtest', 20),
            'pipeline': self.create_random_name('pipeline', 20),
            'storage_account': storage_account,
            'container': 'import-container',
            'keyvault': self.create_random_name('kv', 20),
            'secret': 'sas-token-secret'
        })

        # Create registry
        self.cmd('acr create -g {rg} -n {registry} --sku Premium')

        # Create key vault with access policies (not RBAC)
        self.cmd('keyvault create -g {rg} -n {keyvault} --enable-rbac-authorization false')
        
        # Generate SAS token and store in Key Vault
        from datetime import datetime, timedelta
        expiry = (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%dT%H:%MZ')
        sas_token = self.cmd('storage container generate-sas '
                            '--account-name {storage_account} '
                            '--name {container} '
                            '--permissions racwdl '
                            f'--expiry {expiry} '
                            '-o tsv').output.strip()
        
        self.kwargs['sas_token'] = sas_token
        self.cmd('keyvault secret set --vault-name {keyvault} -n {secret} --value "{sas_token}"')

        # Create storage container
        self.cmd('storage container create -n {container} --account-name {storage_account}')

        # Create import pipeline with storage-sas-token
        self.cmd('acr import-pipeline create -g {rg} -r {registry} -n {pipeline} '
                '--storage-access-mode storage-sas-token '
                '--secret-uri https://{keyvault}.vault.azure.net/secrets/{secret} '
                '--storage-container-uri https://{storage_account}.blob.core.windows.net/{container}',
                checks=[
                    self.check('name', '{pipeline}'),
                    self.check('provisioningState', 'Succeeded'),
                    self.check('source.storageAccessMode', 'SasToken'),
                    self.check('source.keyVaultUri', 'https://{keyvault}.vault.azure.net/secrets/{secret}'),
                    self.check('identity.type', 'systemAssigned')
                ])

        # Clean up
        self.cmd('acr import-pipeline delete -g {rg} -r {registry} -n {pipeline}')
        self.cmd('acr delete -g {rg} -n {registry} --yes')
        self.cmd('keyvault delete -g {rg} -n {keyvault}')

    @ResourceGroupPreparer(name_prefix='cli_test_acr_transfer_export_mi_invalid_')
    @StorageAccountPreparer(name_prefix='acrtransfer', kind='StorageV2', sku='Standard_LRS')
    def test_acr_export_pipeline_entra_mi_auth_with_secret_uri_fails(self, resource_group, storage_account):
        """
        Test Case 6: Verify export pipeline creation fails when entra-mi-auth is used with --secret-uri.
        Expected: Command should fail with validation error since --secret-uri is only for SAS token mode.
        """
        self.kwargs.update({
            'registry': self.create_random_name('acrtest', 20),
            'pipeline': self.create_random_name('pipeline', 20),
            'storage_account': storage_account,
            'container': 'export-container',
            'keyvault': 'dummy-keyvault',
            'secret': 'dummy-secret'
        })

        # Create registry
        self.cmd('acr create -g {rg} -n {registry} --sku Premium')

        # Create storage container
        self.cmd('storage container create -n {container} --account-name {storage_account}')

        # Attempt to create export pipeline with entra-mi-auth AND secret-uri (should fail)
        self.cmd('acr export-pipeline create -g {rg} -r {registry} -n {pipeline} '
                 '--storage-access-mode entra-mi-auth '
                 '--secret-uri https://{keyvault}.vault.azure.net/secrets/{secret} '
                 '--storage-container-uri https://{storage_account}.blob.core.windows.net/{container}',
                 expect_failure=True)

        # Clean up
        self.cmd('acr delete -g {rg} -n {registry} --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_acr_transfer_import_mi_invalid_')
    @StorageAccountPreparer(name_prefix='acrtransfer', kind='StorageV2', sku='Standard_LRS')
    def test_acr_import_pipeline_entra_mi_auth_with_secret_uri_fails(self, resource_group, storage_account):
        """
        Test Case 7: Verify import pipeline creation fails when entra-mi-auth is used with --secret-uri.
        Expected: Command should fail with validation error since --secret-uri is only for SAS token mode.
        """
        self.kwargs.update({
            'registry': self.create_random_name('acrtest', 20),
            'pipeline': self.create_random_name('pipeline', 20),
            'storage_account': storage_account,
            'container': 'import-container',
            'keyvault': 'dummy-keyvault',
            'secret': 'dummy-secret'
        })

        # Create registry
        self.cmd('acr create -g {rg} -n {registry} --sku Premium')

        # Create storage container
        self.cmd('storage container create -n {container} --account-name {storage_account}')

        # Attempt to create import pipeline with entra-mi-auth AND secret-uri (should fail)
        self.cmd('acr import-pipeline create -g {rg} -r {registry} -n {pipeline} '
                 '--storage-access-mode entra-mi-auth '
                 '--secret-uri https://{keyvault}.vault.azure.net/secrets/{secret} '
                 '--storage-container-uri https://{storage_account}.blob.core.windows.net/{container}',
                 expect_failure=True)

        # Clean up
        self.cmd('acr delete -g {rg} -n {registry} --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_acr_transfer_import_uai_')
    @StorageAccountPreparer(name_prefix='acrtransfer', kind='StorageV2', sku='Standard_LRS')
    def test_acr_import_pipeline_entra_mi_auth_user_assigned(self, resource_group, storage_account):
        """
        Test Case 11: Create import pipeline with entra-mi-auth mode and user-assigned identity.
        Expected: Pipeline should use the provided user-assigned managed identity.
        """
        self.kwargs.update({
            'registry': self.create_random_name('acrtest', 20),
            'pipeline': self.create_random_name('pipeline', 20),
            'storage_account': storage_account,
            'container': 'import-container',
            'identity': self.create_random_name('identity', 20)
        })

        # Create registry
        self.cmd('acr create -g {rg} -n {registry} --sku Premium')

        # Create user-assigned managed identity
        identity_result = self.cmd('identity create -g {rg} -n {identity}').get_output_in_json()
        identity_id = identity_result['id']
        self.kwargs['identity_id'] = identity_id

        # Create storage container
        self.cmd('storage container create -n {container} --account-name {storage_account}')

        # Create import pipeline with user-assigned identity
        self.cmd('acr import-pipeline create -g {rg} -r {registry} -n {pipeline} '
                '--storage-access-mode entra-mi-auth '
                '--storage-container-uri https://{storage_account}.blob.core.windows.net/{container} '
                '--assign-identity {identity_id}',
                checks=[
                    self.check('name', '{pipeline}'),
                    self.check('provisioningState', 'Succeeded'),
                    self.check('source.storageAccessMode', 'ManagedIdentity'),
                    self.check('identity.type', 'userAssigned'),
                    self.exists(f'identity.userAssignedIdentities."{identity_id}"'),
                    self.check('source.keyVaultUri', None)
                ])

        # Clean up
        self.cmd('acr import-pipeline delete -g {rg} -r {registry} -n {pipeline}')
        self.cmd('acr delete -g {rg} -n {registry} --yes')
        self.cmd('identity delete -g {rg} -n {identity}')


if __name__ == '__main__':
    unittest.main()
