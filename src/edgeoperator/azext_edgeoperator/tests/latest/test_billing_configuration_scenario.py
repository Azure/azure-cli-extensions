# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import tempfile
from unittest.mock import patch

from azure.cli.testsdk import ScenarioTest

# Recording these tests replaces the active billing configuration on the target environment.
STAMP_ID = "401ECB09-83EC-4777-A56C-6FFF26BCC815"


class BillingConfigurationScenarioTest(ScenarioTest):

    def setUp(self):
        super().setUp()
        if not self.in_recording:
            token_patch = patch(
                "azure.cli.core._profile.Profile.get_raw_token",
                return_value=(("Bearer", "recording-placeholder", {}), None, None),
            )
            token_patch.start()
            self.addCleanup(token_patch.stop)
        subscription = self.get_subscription_id()
        self.kwargs.update({
            "resource": (
                "/subscriptions/{}/resourceGroups/rg-billing-test/providers/"
                "Microsoft.Edge/disconnectedOperations/billing-test"
            ).format(subscription),
            "stamp": STAMP_ID,
        })

    def test_billing_configuration_create_show_and_snapshots(self):
        checks = [
            self.check("name", "default"),
            self.check("type", "Microsoft.EdgeOperator/billingConfigurations", case_sensitive=False),
            self.check("properties.resourceId", "{resource}"),
            self.check("properties.resourceName", "billing-test"),
            self.check("properties.billingConfiguration.current.cores", 12),
            self.check("properties.billingConfiguration.upcoming.cores", 24),
            self.check("properties.benefitPlans.windowsServerVmCount", 5),
        ]
        self.cmd(
            "aldo billing-configuration create --disconnected-operation {resource} --stamp-id {stamp} "
            "--location eastus --billing-model Capacity --connection-intent Connected --cloud Public "
            "--auto-renew Enabled --billing-status Enabled --cores 12 --pricing-model Trial "
            "--start-date 2025-11-01 --end-date 2025-12-31 --upcoming-cores 24 --upcoming-pricing-model Annual "
            "--upcoming-start-date 2026-01-01 --azure-hybrid-benefit Enabled --windows-server-vm-count 5",
            checks=checks + [self.check("properties.provisioningState", "Succeeded")],
        )
        self.cmd("aldo billing-configuration show", checks=checks)

        snapshots = self.cmd("aldo billing-configuration snapshot list").get_output_in_json()
        self.assertGreater(len(snapshots), 0)
        self.kwargs["snapshot"] = snapshots[0]["name"]
        self.cmd("aldo billing-configuration snapshot show --name {snapshot}", checks=[
            self.check("name", "{snapshot}"),
            self.check("type(properties.billingConfiguration)", "object"),
        ])
        if not self.in_recording:
            self.assertTrue(self.cassette.all_played)

    def test_billing_configuration_create_with_manifest(self):
        manifest = {
            "properties": {
                "resourceId": self.kwargs["resource"],
                "resourceName": "billing-test",
                "stampId": STAMP_ID,
                "location": "eastus",
                "billingModel": "Capacity",
                "connectionIntent": "Connected",
                "billingConfiguration": {
                    "autoRenew": "Enabled",
                    "billingStatus": "Enabled",
                    "current": {"cores": 12, "pricingModel": "Annual", "startDate": "2026-01-01"},
                },
                "licenses": [{
                    "benefitType": "AzureHybridBenefit",
                    "benefitName": "WindowsServer",
                    "current": {"unit": "CoresManaged", "quantity": 12},
                }],
                # Shape-only fixture: the service does not yet verify cryptographic signatures.
                "signatures": [{"name": "primary", "signedHash": "c2lnbmF0dXJl", "signingPublicKey": "Y2VydGlmaWNhdGU="}],
            }
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            self.kwargs["manifest"] = os.path.join(temp_dir, "manifest.json")
            with open(self.kwargs["manifest"], "w", encoding="utf-8") as manifest_file:
                json.dump(manifest, manifest_file)

            self.cmd("aldo billing-configuration create --manifest \"{manifest}\"", checks=[
                self.check("properties.licenses[0].benefitName", "WindowsServer"),
                self.check("properties.signatures[0].name", "primary"),
            ])

        sent = json.loads(self.cassette.requests[0].body)["properties"]
        self.assertEqual(sent["licenses"], manifest["properties"]["licenses"])
        self.assertEqual(sent["signatures"], manifest["properties"]["signatures"])
        if not self.in_recording:
            self.assertTrue(self.cassette.all_played)
