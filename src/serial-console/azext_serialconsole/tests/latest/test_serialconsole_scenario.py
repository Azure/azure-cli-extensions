# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import json
import time
import requests
import websocket
import pytest
from azext_serialconsole.custom import check_resource
from azure.cli.testsdk.base import ScenarioTest
from azure.cli.testsdk import (
    LiveScenarioTest, StorageAccountPreparer, ResourceGroupPreparer)
from azure.cli.testsdk.exceptions import JMESPathCheckAssertionError
from azure.cli.core.azclierror import ForbiddenError, ResourceNotFoundError
from azure.cli.core.azclierror import AzureConnectionError
from azure.cli.core.azclierror import ForbiddenError
from azure.core.exceptions import ResourceNotFoundError as ComputeClientResourceNotFoundError
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

class CheckResourceTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_serialconsole', location='westus2')
    @StorageAccountPreparer(name_prefix='cli', location="westus2")
    def test_check_resource_VMSS(self, resource_group, storage_account):
        name = self.create_random_name(prefix='cli', length=24)
        self.kwargs.update({
            'sa': storage_account,
            'rg': resource_group,
            'name': name,
            'urn': 'UbuntuLTS',
            'loc': 'westus2'
        })

        with self.assertRaises(ComputeClientResourceNotFoundError):
            check_resource(self.cli_ctx, resource_group, name, None)
        with self.assertRaises(ComputeClientResourceNotFoundError):
            check_resource(self.cli_ctx, resource_group, name, "0")

        self.cmd('az vmss create -g {rg} -n {name} --image {urn} --instance-count 2 -l {loc}')

        with self.assertRaises(ResourceNotFoundError):
            check_resource(self.cli_ctx, resource_group, name, None)

        iid = self.cmd('vmss list-instances --resource-group {rg} --name {name} --query "[].instanceId"').get_output_in_json()[1]
        self.kwargs.update({'id': iid})
        self.cmd('az vmss update --name {name} --resource-group {rg} --set virtualMachineProfile.diagnosticsProfile="{{\\"bootDiagnostics\\": {{\\"Enabled\\" : \\"True\\",\\"StorageUri\\" : null}}}}"')
        self.cmd('az vmss update-instances -g {rg} -n {name} --instance-ids {id}')

        check_resource(self.cli_ctx, resource_group, name, iid)

        self.cmd('az vmss deallocate -g {rg} -n {name} --instance-ids {id}')

        with self.assertRaises(AzureConnectionError):
            check_resource(self.cli_ctx, resource_group, name, iid)

        self.cmd('az vmss start -g {rg} -n {name} --instance-ids {id}')
        self.cmd('az vmss stop -g {rg} -n {name} --instance-ids {id}')

        check_resource(self.cli_ctx, resource_group, name, iid)

        self.cmd('az vmss start -g {rg} -n {name} --instance-ids {id}')
        self.cmd('az vmss update --name {name} --resource-group {rg} --set virtualMachineProfile.diagnosticsProfile="{{\\"bootDiagnostics\\": {{\\"Enabled\\" : \\"True\\",\\"StorageUri\\":\\"https://{sa}.blob.core.windows.net/\\"}}}}"')
        self.cmd('az vmss update-instances -g {rg} -n {name} --instance-ids {id}')

        check_resource(self.cli_ctx, resource_group, name, iid)

        self.cmd('az serial-console disable')

        with self.assertRaises(ForbiddenError):
            check_resource(self.cli_ctx, resource_group, name, iid)

        self.cmd('az serial-console enable')

        check_resource(self.cli_ctx, resource_group, name, iid)

        self.cmd('az vmss deallocate -g {rg} -n {name} --instance-ids {id}')

        with self.assertRaises(AzureConnectionError):
            check_resource(self.cli_ctx, resource_group, name, iid)

        self.cmd('az vmss start -g {rg} -n {name} --instance-ids {id}')
        self.cmd('az vmss stop -g {rg} -n {name} --instance-ids {id}')

        check_resource(self.cli_ctx, resource_group, name, iid)

        self.cmd('az vmss start -g {rg} -n {name} --instance-ids {id}')
        self.cmd('az vmss update --name {name} --resource-group {rg} --set virtualMachineProfile.diagnosticsProfile="{{\\"bootDiagnostics\\": {{\\"Enabled\\" : \\"False\\",\\"StorageUri\\" : null}}}}"')

        check_resource(self.cli_ctx, resource_group, name, iid)

        self.cmd('az vmss update-instances -g {rg} -n {name} --instance-ids {id}')

        with self.assertRaises(AzureConnectionError):
            check_resource(self.cli_ctx, resource_group, name, iid)

        self.cmd('az vmss deallocate -g {rg} -n {name} --instance-ids {id}')

        with self.assertRaises(AzureConnectionError):
            check_resource(self.cli_ctx, resource_group, name, iid)

        self.cmd('az vmss start -g {rg} -n {name} --instance-ids {id}')
        self.cmd('az vmss update --name {name} --resource-group {rg} --set virtualMachineProfile.diagnosticsProfile="{{\\"bootDiagnostics\\": {{\\"Enabled\\" : \\"True\\",\\"StorageUri\\" : null}}}}"')

        with self.assertRaises(AzureConnectionError):
            check_resource(self.cli_ctx, resource_group, name, iid)

        self.cmd('az vmss update-instances -g {rg} -n {name} --instance-ids {id}')

        check_resource(self.cli_ctx, resource_group, name, iid)

    @ResourceGroupPreparer(name_prefix='cli_test_serialconsole', location='westus2')
    @StorageAccountPreparer(name_prefix='cli', location="westus2")
    @AllowLargeResponse()
    def test_check_resource_VM(self, resource_group, storage_account):
        name = self.create_random_name(prefix='cli', length=24)
        self.kwargs.update({
            'sa': storage_account,
            'rg': resource_group,
            'name': name,
            'urn': 'UbuntuLTS',
            'loc': 'westus2'
        })

        with self.assertRaises(ComputeClientResourceNotFoundError):
            check_resource(self.cli_ctx, resource_group, name, None)
        with self.assertRaises(ComputeClientResourceNotFoundError):
            check_resource(self.cli_ctx, resource_group, name, "0")

        self.cmd('az vm create -g {rg} -n {name} --image {urn} -l {loc} --generate-ssh-keys')

        with self.assertRaises(AzureConnectionError):
            check_resource(self.cli_ctx, resource_group, name, None)

        self.cmd('az vm boot-diagnostics enable -g {rg} -n {name}')

        check_resource(self.cli_ctx, resource_group, name, None)

        self.cmd('az vm deallocate -g {rg} -n {name}')

        with self.assertRaises(AzureConnectionError):
            check_resource(self.cli_ctx, resource_group, name, None)

        self.cmd('az vm start -g {rg} -n {name}')
        self.cmd('az vm stop -g {rg} -n {name}')

        check_resource(self.cli_ctx, resource_group, name, None)

        self.cmd('az vm boot-diagnostics disable -g {rg} -n {name}')

        with self.assertRaises(AzureConnectionError):
            check_resource(self.cli_ctx, resource_group, name, None)

        self.cmd('az vm start -g {rg} -n {name}')

        with self.assertRaises(AzureConnectionError):
            check_resource(self.cli_ctx, resource_group, name, None)

        self.cmd('az vm boot-diagnostics enable -g {rg} -n {name} --storage {sa}')

        check_resource(self.cli_ctx, resource_group, name, None)

        self.cmd('az serial-console disable')

        with self.assertRaises(ForbiddenError):
            check_resource(self.cli_ctx, resource_group, name, None)

        self.cmd('az serial-console enable')

        check_resource(self.cli_ctx, resource_group, name, None)

        self.cmd('az vm stop -g {rg} -n {name}')

        check_resource(self.cli_ctx, resource_group, name, None)

        self.cmd('az vm deallocate -g {rg} -n {name}')

        with self.assertRaises(AzureConnectionError):
            check_resource(self.cli_ctx, resource_group, name, None)


