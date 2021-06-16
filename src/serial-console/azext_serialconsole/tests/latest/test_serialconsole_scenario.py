# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import json
import requests
import websocket
from azext_serialconsole.custom import checkResource
from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (LiveScenarioTest, StorageAccountPreparer, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class SerialconsoleScenarioTest(LiveScenarioTest):
    def setUp(self):
        self.buffer = ""

    def check_result(self, resource_group_name, vm_vmss_name, vmss_instanceid = None, message = ""):

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
        self.assertTrue(result.status_code == 200 and "connectionString" in jsonResults)
        websocketURL = jsonResults["connectionString"]

        ws = websocket.WebSocket()
        ws.connect(websocketURL + "?authorization=" + accessToken, timeout = 30)
        while True:
            try:
                self.buffer += ws.recv()
            except websocket.WebSocketTimeoutException:
                break

        assert message in self.buffer

    @ResourceGroupPreparer(name_prefix='cli_test_serialconsole', location = 'westus2')
    def test_send_sysrq(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        self.kwargs.update({
            'sa': self.create_random_name(prefix='cli', length=24),
            'rg': resource_group,
            'name1': name,
            'urn': 'UbuntuLTS'
        })
        self.cmd('az storage account create -n {sa} -g {rg} -l westus2 --kind Storage --https-only')
        self.cmd('az vm create -g {rg} -n {name1} --image {urn} --boot-diagnostics-storage {sa}')
        self.cmd('serial-console send sysrq -g {rg} -n {name1} --input h')
        self.check_result(resource_group, name, message = "sysrq: HELP")

    @ResourceGroupPreparer(name_prefix='cli_test_serialconsole', location = 'westus2')
    def test_send_nmi(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        self.kwargs.update({
            'sa': self.create_random_name(prefix='cli', length=24),
            'rg': resource_group,
            'name1': name,
            'urn': 'UbuntuLTS'
        })
        self.cmd('az storage account create -n {sa} -g {rg} -l westus2 --kind Storage --https-only')
        self.cmd('az vm create -g {rg} -n {name1} --image {urn} --boot-diagnostics-storage {sa}')
        self.cmd('serial-console send nmi -g {rg} -n {name1}')
        self.check_result(resource_group, name, message = "NMI received")
