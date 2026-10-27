# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from unittest.mock import patch

from azure.cli.testsdk import ScenarioTest


class SystemConfigurationScenarioTest(ScenarioTest):

    def setUp(self):
        super().setUp()
        if not self.in_recording:
            token_patch = patch(
                "azure.cli.core._profile.Profile.get_raw_token",
                return_value=(("Bearer", "recording-placeholder", {}), None, None),
            )
            token_patch.start()
            self.addCleanup(token_patch.stop)

    def test_system_configuration_show(self):
        self.cmd("aldo system-configuration show", checks=[
            self.check("name", "default"),
            self.check("type", "Microsoft.EdgeOperator/systemConfiguration"),
            self.check("type(id)", "string"),
            self.check("type(properties)", "object"),
            self.check("type(properties.externalDomainSuffix)", "string"),
            self.check("type(properties.imageVersion)", "string"),
            self.check("type(properties.ingressNicPrefixLength)", "number"),
            self.check("type(properties.ingressNicIpAddress)", "string"),
            self.check("type(properties.ingressNicDefaultGateway)", "string"),
        ])
        if not self.in_recording:
            self.assertTrue(self.cassette.all_played)

    def test_system_configuration_create_missing_fields(self):
        self.cmd("aldo system-configuration create", expect_failure=True)

        self.assertEqual(len(self.cassette.requests), 1)
        self.assertEqual(self.cassette.requests[0].method, "PUT")
        self.assertEqual(json.loads(self.cassette.requests[0].body), {"properties": {}})
        response = self.cassette.responses[0]
        self.assertEqual(response["status"]["code"], 400)
        error = json.loads(response["body"]["string"])["error"]
        self.assertEqual(error["code"], "InvalidRequest")
        self.assertEqual(len(error["details"]), 4)
        self.assertEqual({detail["target"] for detail in error["details"]}, {
            "Properties.DnsForwarderIpAddress",
            "Properties.ConnectionIntent",
            "Properties.StampId",
            "Properties.DeviceResourceId",
        })
        for detail in error["details"]:
            self.assertEqual(detail["code"], "InvalidField")
            self.assertIn("required", detail["message"].lower())
        if not self.in_recording:
            self.assertTrue(self.cassette.all_played)

    def test_system_configuration_create_and_show(self):
        subscription = self.get_subscription_id()
        self.kwargs.update({
            "dns": "192.0.2.53",
            "intent": "Connected",
            "stamp": "11111111-1111-1111-1111-111111111111",
            "device": (
                "/subscriptions/{subscription}/resourceGroups/rg-test/"
                "providers/Microsoft.Edge/disconnectedOperations/test-device"
            ).format(subscription=subscription),
        })
        checks = [
            self.check("name", "default"),
            self.check("type", "Microsoft.EdgeOperator/systemConfiguration", case_sensitive=False),
            self.check("properties.dnsForwarderIpAddress", "{dns}"),
            self.check("properties.connectionIntent", "{intent}"),
            self.check("properties.stampId", "{stamp}"),
            self.check("properties.deviceResourceId", "{device}"),
        ]
        self.cmd(
            "aldo system-configuration create --dns-forwarder-ip {dns} "
            "--connection-intent {intent} --stamp-id {stamp} "
            "--device-resource-id {device}",
            checks=checks + [self.check("properties.provisioningState", "Succeeded")],
        )
        self.cmd("aldo system-configuration show", checks=checks + [
            self.check("type(id)", "string"),
            self.check("type(properties)", "object"),
            self.check("type(properties.externalDomainSuffix)", "string"),
            self.check("type(properties.imageVersion)", "string"),
            self.check("type(properties.ingressNicPrefixLength)", "number"),
            self.check("type(properties.ingressNicIpAddress)", "string"),
            self.check("type(properties.ingressNicDefaultGateway)", "string"),
        ])
        if not self.in_recording:
            self.assertTrue(self.cassette.all_played)