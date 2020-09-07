# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
from azure.cli.testsdk import (ScenarioTest, JMESPathCheck, JMESPathCheckExists, ResourceGroupPreparer,
                               StorageAccountPreparer, api_version_constraint, live_only)
from azure.cli.core.profiles import ResourceType
from ..storage_test_util import StorageScenarioMixin
from knack.util import CLIError


class StorageOauthTests(StorageScenarioMixin, ScenarioTest):
    def oauth_cmd(self, cmd, *args, **kwargs):
        return self.cmd(cmd + ' --auth-mode login', *args, **kwargs)

    @live_only()
    @ResourceGroupPreparer()
    @StorageAccountPreparer()
    def test_storage_blob_sas_oauth(self, resource_group, storage_account):
        """
        Test user delegaiton SAS.
        A user delegation SAS is secured with Azure Active Directory (Azure AD) credentials and also by the
        permissions specified for the SAS. A user delegation SAS applies to Blob storage only.

        """
        from datetime import datetime, timedelta
        expiry = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%MZ')

        account_info = self.get_account_info(resource_group, storage_account)
        container = self.create_container(account_info)
        local_file = self.create_temp_file(128, full_random=False)
        blob_name = self.create_random_name('blob', 16)

        self.kwargs.update({
            'expiry': expiry,
            'account': storage_account,
            'container': container,
            'local_file': local_file,
            'blob': blob_name
        })

        # ----user delegation key----
        with self.assertRaisesRegexp(CLIError, "incorrect usage: specify --as-user when --auth-mode login"):
            self.oauth_cmd('storage blob generate-sas --account-name {account} -n {blob} -c {container} '
                           '--expiry {expiry} --permissions r --https-only ')

        # test sas-token for a container
        sas = self.oauth_cmd('storage container generate-sas -n {container} --https-only --permissions dlrw '
                             '--expiry {expiry} --as-user --account-name {account} -otsv').output.strip()
        self.kwargs['container_sas'] = sas
        self.cmd('storage blob upload -c {container} -f "{local_file}" -n {blob} '
                 '--account-name {account} --sas-token "{container_sas}"')

        # test sas-token for a blob
        sas = self.oauth_cmd('storage blob generate-sas -c {container} -n {blob} --https-only --permissions acdrw '
                             '--expiry {expiry} --as-user --account-name {account} -otsv').output.strip()
        self.kwargs['blob_sas'] = sas
        self.cmd('storage blob upload -c {container} -f "{local_file}" -n {blob} --overwrite '
                 '--account-name {account} --sas-token "{blob_sas}"')

        self.cmd('storage blob show -c {container} -n {blob} --account-name {account} --sas-token {blob_sas}') \
            .assert_with_checks(JMESPathCheck('name', blob_name))

    @ResourceGroupPreparer()
    @StorageAccountPreparer()
    def test_storage_append_blob_upload_oauth(self, resource_group, storage_account):
        account_info = self.get_account_info(resource_group, storage_account)
        self.kwargs = {
            'account': storage_account,
            'container': self.create_container(account_info),
            'local_file': self.create_temp_file(1, full_random=False),
            'blob': self.create_random_name('blob', 16)
        }

        # create an append blob with pre-condition
        self.oauth_cmd('storage blob upload -c {container} -f "{local_file}" -n {blob} --type append --if-none-match * '
                       '--account-name {account} ')
        result = self.oauth_cmd('storage blob show -n {blob} -c {container} --account-name {account}')\
            .get_output_in_json()
        self.assertEqual(result['properties']['blobType'], 'AppendBlob')
        length = int(result['properties']['contentLength'])

        # append if-none-match should throw exception
        with self.assertRaises(Exception):
            self.oauth_cmd('storage blob upload -c {container} -f "{local_file}" -n {blob} --type append '
                           '--if-none-match * --account-name {} ')

        # append an append blob
        self.oauth_cmd('storage blob upload -c {container} -f "{local_file}" -n {blob} --type append '
                       '--account-name {account} ')
        self.oauth_cmd('storage blob show -n {blob} -c {container} --account-name {account}').assert_with_checks(
            JMESPathCheck('properties.contentLength', length * 2),
            JMESPathCheck('properties.blobType', 'AppendBlob')
        )

        # append an append blob with maxsize_condition
        with self.assertRaises(Exception):
            self.oauth_cmd('storage blob upload -c {container} -f "{local_file}" -n {blob} --type append '
                           '--maxsize-condition 1000 --account-name {account} ')

        # append an append blob with overwrite
        self.oauth_cmd('storage blob upload -c {container} -f "{local_file}" -n {blob} --type append '
                       '--overwrite --account-name {account} ')
        self.oauth_cmd('storage blob show -n {blob} -c {container} --account-name {account}').assert_with_checks(
            JMESPathCheck('properties.contentLength', length),
            JMESPathCheck('properties.blobType', 'AppendBlob')
        )
