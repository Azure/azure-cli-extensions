# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from datetime import datetime, timedelta
from azure.cli.testsdk import (LiveScenarioTest, ResourceGroupPreparer, StorageAccountPreparer,
                               JMESPathCheck, JMESPathCheckExists, NoneCheck)
from ..storage_test_util import StorageScenarioMixin


class StorageSASScenario(StorageScenarioMixin, LiveScenarioTest):
    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='blobsas', kind='StorageV2', location='eastus2euap')
    def test_storage_blob_sas_permission_scenario(self, resource_group, storage_account):
        """
        Test service SAS operations.

        A service SAS is secured with the storage account key. A service SAS delegates access to a resource in only
        one of the Azure Storage services: Blob storage, Queue storage, Table storage, or Azure Files.
        """
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

        # ----account key----
        # test sas-token for a container
        sas = self.storage_cmd('storage container generate-sas -n {} --https-only --permissions dlrwt --expiry {} -otsv',
                               account_info, container, expiry).output.strip()
        self.kwargs['container_sas'] = sas
        self.cmd('storage blob upload -c {container} -f "{local_file}" -n {blob} '
                 '--account-name {account} --sas-token "{container_sas}"')

        # test sas-token for a blob
        sas = self.storage_cmd('storage blob generate-sas -c {} -n {} --https-only --permissions acdrwt --expiry {} '
                               '-otsv', account_info, container, blob_name, expiry).output.strip()
        self.kwargs['blob_sas'] = sas
        self.cmd('storage blob upload -c {container} -f "{local_file}" -n {blob} --overwrite '
                 '--account-name {account} --sas-token "{blob_sas}" --tags test=tag ')

        self.cmd('storage blob show -c {container} -n {blob} --account-name {account} --sas-token {blob_sas}') \
            .assert_with_checks(JMESPathCheck('name', blob_name),
                                JMESPathCheck('tagCount', 1))

        self.cmd('storage blob tag list -n {} -c {} --account-name {} --sas-token "{}" '.format(blob_name,
                 container, storage_account, sas)).assert_with_checks(JMESPathCheck('test', 'tag'))

        # ----connection string----
        connection_str = self.cmd('storage account show-connection-string -n {account}  --query connectionString '
                                  '-otsv').output.strip()
        self.kwargs['con_str'] = connection_str
        # test sas-token for a container
        sas = self.cmd('storage container generate-sas -n {container} --https-only --permissions dlrw '
                       '--connection-string {con_str} --expiry {expiry} -otsv').output.strip()
        self.kwargs['container_sas'] = sas
        self.cmd('storage blob upload -c {container} -f "{local_file}" -n {blob} '
                 '--account-name {account} --sas-token "{container_sas}"')

        # test sas-token for a blob
        sas = self.cmd('storage blob generate-sas -c {container} -n {blob} --account-name {account} --https-only '
                       '--permissions acdrwt --expiry {expiry} -otsv').output.strip()
        self.kwargs['blob_sas'] = sas
        self.cmd('storage blob show -c {container} -n {blob} --account-name {account} --sas-token {blob_sas}') \
            .assert_with_checks(JMESPathCheck('name', blob_name))

    @ResourceGroupPreparer()
    @StorageAccountPreparer()
    def test_storage_blob_sas_permission_scenario(self, resource_group, storage_account):
        """
        Test service SAS with stored access policy.

        A stored access policy is defined on a resource container, which can be a blob container, table, queue,
        or file share. The stored access policy can be used to manage constraints for one or more service shared
        access signatures. When you associate a service SAS with a stored access policy, the SAS inherits the
        constraints—the start time, expiry time, and permissions—defined for the stored access policy.
        """
        expiry = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%MZ')

        account_info = self.get_account_info(resource_group, storage_account)
        container = self.create_container(account_info)
        local_file = self.create_temp_file(128, full_random=False)
        blob_name = self.create_random_name('blob', 16)
        policy = self.create_random_name('policy', 16)

        self.storage_cmd('storage container policy create -c {} -n {} --expiry {} --permissions acdlrw', account_info,
                         container, policy, expiry)
        self.storage_cmd('storage container policy list -c {} ', account_info, container)\
            .assert_with_checks(JMESPathCheckExists('{}.expiry'.format(policy)),
                                JMESPathCheck('{}.permission'.format(policy), 'racwdl'))
        self.storage_cmd('storage container policy show -c {} -n {} ', account_info, container, policy, expiry)\
            .assert_with_checks(JMESPathCheckExists('expiry'),
                                JMESPathCheck('permission', 'racwdl'))

        sas = self.storage_cmd('storage blob generate-sas -n {} -c {} --policy-name {} -otsv ', account_info, blob_name,
                               container, policy).output.strip()

        self.storage_cmd('storage blob upload -n {} -c {} -f "{}" --sas-token "{}" ', account_info, blob_name, container,
                         local_file, sas)

        self.storage_cmd('storage container policy update -c {} -n {} --permissions acdlr', account_info, container,
                         policy)
        self.storage_cmd('storage container policy show -c {} -n {} ', account_info, container, policy)\
            .assert_with_checks(JMESPathCheckExists('expiry'),
                                JMESPathCheck('permission', 'racdl'))
        self.storage_cmd('storage container policy delete -c {} -n {} ', account_info, container, policy)
        self.storage_cmd('storage container policy list -c {} ', account_info, container) \
            .assert_with_checks(NoneCheck())
