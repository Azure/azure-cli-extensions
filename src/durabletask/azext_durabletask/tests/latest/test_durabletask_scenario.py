# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
from unittest.mock import patch

from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest, live_only
from azure.core.exceptions import HttpResponseError

from azext_durabletask._scheduler import _get_caller_object_id

from .recording_processors import IdentityRecordingProcessor


def _patch_playback(test):
    for patcher in (
        patch('azext_durabletask._scheduler._get_caller_object_id',
              return_value='00000000-0000-0000-0000-000000000000'),
        patch('azure.cli.core.aaz._poller.AAZBasePolling._delay', return_value=None),
    ):
        patcher.start()
        test.addCleanup(patcher.stop)


class DurabletaskLifecycleScenario(ScenarioTest):
    def __init__(self, method_name):
        super().__init__(
            method_name, recording_processors=[IdentityRecordingProcessor()],
            replay_processors=[IdentityRecordingProcessor()], replay_patches=[_patch_playback])

    @ResourceGroupPreparer(name_prefix='clitest-durabletask-', random_name_length=40, location='northcentralus')
    def test_durabletask_scheduler_lifecycle_recorded(self):
        self.kwargs.update(
            scheduler=self.create_random_name('dts', 24),
            hub=self.create_random_name('hub', 24),
            identity=self.create_random_name('identity', 24),
            location='northcentralus')
        self.cmd(
            'durabletask scheduler create -g {rg} -n {scheduler} -l {location} '
            '--sku-name Consumption --tags purpose=recording',
            checks=[
                self.check('name', '{scheduler}'),
                self.check('location', '{location}'),
                self.check('properties.sku.name', 'Consumption'),
                self.check('properties.provisioningState', 'Succeeded'),
            ])
        self.cmd('durabletask scheduler show -g {rg} -n {scheduler}', checks=[
            self.check('name', '{scheduler}'), self.exists('properties.endpoint'),
        ])
        self.cmd('durabletask scheduler list -g {rg}', checks=[
            self.check("length([?name=='{scheduler}'])", 1),
        ])
        self.cmd(
            'durabletask scheduler update -g {rg} -n {scheduler} --tags purpose=updated '
            '--public-network-access Enabled --ip-allowlist 10.0.0.0/24', checks=[
                self.check('tags.purpose', 'updated'),
                self.check('properties.publicNetworkAccess', 'Enabled'),
                self.check('properties.ipAllowlist', ['10.0.0.0/24']),
            ])

        identity = self.cmd('identity create -g {rg} -n {identity} -l {location}').get_output_in_json()
        self.kwargs['identity_id'] = identity['id']
        self.cmd(
            'durabletask scheduler identity assign -g {rg} -n {scheduler} --user-assigned {identity_id}',
            checks=[
                self.check('type', 'UserAssigned'),
                self.check('length(userAssignedIdentities)', 1),
            ])
        self.cmd('durabletask scheduler identity show -g {rg} -n {scheduler}', checks=[
            self.check('type', 'UserAssigned'),
            self.check('length(userAssignedIdentities)', 1),
        ])
        self.cmd(
            'durabletask scheduler identity remove -g {rg} -n {scheduler} --user-assigned {identity_id}',
            checks=[self.check('type', 'None')])

        self.cmd('durabletask taskhub create -g {rg} -s {scheduler} -n {hub}', checks=[
            self.check('name', '{hub}'),
            self.check('properties.provisioningState', 'Succeeded'),
        ])
        self.cmd('durabletask taskhub show -g {rg} -s {scheduler} -n {hub}', checks=[
            self.check('name', '{hub}'),
        ])
        self.cmd('durabletask taskhub list -g {rg} -s {scheduler}', checks=[
            self.check("length([?name=='{hub}'])", 1),
        ])
        self.cmd(
            'durabletask retention-policy create -g {rg} -s {scheduler} --default-days 30 '
            '--canceled-days 1 --completed-days 2 --failed-days 3 --terminated-days 4', checks=[
                self.check('length(properties.retentionPolicies)', 5),
                self.check('properties.retentionPolicies[?orchestrationState==`Failed`].retentionPeriodInDays', [3]),
            ])
        self.cmd('durabletask retention-policy show -g {rg} -s {scheduler}', checks=[
            self.check('length(properties.retentionPolicies)', 5),
        ])
        self.cmd('durabletask retention-policy delete -g {rg} -s {scheduler} --yes')
        self.cmd('durabletask taskhub delete -g {rg} -s {scheduler} -n {hub} --yes')
        self.cmd('durabletask taskhub list -g {rg} -s {scheduler}', checks=[self.is_empty()])
        self.cmd('durabletask scheduler delete -g {rg} -n {scheduler} --yes')
        self.cmd('durabletask scheduler list -g {rg}', checks=[self.is_empty()])

    @ResourceGroupPreparer(name_prefix='clitest-durabletask-', random_name_length=40, location='northcentralus')
    def test_durabletask_taskhub_lifecycle_recorded(self):
        self.kwargs.update(
            scheduler=self.create_random_name('dts', 24),
            hub=self.create_random_name('hub', 24), location='northcentralus')
        self.cmd(
            'durabletask scheduler create -g {rg} -n {scheduler} -l {location} --sku-name Consumption')
        self.cmd('durabletask taskhub create -g {rg} -s {scheduler} -n {hub} --capabilities []', checks=[
            self.check('name', '{hub}'),
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('properties.capabilities', []),
        ])
        self.cmd('durabletask taskhub show -g {rg} -s {scheduler} -n {hub}', checks=[
            self.check('name', '{hub}'),
            self.check('properties.capabilities', []),
            self.exists('properties.dashboardUrl'),
        ])
        self.cmd('durabletask taskhub list -g {rg} -s {scheduler}', checks=[
            self.check("length([?name=='{hub}'])", 1),
        ])
        self.cmd('durabletask taskhub create -g {rg} -s {scheduler} -n {hub} --capabilities []', checks=[
            self.check('name', '{hub}'),
            self.check('properties.provisioningState', 'Succeeded'),
        ])
        self.cmd('durabletask taskhub delete -g {rg} -s {scheduler} -n {hub} --yes')
        self.cmd('durabletask taskhub list -g {rg} -s {scheduler}', checks=[self.is_empty()])
        with self.assertRaises(HttpResponseError) as deleted:
            self.cmd('durabletask taskhub show -g {rg} -s {scheduler} -n {hub}')
        self.assertEqual(deleted.exception.status_code, 404)
        self.cmd('durabletask scheduler delete -g {rg} -n {scheduler} --yes')

    @ResourceGroupPreparer(name_prefix='clitest-durabletask-', random_name_length=40, location='northcentralus')
    def test_durabletask_retention_policy_lifecycle_recorded(self):
        self.kwargs.update(scheduler=self.create_random_name('dts', 24), location='northcentralus')
        self.cmd(
            'durabletask scheduler create -g {rg} -n {scheduler} -l {location} --sku-name Consumption')
        self.cmd(
            'durabletask retention-policy create -g {rg} -s {scheduler} --default-days 30 '
            '--canceled-days 1 --completed-days 2 --failed-days 3 --terminated-days 4', checks=[
                self.check('length(properties.retentionPolicies)', 5),
                self.check('properties.retentionPolicies[?orchestrationState==`null`].retentionPeriodInDays', [30]),
                self.check('properties.retentionPolicies[?orchestrationState==`Canceled`].retentionPeriodInDays', [1]),
                self.check('properties.retentionPolicies[?orchestrationState==`Completed`].retentionPeriodInDays', [2]),
                self.check('properties.retentionPolicies[?orchestrationState==`Failed`].retentionPeriodInDays', [3]),
                self.check('properties.retentionPolicies[?orchestrationState==`Terminated`].retentionPeriodInDays', [4]),
            ])
        self.cmd('durabletask retention-policy show -g {rg} -s {scheduler}', checks=[
            self.check('length(properties.retentionPolicies)', 5),
        ])
        self.cmd(
            'durabletask retention-policy create -g {rg} -s {scheduler} --default-days 7 --failed-days 14',
            checks=[self.check('length(properties.retentionPolicies)', 2)])
        self.cmd('durabletask retention-policy show -g {rg} -s {scheduler}', checks=[
            self.check('length(properties.retentionPolicies)', 2),
            self.check('properties.retentionPolicies[?orchestrationState==`null`].retentionPeriodInDays', [7]),
            self.check('properties.retentionPolicies[?orchestrationState==`Failed`].retentionPeriodInDays', [14]),
        ])
        self.cmd('durabletask retention-policy delete -g {rg} -s {scheduler} --yes')
        with self.assertRaises(HttpResponseError) as deleted:
            self.cmd('durabletask retention-policy show -g {rg} -s {scheduler}')
        self.assertEqual(deleted.exception.status_code, 404)
        self.cmd('durabletask scheduler delete -g {rg} -n {scheduler} --yes')

    @ResourceGroupPreparer(name_prefix='clitest-durabletask-', random_name_length=40, location='northcentralus')
    def test_durabletask_identity_lifecycle_recorded(self):
        self.kwargs.update(
            scheduler=self.create_random_name('dts', 24),
            identity=self.create_random_name('identity', 24),
            other_identity=self.create_random_name('identity', 24),
            location='northcentralus')
        self.cmd(
            'durabletask scheduler create -g {rg} -n {scheduler} -l {location} --sku-name Consumption')
        first = self.cmd('identity create -g {rg} -n {identity} -l {location}').get_output_in_json()
        second = self.cmd('identity create -g {rg} -n {other_identity} -l {location}').get_output_in_json()
        self.kwargs.update(identity_id=first['id'], other_identity_id=second['id'])
        self.cmd(
            'durabletask scheduler identity assign -g {rg} -n {scheduler} --user-assigned {identity_id}',
            checks=[self.check('type', 'UserAssigned'), self.check('length(userAssignedIdentities)', 1)])
        self.cmd(
            'durabletask scheduler identity assign -g {rg} -n {scheduler} --user-assigned {other_identity_id}',
            checks=[self.check('type', 'UserAssigned'), self.check('length(userAssignedIdentities)', 2)])
        assigned = self.cmd('durabletask scheduler identity show -g {rg} -n {scheduler}').get_output_in_json()
        self.assertEqual(
            {resource_id.lower() for resource_id in assigned['userAssignedIdentities']},
            {first['id'].lower(), second['id'].lower()})
        self.cmd(
            'durabletask scheduler identity remove -g {rg} -n {scheduler} --mi-user-assigned {identity_id}',
            checks=[self.check('type', 'UserAssigned'), self.check('length(userAssignedIdentities)', 1)])
        remaining = self.cmd('durabletask scheduler identity show -g {rg} -n {scheduler}').get_output_in_json()
        self.assertEqual(
            {resource_id.lower() for resource_id in remaining['userAssignedIdentities']},
            {second['id'].lower()})
        self.cmd(
            'durabletask scheduler identity remove -g {rg} -n {scheduler} --user-assigned {other_identity_id}',
            checks=[self.check('type', 'None')])
        self.cmd('durabletask scheduler identity show -g {rg} -n {scheduler}', checks=[
            self.check('type', 'None'),
        ])
        self.cmd('identity show -g {rg} -n {identity}', checks=[self.check('id', '{identity_id}')])
        self.cmd('identity show -g {rg} -n {other_identity}', checks=[self.check('id', '{other_identity_id}')])
        self.cmd('identity delete -g {rg} -n {identity}')
        self.cmd('identity delete -g {rg} -n {other_identity}')
        self.cmd('durabletask scheduler delete -g {rg} -n {scheduler} --yes')

    @ResourceGroupPreparer(name_prefix='clitest-durabletask-', random_name_length=40, location='northcentralus')
    def test_durabletask_taskqueue_lifecycle_recorded(self):
        self.kwargs.update(
            scheduler=self.create_random_name('dts', 24),
            hub=self.create_random_name('hub', 24),
            queue=self.create_random_name('queue', 24),
            location='northcentralus')
        self.cmd(
            'durabletask scheduler create -g {rg} -n {scheduler} -l {location} '
            '--sku-name Dedicated --sku-capacity 1',
            checks=[self.check('properties.provisioningState', 'Succeeded')])
        self.cmd('durabletask taskhub create -g {rg} -s {scheduler} -n {hub}')
        self.cmd(
            'durabletask taskqueue create -g {rg} -s {scheduler} -t {hub} -n {queue} '
            '--actions-per-second 100', checks=[
                self.check('name', '{queue}'),
                self.check('properties.throughput.actionsPerSecond', 100),
                self.check('properties.provisioningState', 'Succeeded'),
            ])
        self.cmd('durabletask taskqueue show -g {rg} -s {scheduler} -t {hub} -n {queue}', checks=[
            self.check('name', '{queue}'),
            self.check('properties.throughput.actionsPerSecond', 100),
        ])
        self.cmd('durabletask taskqueue list -g {rg} -s {scheduler} -t {hub}', checks=[
            self.check("length([?name=='{queue}'])", 1),
        ])
        self.cmd(
            'durabletask taskqueue update -g {rg} -s {scheduler} -t {hub} -n {queue} '
            '--actions-per-second 200', checks=[self.check('properties.throughput.actionsPerSecond', 200)])
        self.cmd('durabletask taskqueue show -g {rg} -s {scheduler} -t {hub} -n {queue}', checks=[
            self.check('properties.throughput.actionsPerSecond', 200),
        ])
        self.cmd('durabletask scheduler restart -g {rg} -n {scheduler}', checks=[
            self.check('schedulerName', '{scheduler}'),
            self.check('resourceGroupName', '{rg}'),
            self.check('status', 'Restart initiated'),
        ])
        self.cmd('durabletask taskqueue delete -g {rg} -s {scheduler} -t {hub} -n {queue} --yes')
        self.cmd('durabletask taskqueue list -g {rg} -s {scheduler} -t {hub}', checks=[self.is_empty()])
        self.cmd('durabletask taskhub delete -g {rg} -s {scheduler} -n {hub} --yes')
        self.cmd('durabletask scheduler delete -g {rg} -n {scheduler} --yes')

    @ResourceGroupPreparer(name_prefix='clitest-durabletask-', random_name_length=40, location='northcentralus')
    def test_durabletask_encryption_lifecycle_recorded(self):
        self.kwargs.update(
            scheduler=self.create_random_name('dts', 24),
            vault=self.create_random_name('dtsvault', 24),
            key=self.create_random_name('key', 24),
            admin_assignment=str(self.create_guid()),
            encryption_assignment=str(self.create_guid()),
            location='northcentralus')
        self.cmd(
            'durabletask scheduler create -g {rg} -n {scheduler} -l {location} '
            '--sku-name Dedicated --sku-capacity 1')
        service_principal = self.cmd(
            'rest --method get --url "https://graph.microsoft.com/v1.0/'
            'servicePrincipals(appId=\'887c6b43-ba92-4adb-a82b-73670fc48dac\')?$select=id"'
        ).get_output_in_json()
        self.kwargs['principal_id'] = service_principal['id']
        vault = self.cmd(
            'keyvault create -g {rg} -n {vault} -l {location} --enable-rbac-authorization true '
            '--enable-purge-protection true --retention-days 7').get_output_in_json()
        self.kwargs['vault_id'] = vault['id']
        self.kwargs['caller_id'] = (
            _get_caller_object_id(self.cli_ctx) if self.in_recording else '00000000-0000-0000-0000-000000000000')
        self.assertIsNotNone(self.kwargs['caller_id'], 'The recording account must have an Entra object ID')
        self.cmd(
            'role assignment create --name {admin_assignment} --assignee-object-id {caller_id} '
            '--assignee-principal-type User --role "Key Vault Administrator" --scope {vault_id}')
        self.cmd(
            'role assignment create --name {encryption_assignment} --assignee-object-id {principal_id} '
            '--assignee-principal-type ServicePrincipal --role "Key Vault Crypto Service Encryption User" '
            '--scope {vault_id}')
        # Allow Key Vault data-plane RBAC to observe the new role assignments; playback skips sleep.
        time.sleep(60)
        key = self.cmd(
            'keyvault key create --vault-name {vault} -n {key} --kty RSA --size 2048').get_output_in_json()
        self.kwargs['key_uri'] = key['key']['kid']
        self.cmd(
            'durabletask scheduler transparent-data-encryption create -g {rg} '
            '--scheduler-name {scheduler} --key-source CustomerManaged --key-vault-key-uri {key_uri} '
            '--auto-rotation-enabled false',
            checks=[
                self.check('properties.keySource', 'CustomerManaged'),
                self.check('properties.provisioningState', 'Succeeded'),
            ])
        self.cmd(
            'durabletask scheduler transparent-data-encryption show -g {rg} --scheduler-name {scheduler}',
            checks=[self.check('properties.keySource', 'CustomerManaged')])
        self.cmd(
            'durabletask scheduler transparent-data-encryption update -g {rg} '
            '--scheduler-name {scheduler} --auto-rotation-enabled true',
            checks=[self.check('properties.autoRotationEnabled', True)])
        self.cmd(
            'durabletask scheduler transparent-data-encryption update -g {rg} '
            '--scheduler-name {scheduler} --auto-rotation-enabled false',
            checks=[self.check('properties.autoRotationEnabled', False)])
        self.cmd(
            'durabletask scheduler transparent-data-encryption delete -g {rg} '
            '--scheduler-name {scheduler} --yes')
        self.cmd('durabletask scheduler delete -g {rg} -n {scheduler} --yes')

    @live_only()
    @ResourceGroupPreparer(name_prefix='clitest-durabletask-', random_name_length=40, location='northcentralus')
    def test_durabletask_failover_lifecycle_live(self):
        """Exercise cross-region failover when the service can provision the configuration."""
        self.kwargs.update(
            scheduler=self.create_random_name('dts', 24),
            partner=self.create_random_name('partner', 24),
            hub=self.create_random_name('hub', 24),
            location='northcentralus', partner_location='westus2')
        self.cmd(
            'durabletask scheduler create -g {rg} -n {scheduler} -l {location} '
            '--sku-name Dedicated --sku-capacity 1 --no-wait')
        self.cmd(
            'durabletask scheduler create -g {rg} -n {partner} -l {partner_location} '
            '--sku-name Dedicated --sku-capacity 1 --no-wait')
        self.cmd(
            'durabletask scheduler wait -g {rg} -n {scheduler} --created --interval 10 --timeout 900')
        self.cmd(
            'durabletask scheduler wait -g {rg} -n {partner} --created --interval 10 --timeout 900')
        partner = self.cmd(
            'durabletask scheduler show -g {rg} -n {partner}', checks=[
                self.check('location', '{partner_location}'),
                self.check('properties.provisioningState', 'Succeeded'),
            ]).get_output_in_json()
        self.kwargs['partner_id'] = partner['id']
        self.cmd('durabletask taskhub create -g {rg} -s {scheduler} -n {hub}', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
        ])
        self.cmd(
            'durabletask scheduler failover-instance create -g {rg} -s {scheduler} '
            '--partner-scheduler-resource-id {partner_id} --no-wait')

        def delete_failover():
            self.cmd('durabletask scheduler failover-instance delete -g {rg} -s {scheduler} --yes --no-wait')
            self.cmd(
                'durabletask scheduler failover-instance wait -g {rg} -s {scheduler} '
                '--deleted --interval 10 --timeout 600')

        self.addCleanup(delete_failover)
        self.cmd(
            'durabletask scheduler failover-instance wait -g {rg} -s {scheduler} '
            '--created --interval 10 --timeout 600')
        self.cmd('durabletask scheduler failover-instance show -g {rg} -s {scheduler}', checks=[
            self.check('properties.partnerSchedulerResourceId', '{partner_id}'),
        ])
        self.cmd(
            'durabletask scheduler failover-instance update -g {rg} -s {scheduler} '
            '--pid {partner_id} --no-wait')
        self.cmd(
            'durabletask scheduler failover-instance wait -g {rg} -s {scheduler} '
            '--updated --interval 10 --timeout 600')
        self.cmd('durabletask scheduler failover-instance failover -g {rg} -s {scheduler} --no-wait')
        self.cmd(
            'durabletask scheduler failover-instance wait -g {rg} -s {scheduler} '
            '--updated --interval 10 --timeout 600')
        self.cmd(
            'durabletask scheduler failover-instance force-failover-allow-data-loss '
            '-g {rg} -s {scheduler} --no-wait')
        self.cmd(
            'durabletask scheduler failover-instance wait -g {rg} -s {scheduler} '
            '--updated --interval 10 --timeout 600')
        self.cmd(
            'durabletask scheduler failover-instance show -g {rg} -s {scheduler}',
            checks=[self.check('properties.provisioningState', 'Succeeded')])

    @ResourceGroupPreparer(name_prefix='clitest-durabletask-', random_name_length=40, location='northcentralus')
    def test_durabletask_attach_functionapp_recorded(self):
        self.kwargs.update(
            scheduler=self.create_random_name('dts', 24),
            hub=self.create_random_name('hub', 24),
            function=self.create_random_name('dtsfunc', 24),
            plan=self.create_random_name('dtsplan', 24),
            location='northcentralus')
        self.cmd(
            'durabletask scheduler create -g {rg} -n {scheduler} -l {location} --sku-name Consumption')
        self.cmd('durabletask taskhub create -g {rg} -s {scheduler} -n {hub}')
        plan = self.cmd(
            'appservice plan create -g {rg} -n {plan} -l {location} --sku B1 --is-linux').get_output_in_json()
        self.kwargs['plan_id'] = plan['id']
        # Attachment only needs an ARM Function App and its identity, not a running host or storage keys.
        function = self.cmd(
            'resource create -g {rg} -n {function} --resource-type Microsoft.Web/sites '
            '--api-version 2024-04-01 --is-full-object --properties '
            '\'{{"location":"{location}","kind":"functionapp,linux",'
            '"identity":{{"type":"SystemAssigned"}},'
            '"properties":{{"serverFarmId":"{plan_id}","reserved":true}}}}\'').get_output_in_json()
        self.kwargs['target'] = function['id']
        self.cmd(
            'durabletask scheduler attach -g {rg} -n {scheduler} --task-hub-name {hub} '
            '--target {target} --role-type worker', checks=[
                self.check('schedulerName', '{scheduler}'),
                self.check('taskHubName', '{hub}'),
                self.check('targetResourceId', '{target}'),
                self.check('targetType', 'functionapp'),
                self.check('roleAssigned', 'Durable Task Worker'),
            ])
        self.cmd('functionapp config appsettings list -g {rg} -n {function}', checks=[
            self.check("[?name=='TASKHUB_NAME'].value | [0]", '{hub}'),
            self.check("length([?name=='DURABLE_TASK_SCHEDULER_CONNECTION_STRING'])", 1),
        ])
        self.cmd('durabletask taskhub delete -g {rg} -s {scheduler} -n {hub} --yes')
        self.cmd('durabletask scheduler delete -g {rg} -n {scheduler} --yes')
