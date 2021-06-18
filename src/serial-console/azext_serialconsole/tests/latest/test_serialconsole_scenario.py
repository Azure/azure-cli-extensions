# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import json
import time
import requests
import websocket
from azext_serialconsole.custom import checkResource
from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (
    LiveScenarioTest, StorageAccountPreparer, ResourceGroupPreparer)
from azure.cli.testsdk.exceptions import JMESPathCheckAssertionError
from azure.cli.core.azclierror import ResourceNotFoundError


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class SerialconsoleAdminCommandsTest(LiveScenarioTest):

    def check_result(self, resource_group_name, vm_vmss_name, vmss_instanceid=None, message=""):
        armEndpoint = "https://management.azure.com"
        RP_PROVIDER = "Microsoft.SerialConsole"
        subscriptionId = self.get_subscription_id()
        vmPath = f"virtualMachineScaleSets/{vm_vmss_name}/virtualMachines/{vmss_instanceid}" \
            if vmss_instanceid else f"virtualMachines/{vm_vmss_name}"
        connectionUrl = (f"{armEndpoint}/subscriptions/{subscriptionId}/resourcegroups/{resource_group_name}"
                         f"/providers/Microsoft.Compute/{vmPath}"
                         f"/providers/{RP_PROVIDER}/serialPorts/0"
                         f"/connect?api-version=2018-05-01")

        from azure.cli.core._profile import Profile
        tokenInfo, _, _ = Profile().get_raw_token()
        accessToken = tokenInfo[1]
        applicationJsonFormat = "application/json"
        headers = {'authorization': "Bearer " + accessToken,
                   'accept': applicationJsonFormat,
                   'content-type': applicationJsonFormat}
        result = requests.post(connectionUrl, headers=headers)
        jsonResults = json.loads(result.text)
        self.assertTrue(result.status_code ==
                        200 and "connectionString" in jsonResults)
        websocketURL = jsonResults["connectionString"]

        ws = websocket.WebSocket()
        ws.connect(websocketURL + "?authorization=" + accessToken, timeout=30)
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
            'az storage account create -n {sa} -g {rg} -l {loc} --kind Storage --https-only')
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
            'az storage account create -n {sa} -g {rg} -l {loc} --kind Storage --https-only')
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
