# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from azure.cli.testsdk import (LiveScenarioTest, ResourceGroupPreparer, StorageAccountPreparer,
                               JMESPathCheck, live_only)
from ..storage_test_util import StorageScenarioMixin


class StorageSASScenario(StorageScenarioMixin, LiveScenarioTest):
    @ResourceGroupPreparer()
    @StorageAccountPreparer()
    def test_storage_blob_sas_scenario(self, resource_group, storage_account):
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

        # account key
        # test sas-token for a container
        sas = self.storage_cmd('storage container generate-sas -n {} --https-only --permissions dlrw --expiry {} -otsv',
                               account_info, container, expiry).output.strip()
        self.kwargs['container_sas'] = sas
        self.cmd('storage blob upload -c {container} -f "{local_file}" -n {blob} '
                 '--account-name {account} --sas-token "{container_sas}"')

        # test sas-token for a file
        sas = self.storage_cmd('storage blob generate-sas -c {} -n {} --https-only --permissions acdrw --expiry {} '
                               '-otsv', account_info, container, blob_name, expiry).output.strip()
        self.kwargs['blob_sas'] = sas
        self.cmd('storage blob show -c {container} -n {blob} --account-name {account} --sas-token {blob_sas}') \
            .assert_with_checks(JMESPathCheck('name', blob_name))

        # connection string
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
                       '--permissions acdrw --expiry {expiry} -otsv').output.strip()
        self.kwargs['blob_sas'] = sas
        self.cmd('storage blob show -c {container} -n {blob} --account-name {account} --sas-token {blob_sas}') \
            .assert_with_checks(JMESPathCheck('name', blob_name))

