# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from .recording_processors import KeyReplacer


class RemoteRenderingAccountScenarioTest(ScenarioTest):

    def __init__(self, method_name):
        super(RemoteRenderingAccountScenarioTest, self).__init__(
            method_name, recording_processors=[KeyReplacer()]
        )

    @ResourceGroupPreparer(location='eastus2', parameter_name_for_location='location')
    def test_remote_rendering_account_scenario(self, resource_group, location):
        self.kwargs.update({
            'rg': resource_group,
            'account_name': 'remote-rendering-account-name',
            'account_name1': 'remote-rendering-account-name1',
            'storage_account_name': 'storage_account_name',
            'storage_account_name1': 'storage_account_name1',
        })

        # Create with minimum parameters
        self.cmd('remote-rendering-account create -g {rg} -n {account_name}', checks=self.not_exists('tags'))

        # Create with more parameters
        self.cmd('remote-rendering-account create -g {rg} -n {account_name1} '
                 '--storage-account-name {storage_account_name} --tag tag=tag',
                 checks=[self.exists('tags'),
                         self.check('storageAccountName', '{storage_account_name}')])

        self.cmd('remote-rendering-account update -g {rg} -n {account_name} '
                 '--storage-account-name {storage_account_name1}',
                 checks=self.check('storageAccountName', '{storage_account_name1}'))

        self.cmd('remote-rendering-account show -g {rg} -n {account_name}')
        self.cmd('remote-rendering-account list -g {rg}', checks=self.check('length(@)', 2))
        self.cmd('remote-rendering-account delete -g {rg} -n {account_name1}')
        self.cmd('remote-rendering-account list -g {rg}', checks=self.check('length(@)', 1))

        # key
        self.cmd('remote-rendering-account key renew -g {rg} -n {account_name}')
        self.cmd('remote-rendering-account key renew -g {rg} -n {account_name} --serial 1')
        self.cmd('remote-rendering-account key renew -g {rg} -n {account_name} --serial 2')
        self.cmd('remote-rendering-account key show -g {rg} -n {account_name}')
