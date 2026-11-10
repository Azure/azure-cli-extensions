# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import tempfile

from unittest import TestCase
from unittest.mock import Mock, call, patch

from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
    RequiredArgumentMissingError,
)

from azext_edgeoperator._format import transform_billing_snapshot_list
from azext_edgeoperator.custom import (
    BILLING_API_VERSION,
    create_billing_configuration,
    list_billing_configuration_snapshots,
    show_billing_configuration,
    show_billing_configuration_snapshot,
)

SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
BILLING_URL = (
    "https://management.example.com/subscriptions/{}/providers/Microsoft.EdgeOperator/"
    "billingConfigurations/default"
).format(SUBSCRIPTION_ID)
DISCONNECTED_OPERATION = (
    "/subscriptions/{}/resourceGroups/rg-aldo/providers/Microsoft.Edge/disconnectedOperations/example"
).format(SUBSCRIPTION_ID)
MANIFEST_PROPERTIES = {
    "resourceId": DISCONNECTED_OPERATION,
    "resourceName": "example",
    "stampId": "11111111-1111-1111-1111-111111111111",
    "location": "eastus",
    "billingModel": "Capacity",
    "connectionIntent": "Disconnected",
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
    "signatures": [{"name": "primary", "signedHash": "c2lnbmF0dXJl", "signingPublicKey": "Y2VydGlmaWNhdGU="}],
}
REQUIRED_FLAGS = {
    "disconnected_operation": DISCONNECTED_OPERATION,
    "stamp_id": "11111111-1111-1111-1111-111111111111",
    "location": "eastus",
    "billing_model": "Capacity",
    "connection_intent": "Disconnected",
    "auto_renew": "Enabled",
    "billing_status": "Enabled",
    "cores": 12,
    "pricing_model": "Annual",
    "start_date": "2026-01-01",
}


def _response(body):
    response = Mock()
    response.json.return_value = body
    return response


