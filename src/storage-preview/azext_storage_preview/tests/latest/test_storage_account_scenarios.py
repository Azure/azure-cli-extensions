# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, JMESPathCheck, ResourceGroupPreparer, StorageAccountPreparer,
                               api_version_constraint)
from .storage_test_util import StorageScenarioMixin
from ...profiles import CUSTOM_MGMT_PREVIEW_STORAGE
from azure_devtools.scenario_tests import AllowLargeResponse


@api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2016-12-01')
class StorageAccountTests(StorageScenarioMixin, ScenarioTest):
    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2017-06-01')
    @ResourceGroupPreparer(name_prefix='cli_test_storage_service_endpoints')
    def test_storage_account_service_endpoints(self, resource_group):
        kwargs = {
            'rg': resource_group,
            'acc': self.create_random_name(prefix='cli', length=24),
            'vnet': 'vnet1',
            'subnet': 'subnet1'
        }
        self.cmd('storage account create -g {rg} -n {acc} --bypass Metrics --default-action Deny --https-only'.format(**kwargs),
                 checks=[
                     JMESPathCheck('networkRuleSet.bypass', 'Metrics'),
                     JMESPathCheck('networkRuleSet.defaultAction', 'Deny')])
        self.cmd('storage account update -g {rg} -n {acc} --bypass Logging --default-action Allow'.format(**kwargs),
                 checks=[
                     JMESPathCheck('networkRuleSet.bypass', 'Logging'),
                     JMESPathCheck('networkRuleSet.defaultAction', 'Allow')])
        self.cmd('storage account update -g {rg} -n {acc} --set networkRuleSet.default_action=deny'.format(**kwargs),
                 checks=[
                     JMESPathCheck('networkRuleSet.bypass', 'Logging'),
                     JMESPathCheck('networkRuleSet.defaultAction', 'Deny')])

        self.cmd('network vnet create -g {rg} -n {vnet} --subnet-name {subnet}'.format(**kwargs))
        self.cmd(
            'network vnet subnet update -g {rg} --vnet-name {vnet} -n {subnet} --service-endpoints Microsoft.Storage'.format(
                **kwargs))

        self.cmd('storage account network-rule add -g {rg} --account-name {acc} --ip-address 25.1.2.3'.format(**kwargs))
        # test network-rule add idempotent
        self.cmd('storage account network-rule add -g {rg} --account-name {acc} --ip-address 25.1.2.3'.format(**kwargs))
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {acc} --ip-address 25.2.0.0/24'.format(**kwargs))
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {acc} --vnet-name {vnet} --subnet {subnet}'.format(
                **kwargs))
        self.cmd('storage account network-rule list -g {rg} --account-name {acc}'.format(**kwargs), checks=[
            JMESPathCheck('length(ipRules)', 2),
            JMESPathCheck('length(virtualNetworkRules)', 1)
        ])
        # test network-rule add idempotent
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {acc} --vnet-name {vnet} --subnet {subnet}'.format(
                **kwargs))
        self.cmd('storage account network-rule list -g {rg} --account-name {acc}'.format(**kwargs), checks=[
            JMESPathCheck('length(ipRules)', 2),
            JMESPathCheck('length(virtualNetworkRules)', 1)
        ])
        self.cmd(
            'storage account network-rule remove -g {rg} --account-name {acc} --ip-address 25.1.2.3'.format(**kwargs))
        self.cmd(
            'storage account network-rule remove -g {rg} --account-name {acc} --vnet-name {vnet} --subnet {subnet}'.format(
                **kwargs))
        self.cmd('storage account network-rule list -g {rg} --account-name {acc}'.format(**kwargs), checks=[
            JMESPathCheck('length(ipRules)', 1),
            JMESPathCheck('length(virtualNetworkRules)', 0)
        ])

    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2017-06-01')
    @ResourceGroupPreparer(location='southcentralus')
    def test_create_storage_account_with_assigned_identity(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        cmd = 'az storage account create -n {} -g {} --sku Standard_LRS --assign-identity'.format(name, resource_group)
        result = self.cmd(cmd).get_output_in_json()

        self.assertIn('identity', result)
        self.assertTrue(result['identity']['principalId'])
        self.assertTrue(result['identity']['tenantId'])

    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2017-06-01')
    @ResourceGroupPreparer(location='southcentralus')
    def test_update_storage_account_with_assigned_identity(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        create_cmd = 'az storage account create -n {} -g {} --sku Standard_LRS'.format(name, resource_group)
        self.cmd(create_cmd, checks=[JMESPathCheck('identity', None)])

        update_cmd = 'az storage account update -n {} -g {} --assign-identity'.format(name, resource_group)
        result = self.cmd(update_cmd).get_output_in_json()

        self.assertIn('identity', result)
        self.assertTrue(result['identity']['principalId'])
        self.assertTrue(result['identity']['tenantId'])

    @AllowLargeResponse()
    @ResourceGroupPreparer(parameter_name_for_location='location')
    def test_create_storage_account(self, resource_group, location):
        name = self.create_random_name(prefix='cli', length=24)

        self.cmd('az storage account create -n {} -g {} --sku {} -l {}'.format(
            name, resource_group, 'Standard_LRS', location))

        self.cmd('storage account check-name --name {}'.format(name), checks=[
            JMESPathCheck('nameAvailable', False),
            JMESPathCheck('reason', 'AlreadyExists')
        ])

        self.cmd('storage account list -g {}'.format(resource_group), checks=[
            JMESPathCheck('[0].location', 'westus'),
            JMESPathCheck('[0].sku.name', 'Standard_LRS'),
            JMESPathCheck('[0].resourceGroup', resource_group)
        ])

        self.cmd('az storage account show -n {} -g {}'.format(name, resource_group), checks=[
            JMESPathCheck('name', name),
            JMESPathCheck('location', location),
            JMESPathCheck('sku.name', 'Standard_LRS'),
            JMESPathCheck('kind', 'StorageV2')
        ])

        self.cmd('az storage account show -n {}'.format(name), checks=[
            JMESPathCheck('name', name),
            JMESPathCheck('location', location),
            JMESPathCheck('sku.name', 'Standard_LRS'),
            JMESPathCheck('kind', 'StorageV2')
        ])

        self.cmd('storage account show-connection-string -g {} -n {} --protocol http'.format(
            resource_group, name), checks=[
            JMESPathCheck("contains(connectionString, 'https')", False),
            JMESPathCheck("contains(connectionString, '{}')".format(name), True)])

        self.cmd('storage account update -g {} -n {} --tags foo=bar cat'
                 .format(resource_group, name),
                 checks=JMESPathCheck('tags', {'cat': '', 'foo': 'bar'}))
        self.cmd('storage account update -g {} -n {} --sku Standard_GRS --tags'
                 .format(resource_group, name),
                 checks=[JMESPathCheck('tags', {}),
                         JMESPathCheck('sku.name', 'Standard_GRS')])
        self.cmd('storage account update -g {} -n {} --set tags.test=success'
                 .format(resource_group, name),
                 checks=JMESPathCheck('tags', {'test': 'success'}))
        self.cmd('storage account delete -g {} -n {} --yes'.format(resource_group, name))
        self.cmd('storage account check-name --name {}'.format(name),
                 checks=JMESPathCheck('nameAvailable', True))

        large_file_name = self.create_random_name(prefix='cli', length=24)
        self.cmd('storage account create -g {} -n {} --sku {} --enable-large-file-share'.format(
            resource_group, large_file_name, 'Standard_LRS'))
        self.cmd('az storage account show -n {} -g {}'.format(large_file_name, resource_group), checks=[
            JMESPathCheck('name', large_file_name),
            JMESPathCheck('sku.name', 'Standard_LRS'),
            JMESPathCheck('largeFileSharesState', 'Enabled')
        ])

    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2019-06-01')
    @ResourceGroupPreparer(location='eastus2euap')
    def test_create_storage_account_with_double_encryption(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        self.cmd('az storage account create -n {} -g {} --require-infrastructure-encryption'.format(
            name, resource_group), checks=[
            JMESPathCheck('name', name),
            JMESPathCheck('encryption.requireInfrastructureEncryption', True)
        ])
        self.cmd('az storage account show -n {} -g {}'.format(name, resource_group), checks=[
            JMESPathCheck('name', name),
            JMESPathCheck('encryption.requireInfrastructureEncryption', True)
        ])

    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2017-10-01')
    @ResourceGroupPreparer(parameter_name_for_location='location', location='southcentralus')
    def test_create_storage_account_v2(self, resource_group, location):
        self.kwargs.update({
            'name': self.create_random_name(prefix='cli', length=24),
            'loc': location
        })

        self.cmd('storage account create -n {name} -g {rg} -l {loc} --kind StorageV2',
                 checks=[JMESPathCheck('kind', 'StorageV2')])

        self.cmd('storage account check-name --name {name}', checks=[
            JMESPathCheck('nameAvailable', False),
            JMESPathCheck('reason', 'AlreadyExists')
        ])

    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2016-01-01')
    @ResourceGroupPreparer(location='southcentralus')
    def test_storage_create_default_sku(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        create_cmd = 'az storage account create -n {} -g {}'.format(name, resource_group)
        self.cmd(create_cmd, checks=[JMESPathCheck('sku.name', 'Standard_RAGRS')])

    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2017-10-01')
    @ResourceGroupPreparer(location='southcentralus')
    def test_storage_create_default_kind(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        create_cmd = 'az storage account create -n {} -g {}'.format(name, resource_group)
        self.cmd(create_cmd, checks=[JMESPathCheck('kind', 'StorageV2')])

    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2018-02-01')
    @ResourceGroupPreparer(location='southcentralus', name_prefix='cli_storage_account_hns')
    def test_storage_create_with_hns(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        create_cmd = 'az storage account create -n {} -g {} --kind StorageV2 --hns'.format(name, resource_group)
        self.cmd(create_cmd, checks=[JMESPathCheck('isHnsEnabled', True)])

    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2018-02-01')
    @ResourceGroupPreparer(location='southcentralus', name_prefix='cli_storage_account_hns')
    def test_storage_create_with_hns_true(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        create_cmd = 'az storage account create -n {} -g {} --kind StorageV2 --hns true'.format(name, resource_group)
        self.cmd(create_cmd, checks=[JMESPathCheck('isHnsEnabled', True)])

    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2018-02-01')
    @ResourceGroupPreparer(location='southcentralus', name_prefix='cli_storage_account_hns')
    def test_storage_create_with_hns_false(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        create_cmd = 'az storage account create -n {} -g {} --kind StorageV2 --hns false'.format(name, resource_group)
        self.cmd(create_cmd, checks=[JMESPathCheck('isHnsEnabled', False)])

    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2019-06-01')
    @ResourceGroupPreparer(location='eastus2euap', name_prefix='cli_storage_account_encryption')
    def test_storage_create_with_encryption_key_type(self, resource_group):
        name = self.create_random_name(prefix='cliencryption', length=24)
        create_cmd = 'az storage account create -n {} -g {} --kind StorageV2 -t Account -q Service'.format(
            name, resource_group)
        self.cmd(create_cmd, checks=[
            JMESPathCheck('encryption.services.queue', None),
            JMESPathCheck('encryption.services.table.enabled', True),
            JMESPathCheck('encryption.services.table.keyType', 'Account'),
        ])

    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2019-04-01')
    @ResourceGroupPreparer(location='eastus', name_prefix='cli_storage_account')
    def test_storage_create_with_public_access(self, resource_group):
        name1 = self.create_random_name(prefix='cli', length=24)
        name2 = self.create_random_name(prefix='cli', length=24)
        name3 = self.create_random_name(prefix='cli', length=24)
        self.cmd('az storage account create -n {} -g {} --allow-blob-public-access'.format(name1, resource_group),
                 checks=[JMESPathCheck('allowBlobPublicAccess', True)])

        self.cmd('az storage account create -n {} -g {} --allow-blob-public-access true'.format(name2, resource_group),
                 checks=[JMESPathCheck('allowBlobPublicAccess', True)])

        self.cmd('az storage account create -n {} -g {} --allow-blob-public-access false'.format(name3, resource_group),
                 checks=[JMESPathCheck('allowBlobPublicAccess', False)])

    @AllowLargeResponse()
    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2019-04-01')
    @ResourceGroupPreparer(location='eastus', name_prefix='cli_storage_account')
    @StorageAccountPreparer(name_prefix='blob')
    def test_storage_update_with_public_access(self, storage_account):
        self.cmd('az storage account update -n {} --allow-blob-public-access'.format(storage_account),
                 checks=[JMESPathCheck('allowBlobPublicAccess', True)])

        self.cmd('az storage account update -n {} --allow-blob-public-access true'.format(storage_account),
                 checks=[JMESPathCheck('allowBlobPublicAccess', True)])

        self.cmd('az storage account update -n {} --allow-blob-public-access false'.format(storage_account),
                 checks=[JMESPathCheck('allowBlobPublicAccess', False)])

    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2019-04-01')
    @ResourceGroupPreparer(location='eastus', name_prefix='cli_storage_account')
    def test_storage_create_with_min_tls(self, resource_group):
        name1 = self.create_random_name(prefix='cli', length=24)
        name2 = self.create_random_name(prefix='cli', length=24)
        name3 = self.create_random_name(prefix='cli', length=24)
        name4 = self.create_random_name(prefix='cli', length=24)
        self.cmd('az storage account create -n {} -g {}'.format(name1, resource_group),
                 checks=[JMESPathCheck('minimumTlsVersion', None)])

        self.cmd('az storage account create -n {} -g {} --min-tls-version TLS1_0'.format(name2, resource_group),
                 checks=[JMESPathCheck('minimumTlsVersion', 'TLS1_0')])

        self.cmd('az storage account create -n {} -g {} --min-tls-version TLS1_1'.format(name3, resource_group),
                 checks=[JMESPathCheck('minimumTlsVersion', 'TLS1_1')])

        self.cmd('az storage account create -n {} -g {} --min-tls-version TLS1_2'.format(name4, resource_group),
                 checks=[JMESPathCheck('minimumTlsVersion', 'TLS1_2')])

    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2019-04-01')
    @ResourceGroupPreparer(location='eastus', name_prefix='cli_storage_account')
    @StorageAccountPreparer(name_prefix='tls')
    def test_storage_update_with_min_tls(self, storage_account, resource_group):
        self.cmd('az storage account show -n {} -g {}'.format(storage_account, resource_group),
                 checks=[JMESPathCheck('minimumTlsVersion', None)])

        self.cmd('az storage account update -n {} -g {} --min-tls-version TLS1_0'.format(
            storage_account, resource_group), checks=[JMESPathCheck('minimumTlsVersion', 'TLS1_0')])

        self.cmd('az storage account update -n {} -g {} --min-tls-version TLS1_1'.format(
            storage_account, resource_group), checks=[JMESPathCheck('minimumTlsVersion', 'TLS1_1')])

        self.cmd('az storage account update -n {} -g {} --min-tls-version TLS1_2'.format(
            storage_account, resource_group), checks=[JMESPathCheck('minimumTlsVersion', 'TLS1_2')])

    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2019-06-01')
    @ResourceGroupPreparer(location='eastus', name_prefix='cli_storage_account_routing')
    def test_storage_account_with_routing_preference(self, resource_group):
        # Create Storage Account with Publish MicrosoftEndpoint, choose MicrosoftRouting
        name1 = self.create_random_name(prefix='clirouting', length=24)
        create_cmd1 = 'az storage account create -n {} -g {} --routing-choice MicrosoftRouting --publish-microsoft-endpoint true'.format(
            name1, resource_group)
        self.cmd(create_cmd1, checks=[
            JMESPathCheck('routingPreference.publishInternetEndpoints', None),
            JMESPathCheck('routingPreference.publishMicrosoftEndpoints', True),
            JMESPathCheck('routingPreference.routingChoice', 'MicrosoftRouting'),
        ])

        # Update Storage Account with Publish InternetEndpoint
        update_cmd1 = 'az storage account update -n {} -g {} --routing-choice InternetRouting --publish-microsoft-endpoint false --publish-internet-endpoint true'.format(
            name1, resource_group)
        self.cmd(update_cmd1, checks=[
            JMESPathCheck('routingPreference.publishInternetEndpoints', True),
            JMESPathCheck('routingPreference.publishMicrosoftEndpoints', False),
            JMESPathCheck('routingPreference.routingChoice', 'InternetRouting'),
        ])

        # Create Storage Account with Publish InternetEndpoint, choose InternetRouting
        name2 = self.create_random_name(prefix='clirouting', length=24)
        create_cmd2 = 'az storage account create -n {} -g {} --routing-choice InternetRouting --publish-internet-endpoints true --publish-microsoft-endpoints false'.format(
            name2, resource_group)
        self.cmd(create_cmd2, checks=[
            JMESPathCheck('routingPreference.publishInternetEndpoints', True),
            JMESPathCheck('routingPreference.publishMicrosoftEndpoints', False),
            JMESPathCheck('routingPreference.routingChoice', 'InternetRouting'),
        ])

        # Update Storage Account with MicrosoftRouting routing choice
        update_cmd2 = 'az storage account update -n {} -g {} --routing-choice MicrosoftRouting'\
            .format(name2, resource_group)

        self.cmd(update_cmd2, checks=[
            JMESPathCheck('routingPreference.routingChoice', 'MicrosoftRouting'),
        ])

        # Create without any routing preference
        name3 = self.create_random_name(prefix='clirouting', length=24)
        create_cmd3 = 'az storage account create -n {} -g {}'.format(
            name3, resource_group)
        self.cmd(create_cmd3, checks=[
            JMESPathCheck('routingPreference', None),
        ])

        # Update Storage Account with Publish MicrosoftEndpoint, choose MicrosoftRouting
        update_cmd3 = 'az storage account update -n {} -g {} --routing-choice MicrosoftRouting --publish-internet-endpoints false --publish-microsoft-endpoints true'\
            .format(name3, resource_group)

        self.cmd(update_cmd3, checks=[
            JMESPathCheck('routingPreference.publishInternetEndpoints', False),
            JMESPathCheck('routingPreference.publishMicrosoftEndpoints', True),
            JMESPathCheck('routingPreference.routingChoice', 'MicrosoftRouting'),
        ])


@api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2016-12-01')
class StorageAccountNetworkRuleTests(StorageScenarioMixin, ScenarioTest):
    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2017-06-01')
    @ResourceGroupPreparer(name_prefix='cli_test_storage_service_endpoints')
    @StorageAccountPreparer()
    def test_storage_account_network_rules(self, resource_group):
        kwargs = {
            'rg': resource_group,
            'acc': self.create_random_name(prefix='cli', length=24),
            'vnet': 'vnet1',
            'subnet': 'subnet1'
        }
        self.cmd('storage account create -g {rg} -n {acc} --bypass Metrics --default-action Deny --https-only'.format(**kwargs),
                 checks=[
                     JMESPathCheck('networkRuleSet.bypass', 'Metrics'),
                     JMESPathCheck('networkRuleSet.defaultAction', 'Deny')])
        self.cmd('storage account update -g {rg} -n {acc} --bypass Logging --default-action Allow'.format(**kwargs),
                 checks=[
                     JMESPathCheck('networkRuleSet.bypass', 'Logging'),
                     JMESPathCheck('networkRuleSet.defaultAction', 'Allow')])
        self.cmd('storage account update -g {rg} -n {acc} --set networkRuleSet.default_action=deny'.format(**kwargs),
                 checks=[
                     JMESPathCheck('networkRuleSet.bypass', 'Logging'),
                     JMESPathCheck('networkRuleSet.defaultAction', 'Deny')])

        self.cmd('network vnet create -g {rg} -n {vnet} --subnet-name {subnet}'.format(**kwargs))
        self.cmd(
            'network vnet subnet update -g {rg} --vnet-name {vnet} -n {subnet} --service-endpoints Microsoft.Storage'.format(
                **kwargs))

        self.cmd('storage account network-rule add -g {rg} --account-name {acc} --ip-address 25.1.2.3'.format(**kwargs))
        # test network-rule add idempotent
        self.cmd('storage account network-rule add -g {rg} --account-name {acc} --ip-address 25.1.2.3'.format(**kwargs))
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {acc} --ip-address 25.2.0.0/24'.format(**kwargs))
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {acc} --vnet-name {vnet} --subnet {subnet}'.format(
                **kwargs))
        self.cmd('storage account network-rule list -g {rg} --account-name {acc}'.format(**kwargs), checks=[
            JMESPathCheck('length(ipRules)', 2),
            JMESPathCheck('length(virtualNetworkRules)', 1)
        ])
        # test network-rule add idempotent
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {acc} --vnet-name {vnet} --subnet {subnet}'.format(
                **kwargs))
        self.cmd('storage account network-rule list -g {rg} --account-name {acc}'.format(**kwargs), checks=[
            JMESPathCheck('length(ipRules)', 2),
            JMESPathCheck('length(virtualNetworkRules)', 1)
        ])
        self.cmd(
            'storage account network-rule remove -g {rg} --account-name {acc} --ip-address 25.1.2.3'.format(**kwargs))
        self.cmd(
            'storage account network-rule remove -g {rg} --account-name {acc} --vnet-name {vnet} --subnet {subnet}'.format(
                **kwargs))
        self.cmd('storage account network-rule list -g {rg} --account-name {acc}'.format(**kwargs), checks=[
            JMESPathCheck('length(ipRules)', 1),
            JMESPathCheck('length(virtualNetworkRules)', 0)
        ])

    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2020-08-01-preview')
    @ResourceGroupPreparer(name_prefix='cli_test_storage_service_endpoints')
    @StorageAccountPreparer()
    def test_storage_account_resource_access_rules(self, resource_group, storage_account):
        self.kwargs = {
            'rg': resource_group,
            'sa': storage_account,
            'rid1': "/subscriptions/a7e99807-abbf-4642-bdec-2c809a96a8bc/resourceGroups/res9407/providers/Microsoft.Synapse/workspaces/testworkspace1",
            'rid2': "/subscriptions/a7e99807-abbf-4642-bdec-2c809a96a8bc/resourceGroups/res9407/providers/Microsoft.Synapse/workspaces/testworkspace2",
            'rid3': "/subscriptions/a7e99807-abbf-4642-bdec-2c809a96a8bc/resourceGroups/res9407/providers/Microsoft.Synapse/workspaces/testworkspace3",
            'tid1': "72f988bf-86f1-41af-91ab-2d7cd011db47",
            'tid2': "72f988bf-86f1-41af-91ab-2d7cd011db47"
        }

        self.cmd(
            'storage account network-rule add -g {rg} --account-name {sa} --resource-id {rid1} --tenant-id {tid1}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 1)
        ])

        # test network-rule add idempotent
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {sa} --resource-id {rid1} --tenant-id {tid1}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 1)
        ])

        # test network-rule add more
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {sa} --resource-id {rid2} --tenant-id {tid1}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 2)
        ])

        self.cmd(
            'storage account network-rule add -g {rg} --account-name {sa} --resource-id {rid3} --tenant-id {tid2}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 3)
        ])

        # remove network-rule
        self.cmd(
            'storage account network-rule remove -g {rg} --account-name {sa} --resource-id {rid1} --tenant-id {tid1}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 2)
        ])
        self.cmd(
            'storage account network-rule remove -g {rg} --account-name {sa} --resource-id {rid2} --tenant-id {tid2}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 1)
        ])