class SerialConsoleEnableDisableTest(ScenarioTest):

    def test_enable_disable(self):
        self.cmd('az serial-console disable', checks=[
            self.check('properties.disabled', 'True')
        ])
        self.cmd('az serial-console enable', checks=[
            self.check('properties.disabled', 'False')
        ])


class SerialconsoleAdminCommandsTest(LiveScenarioTest):

    def check_result(self, resource_group_name, vm_vmss_name, vmss_instanceid=None, message=""):
        ARM_ENDPOINT = "https://management.azure.com"
        RP_PROVIDER = "Microsoft.SerialConsole"
        subscription_id = self.get_subscription_id()
        vm_path = f"virtualMachineScaleSets/{vm_vmss_name}/virtualMachines/{vmss_instanceid}" \
            if vmss_instanceid else f"virtualMachines/{vm_vmss_name}"
        connection_url = (f"{ARM_ENDPOINT}/subscriptions/{subscription_id}/resourcegroups/{resource_group_name}"
                         f"/providers/Microsoft.Compute/{vm_path}"
                         f"/providers/{RP_PROVIDER}/serialPorts/0"
                         f"/connect?api-version=2018-05-01")

        from azure.cli.core._profile import Profile
        token_info, _, _ = Profile().get_raw_token()
        access_token = token_info[1]
        application_json_format = "application/json"
        headers = {'authorization': "Bearer " + access_token,
                   'accept': application_json_format,
                   'content-type': application_json_format}
        result = requests.post(connection_url, headers=headers)
        json_results = json.loads(result.text)
        self.assertTrue(result.status_code ==
                        200 and "connectionString" in json_results)
        websocket_url = json_results["connectionString"]

        ws = websocket.WebSocket()
        ws.connect(websocket_url + "?authorization=" + access_token, timeout=30)
        buffer = ""
        while True:
            try:
                buffer += ws.recv()
            except (websocket.WebSocketTimeoutException, websocket.WebSocketConnectionClosedException):
                break

        assert message in buffer

    @ResourceGroupPreparer(name_prefix='cli_test_serialconsole', location='westus2')
    @StorageAccountPreparer(name_prefix='cli', location="westus2")
    def test_send_sysrq_VMSS(self, resource_group, storage_account):
        name = self.create_random_name(prefix='cli', length=24)
        self.kwargs.update({
            'sa': storage_account,
            'rg': resource_group,
            'name': name,
            'urn': 'UbuntuLTS',
            'loc': 'westus2'
        })
        self.cmd(
            'az vmss create -g {rg} -n {name} --image {urn} --instance-count 2 -l {loc}')
        self.cmd('az vmss update --name {name} --resource-group {rg} --set virtualMachineProfile.diagnosticsProfile="{{\\"bootDiagnostics\\": {{\\"Enabled\\" : \\"True\\",\\"StorageUri\\":\\"https://{sa}.blob.core.windows.net/\\"}}}}"')
        result = self.cmd(
            'vmss list-instances --resource-group {rg} --name {name} --query "[].instanceId"').get_output_in_json()
        self.kwargs.update({'id': result[1]})
        self.cmd(
            'az vmss update-instances -g {rg} -n {name} --instance-ids {id}')
        time.sleep(60)
        for i in range(5):
            try:
                self.cmd('vmss get-instance-view --resource-group {rg} --name {name} --instance-id {id}', checks=[
                    self.check('statuses[0].code',
                               'ProvisioningState/succeeded'),
                    self.check('statuses[1].code', 'PowerState/running'),
                ])
                break
            except JMESPathCheckAssertionError:
                time.sleep(30)
        self.cmd(
            'serial-console send sysrq -g {rg} -n {name} --instance-id {id} --input h')
        self.check_result(resource_group, name,
                          vmss_instanceid=result[1], message="sysrq: HELP")

    @ResourceGroupPreparer(name_prefix='cli_test_serialconsole', location='westus2')
    @StorageAccountPreparer(name_prefix='cli', location="westus2")
    def test_send_nmi_VMSS(self, resource_group, storage_account):
        name = self.create_random_name(prefix='cli', length=24)
        self.kwargs.update({
            'sa': storage_account,
            'rg': resource_group,
            'name': name,
            'urn': 'UbuntuLTS',
            'loc': 'westus2'
        })
        self.cmd(
            'az vmss create -g {rg} -n {name} --image {urn} --instance-count 2 -l {loc}')
        self.cmd('az vmss update --name {name} --resource-group {rg} --set virtualMachineProfile.diagnosticsProfile="{{\\"bootDiagnostics\\": {{\\"Enabled\\" : \\"True\\",\\"StorageUri\\":\\"https://{sa}.blob.core.windows.net/\\"}}}}"')
        result = self.cmd(
            'vmss list-instances --resource-group {rg} --name {name} --query "[].instanceId"').get_output_in_json()
        self.kwargs.update({'id': result[1]})
        self.cmd(
            'az vmss update-instances -g {rg} -n {name} --instance-ids {id}')
        time.sleep(60)
        for i in range(5):
            try:
                self.cmd('vmss get-instance-view --resource-group {rg} --name {name} --instance-id {id}', checks=[
                    self.check('statuses[0].code',
                               'ProvisioningState/succeeded'),
                    self.check('statuses[1].code', 'PowerState/running'),
                ])
                break
            except JMESPathCheckAssertionError:
                time.sleep(30)
        self.cmd(
            'serial-console send nmi -g {rg} -n {name} --instance-id {id}')
        self.check_result(resource_group, name,
                          vmss_instanceid=result[1], message="NMI received")

    @ResourceGroupPreparer(name_prefix='cli_test_serialconsole', location='westus2')
    @StorageAccountPreparer(name_prefix='cli', location="westus2")
    def test_send_reset_VMSS(self, resource_group, storage_account):
        name = self.create_random_name(prefix='cli', length=24)
        self.kwargs.update({
            'sa': storage_account,
            'rg': resource_group,
            'name': name,
            'urn': 'UbuntuLTS',
            'loc': 'westus2'
        })
        self.cmd(
            'az vmss create -g {rg} -n {name} --image {urn} --instance-count 2 -l {loc}')
        self.cmd('az vmss update --name {name} --resource-group {rg} --set virtualMachineProfile.diagnosticsProfile="{{\\"bootDiagnostics\\": {{\\"Enabled\\" : \\"True\\",\\"StorageUri\\":\\"https://{sa}.blob.core.windows.net/\\"}}}}"')
        result = self.cmd(
            'vmss list-instances --resource-group {rg} --name {name} --query "[].instanceId"').get_output_in_json()
        self.kwargs.update({'id': result[1]})
        self.cmd(
            'az vmss update-instances -g {rg} -n {name} --instance-ids {id}')
        time.sleep(60)
        for i in range(5):
            try:
                self.cmd('vmss get-instance-view --resource-group {rg} --name {name} --instance-id {id}', checks=[
                    self.check('statuses[0].code',
                               'ProvisioningState/succeeded'),
                    self.check('statuses[1].code', 'PowerState/running'),
                ])
                break
            except JMESPathCheckAssertionError:
                time.sleep(30)
        self.cmd('serial-console send reset -g {rg} -n {name} --instance-id {id}')

    @ResourceGroupPreparer(name_prefix='cli_test_serialconsole', location='westus2')
    @StorageAccountPreparer(name_prefix='cli', location="westus2")
    def test_send_nmi_VM(self, resource_group, storage_account):
        name = self.create_random_name(prefix='cli', length=24)
        self.kwargs.update({
            'sa': storage_account,
            'rg': resource_group,
            'name': name,
            'urn': 'UbuntuLTS',
            'loc': 'westus2'
        })
        self.cmd(
            'az vm create -g {rg} -n {name} --image {urn} --boot-diagnostics-storage {sa} -l {loc} --generate-ssh-keys')
        time.sleep(60)
        for i in range(5):
            try:
                self.cmd('vm get-instance-view --resource-group {rg} --name {name}', checks=[
                    self.check(
                        'instanceView.statuses[0].code', 'ProvisioningState/succeeded'),
                    self.check(
                        'instanceView.statuses[1].code', 'PowerState/running'),
                ])
                break
            except JMESPathCheckAssertionError:
                time.sleep(30)
        self.cmd('serial-console send nmi -g {rg} -n {name}')
        self.check_result(resource_group, name, message="NMI received")

    @ResourceGroupPreparer(name_prefix='cli_test_serialconsole', location='westus2')
    @StorageAccountPreparer(name_prefix='cli', location="westus2")
    def test_send_sysrq_VM(self, resource_group, storage_account):
        name = self.create_random_name(prefix='cli', length=24)
        self.kwargs.update({
            'sa': storage_account,
            'rg': resource_group,
            'name': name,
            'urn': 'UbuntuLTS',
            'loc': 'westus2'
        })
        self.cmd(
            'az vm create -g {rg} -n {name} --image {urn} --boot-diagnostics-storage {sa} -l {loc} --generate-ssh-keys')
        time.sleep(60)
        for i in range(5):
            try:
                self.cmd('vm get-instance-view --resource-group {rg} --name {name}', checks=[
                    self.check(
                        'instanceView.statuses[0].code', 'ProvisioningState/succeeded'),
                    self.check(
                        'instanceView.statuses[1].code', 'PowerState/running'),
                ])
                break
            except JMESPathCheckAssertionError:
                time.sleep(30)
        self.cmd('serial-console send sysrq -g {rg} -n {name} --input h')
        self.check_result(resource_group, name, message="sysrq: HELP")

    @ResourceGroupPreparer(name_prefix='cli_test_serialconsole', location='westus2')
    @StorageAccountPreparer(name_prefix='cli', location="westus2")
    def test_send_reset_VM(self, resource_group, storage_account):
        name = self.create_random_name(prefix='cli', length=24)
        self.kwargs.update({
            'sa': storage_account,
            'rg': resource_group,
            'name': name,
            'urn': 'UbuntuLTS',
            'loc': 'westus2'
        })
        self.cmd(
            'az vm create -g {rg} -n {name} --image {urn} --boot-diagnostics-storage {sa} -l {loc} --generate-ssh-keys')
        time.sleep(60)
        for i in range(5):
            try:
                self.cmd('vm get-instance-view --resource-group {rg} --name {name}', checks=[
                    self.check(
                        'instanceView.statuses[0].code', 'ProvisioningState/succeeded'),
                    self.check(
                        'instanceView.statuses[1].code', 'PowerState/running'),
                ])
                break
            except JMESPathCheckAssertionError:
                time.sleep(30)
        self.cmd('serial-console send reset -g {rg} -n {name}')