class BillingConfigurationCustomTest(TestCase):

    def setUp(self):
        subscription_patch = patch("azext_edgeoperator.custom.get_subscription_id")
        subscription_patch.start().return_value = SUBSCRIPTION_ID
        self.addCleanup(subscription_patch.stop)
        request_patch = patch("azext_edgeoperator.custom.send_raw_request")
        self.send_raw_request = request_patch.start()
        self.addCleanup(request_patch.stop)
        self.cli_ctx = Mock()
        self.cli_ctx.cloud.endpoints.resource_manager = "https://management.example.com/"
        self.cmd = Mock(cli_ctx=self.cli_ctx)
        temp_dir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.addCleanup(temp_dir.cleanup)
        self.temp_dir = temp_dir.name

    def _write_manifest(self, text):
        path = os.path.join(self.temp_dir, "manifest.json")
        with open(path, "w", encoding="utf-8") as manifest_file:
            manifest_file.write(text)
        return path

    def _sent_text(self):
        return self.send_raw_request.call_args.kwargs["body"]

    def _sent_properties(self):
        return json.loads(self._sent_text())["properties"]

    def test_show_uses_billing_api_version(self):
        result = show_billing_configuration(self.cmd)

        self.send_raw_request.assert_called_once_with(
            self.cli_ctx, "GET", BILLING_URL + "?api-version=" + BILLING_API_VERSION
        )
        self.assertEqual(result, self.send_raw_request.return_value.json.return_value)

    def test_create_with_full_body_manifest_forwards_properties_unchanged(self):
        manifest = {"id": "ignored", "etag": "ignored", "properties": MANIFEST_PROPERTIES}
        path = self._write_manifest(json.dumps(manifest))

        result = create_billing_configuration(self.cmd, manifest=path)

        self.send_raw_request.assert_called_once_with(
            self.cli_ctx, "PUT", BILLING_URL + "?api-version=" + BILLING_API_VERSION,
            body=self._sent_text(), headers=None
        )
        self.assertEqual(json.loads(self._sent_text()), {"properties": MANIFEST_PROPERTIES})
        self.assertEqual(list(self._sent_properties()), list(MANIFEST_PROPERTIES))
        self.assertEqual(result, self.send_raw_request.return_value.json.return_value)

    def test_create_with_properties_only_manifest(self):
        path = self._write_manifest("\ufeff" + json.dumps(MANIFEST_PROPERTIES))

        create_billing_configuration(self.cmd, manifest=path)

        self.assertEqual(self._sent_properties(), MANIFEST_PROPERTIES)

    def test_create_rejects_manifest_with_individual_arguments(self):
        path = self._write_manifest(json.dumps(MANIFEST_PROPERTIES))

        with self.assertRaises(MutuallyExclusiveArgumentError):
            create_billing_configuration(self.cmd, manifest=path, cores=24)
        self.send_raw_request.assert_not_called()

    def test_create_rejects_invalid_manifest(self):
        for content, error in (
            ("[1, 2]", "JSON object"),
            ('{"properties": [1]}', "'properties' value"),
        ):
            with self.subTest(content=content):
                with self.assertRaisesRegex(InvalidArgumentValueError, error):
                    create_billing_configuration(self.cmd, manifest=self._write_manifest(content))
        with self.assertRaisesRegex(InvalidArgumentValueError, "Unable to read --manifest"):
            create_billing_configuration(self.cmd, manifest=os.path.join(self.temp_dir, "missing.json"))
        self.send_raw_request.assert_not_called()

    def test_create_with_required_arguments(self):
        create_billing_configuration(self.cmd, **REQUIRED_FLAGS)

        self.assertEqual(self._sent_properties(), {
            "resourceId": DISCONNECTED_OPERATION,
            "resourceName": "example",
            "stampId": "11111111-1111-1111-1111-111111111111",
            "location": "eastus",
            "billingModel": "Capacity",
            "connectionIntent": "Disconnected",
            "billingConfiguration": {
                "autoRenew": "Enabled",
                "billingStatus": "Enabled",
                "current": {"cores": 12, "pricingModel": "Annual", "startDate": "2026-01-01"},
            },
        })

    def test_create_with_all_arguments(self):
        create_billing_configuration(
            self.cmd, cloud="Public", end_date="2026-12-31", upcoming_cores=24, upcoming_pricing_model="Annual",
            upcoming_start_date="2027-01-01", upcoming_end_date="2027-12-31", azure_hybrid_benefit="Enabled",
            windows_server_vm_count=5, **REQUIRED_FLAGS
        )

        properties = self._sent_properties()
        self.assertEqual(properties["cloud"], "Public")
        self.assertEqual(properties["billingConfiguration"]["current"]["endDate"], "2026-12-31")
        self.assertEqual(properties["billingConfiguration"]["upcoming"], {
            "cores": 24, "pricingModel": "Annual", "startDate": "2027-01-01", "endDate": "2027-12-31",
        })
        self.assertEqual(properties["benefitPlans"], {
            "azureHybridWindowsServerBenefit": "Enabled", "windowsServerVmCount": 5,
        })

    def test_create_requires_manifest_or_required_arguments(self):
        with self.assertRaisesRegex(RequiredArgumentMissingError, "--manifest.*--disconnected-operation.*--start-date"):
            create_billing_configuration(self.cmd)

        flags = dict(REQUIRED_FLAGS, cores=None)
        with self.assertRaisesRegex(RequiredArgumentMissingError, "arguments: --cores\\.$"):
            create_billing_configuration(self.cmd, **flags)
        self.send_raw_request.assert_not_called()

    def test_create_requires_complete_upcoming_period(self):
        with self.assertRaisesRegex(RequiredArgumentMissingError,
                                    "--upcoming-cores, --upcoming-pricing-model, --upcoming-start-date"):
            create_billing_configuration(self.cmd, upcoming_end_date="2027-12-31", **REQUIRED_FLAGS)
        self.send_raw_request.assert_not_called()

    def test_create_rejects_invalid_disconnected_operation(self):
        flags = dict(REQUIRED_FLAGS, disconnected_operation="example")

        with self.assertRaisesRegex(InvalidArgumentValueError, "--disconnected-operation"):
            create_billing_configuration(self.cmd, **flags)
        self.send_raw_request.assert_not_called()

    def test_create_sends_concurrency_headers(self):
        create_billing_configuration(self.cmd, if_match='"etag-1"', if_none_match="*", **REQUIRED_FLAGS)

        headers = self.send_raw_request.call_args.kwargs["headers"]
        self.assertEqual(json.loads(headers[0]), {"If-Match": '"etag-1"', "If-None-Match": "*"})

    def test_snapshot_show_and_list(self):
        next_link = BILLING_URL + "/snapshots?api-version=" + BILLING_API_VERSION + "&page=2"
        self.send_raw_request.side_effect = [
            _response({"name": "snapshot1"}),
            _response({"value": [{"name": "snapshot1"}], "nextLink": next_link}),
            _response({"value": [{"name": "snapshot2"}]}),
        ]

        self.assertEqual(show_billing_configuration_snapshot(self.cmd, "snapshot1"), {"name": "snapshot1"})
        self.assertEqual(list_billing_configuration_snapshots(self.cmd), [{"name": "snapshot1"}, {"name": "snapshot2"}])
        self.assertEqual(self.send_raw_request.call_args_list, [
            call(self.cli_ctx, "GET", BILLING_URL + "/snapshots/snapshot1?api-version=" + BILLING_API_VERSION),
            call(self.cli_ctx, "GET", BILLING_URL + "/snapshots?api-version=" + BILLING_API_VERSION),
            call(self.cli_ctx, "GET", next_link),
        ])

    def test_snapshot_list_table_format(self):
        rows = transform_billing_snapshot_list([{"name": "snapshot1", "properties": MANIFEST_PROPERTIES}, {}])

        self.assertEqual(list(rows[0].items()), [
            ("Name", "snapshot1"), ("BillingStatus", "Enabled"), ("Cores", 12),
            ("PricingModel", "Annual"), ("StartDate", "2026-01-01"), ("EndDate", None),
        ])
        self.assertIsNone(rows[1]["Name"])