class StorageAccountBlobInventoryScenarioTest(StorageScenarioMixin, ScenarioTest):
    @AllowLargeResponse()
    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2020-08-01-preview')
    @ResourceGroupPreparer(name_prefix='cli_test_blob_inventory', location='eastus2')
    @StorageAccountPreparer(location='eastus2euap', kind='StorageV2')
    def test_storage_account_blob_inventory_policy(self, resource_group, storage_account):
        import os
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        policy_file = os.path.join(curr_dir, 'blob_inventory_policy.json').replace('\\', '\\\\')
        policy_file_no_type = os.path.join(curr_dir, 'blob_inventory_policy_no_type.json').replace('\\', '\\\\')
        self.kwargs = {'rg': resource_group,
                       'sa': storage_account,
                       'policy': policy_file,
                       'policy_no_type': policy_file_no_type}
        account_info = self.get_account_info(resource_group, storage_account)
        self.storage_cmd('storage container create -n mycontainer', account_info)

        # Create policy without type specified
        self.cmd('storage account blob-inventory-policy create --account-name {sa} -g {rg} --policy @"{policy_no_type}"',
                 checks=[JMESPathCheck("name", "DefaultInventoryPolicy"),
                         JMESPathCheck("policy.destination", "mycontainer"),
                         JMESPathCheck("policy.enabled", True),
                         JMESPathCheck("policy.rules[0].definition.filters.blobTypes[0]", "blockBlob"),
                         JMESPathCheck("policy.rules[0].definition.filters.includeBlobVersions", None),
                         JMESPathCheck("policy.rules[0].definition.filters.includeSnapshots", None),
                         JMESPathCheck("policy.rules[0].definition.filters.prefixMatch", None),
                         JMESPathCheck("policy.rules[0].enabled", True),
                         JMESPathCheck("policy.rules[0].name", "inventoryPolicyRule1"),
                         JMESPathCheck("policy.type", "Inventory"),
                         JMESPathCheck("resourceGroup", resource_group),
                         JMESPathCheck("systemData", None)])

        self.cmd('storage account blob-inventory-policy show --account-name {sa} -g {rg}',
                 checks=[JMESPathCheck("name", "DefaultInventoryPolicy"),
                         JMESPathCheck("policy.destination", "mycontainer"),
                         JMESPathCheck("policy.enabled", True),
                         JMESPathCheck("policy.rules[0].definition.filters.blobTypes[0]", "blockBlob"),
                         JMESPathCheck("policy.rules[0].definition.filters.includeBlobVersions", None),
                         JMESPathCheck("policy.rules[0].definition.filters.includeSnapshots", None),
                         JMESPathCheck("policy.rules[0].definition.filters.prefixMatch", None),
                         JMESPathCheck("policy.rules[0].enabled", True),
                         JMESPathCheck("policy.rules[0].name", "inventoryPolicyRule1"),
                         JMESPathCheck("policy.type", "Inventory"),
                         JMESPathCheck("resourceGroup", resource_group),
                         JMESPathCheck("systemData", None)])

        # Enable Versioning for Storage Account when includeBlobInventory=true in policy
        self.cmd('storage account blob-service-properties update -n {sa} -g {rg} --enable-versioning', checks=[
                 JMESPathCheck('isVersioningEnabled', True)])

        self.cmd('storage account blob-inventory-policy create --account-name {sa} -g {rg} --policy @"{policy}"',
                 checks=[JMESPathCheck("name", "DefaultInventoryPolicy"),
                         JMESPathCheck("policy.destination", "mycontainer"),
                         JMESPathCheck("policy.enabled", True),
                         JMESPathCheck("policy.rules[0].definition.filters.blobTypes[0]", "blockBlob"),
                         JMESPathCheck("policy.rules[0].definition.filters.includeBlobVersions", True),
                         JMESPathCheck("policy.rules[0].definition.filters.includeSnapshots", True),
                         JMESPathCheck("policy.rules[0].definition.filters.prefixMatch[0]", "inventoryprefix1"),
                         JMESPathCheck("policy.rules[0].definition.filters.prefixMatch[1]", "inventoryprefix2"),
                         JMESPathCheck("policy.rules[0].enabled", True),
                         JMESPathCheck("policy.rules[0].name", "inventoryPolicyRule1"),
                         JMESPathCheck("policy.type", "Inventory"),
                         JMESPathCheck("resourceGroup", resource_group),
                         JMESPathCheck("systemData", None)])

        self.cmd('storage account blob-inventory-policy show --account-name {sa} -g {rg}',
                 checks=[JMESPathCheck("name", "DefaultInventoryPolicy"),
                         JMESPathCheck("policy.destination", "mycontainer"),
                         JMESPathCheck("policy.enabled", True),
                         JMESPathCheck("policy.rules[0].definition.filters.blobTypes[0]", "blockBlob"),
                         JMESPathCheck("policy.rules[0].definition.filters.includeBlobVersions", True),
                         JMESPathCheck("policy.rules[0].definition.filters.includeSnapshots", True),
                         JMESPathCheck("policy.rules[0].definition.filters.prefixMatch[0]", "inventoryprefix1"),
                         JMESPathCheck("policy.rules[0].definition.filters.prefixMatch[1]", "inventoryprefix2"),
                         JMESPathCheck("policy.rules[0].enabled", True),
                         JMESPathCheck("policy.rules[0].name", "inventoryPolicyRule1"),
                         JMESPathCheck("policy.type", "Inventory"),
                         JMESPathCheck("resourceGroup", resource_group),
                         JMESPathCheck("systemData", None)])

        self.cmd('storage account blob-inventory-policy update --account-name {sa} -g {rg}'
                 ' --set "policy.rules[0].name=newname"')
        self.cmd('storage account blob-inventory-policy show --account-name {sa} -g {rg}',
                 checks=JMESPathCheck('policy.rules[0].name', 'newname'))

        self.cmd('storage account blob-inventory-policy delete --account-name {sa} -g {rg} -y')
        self.cmd('storage account blob-inventory-policy show --account-name {sa} -g {rg}', expect_failure=True)

