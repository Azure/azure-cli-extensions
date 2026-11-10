# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from types import SimpleNamespace
from unittest import TestCase

from ._recording_processors import ArmEndpointNormalizer, PrivateAuthRequestFilter


class RecordingProcessorsTest(TestCase):

    def test_normalizes_arm_request_hosts(self):
        for host in ("management", "armmanagement"):
            with self.subTest(host=host):
                request = SimpleNamespace(
                    uri="https://{}.autonomous.cloud.private/providers/Microsoft.EdgeOperator/test".format(host)
                )
                result = ArmEndpointNormalizer().process_request(request)
                self.assertEqual(result.uri, "https://management.azure.com/providers/Microsoft.EdgeOperator/test")

    def test_normalizes_response_urls_without_changing_body_type(self):
        url = "https://management.autonomous.cloud.private/providers/Microsoft.EdgeOperator/test"
        expected = "https://management.azure.com/providers/Microsoft.EdgeOperator/test"
        for body in (url, url.encode("utf-8")):
            with self.subTest(body_type=type(body)):
                response = {
                    "headers": {"Azure-AsyncOperation": [url], "Location": [url]},
                    "body": {"string": body},
                }
                result = ArmEndpointNormalizer().process_response(response)
                self.assertEqual(result["headers"]["Azure-AsyncOperation"], [expected])
                self.assertEqual(result["headers"]["Location"], [expected])
                self.assertIsInstance(result["body"]["string"], type(body))
                self.assertEqual(
                    result["body"]["string"], expected.encode("utf-8") if isinstance(body, bytes) else expected
                )

    def test_filters_private_authentication_requests(self):
        request = SimpleNamespace(uri="https://login.autonomous.cloud.private/organizations/oauth2/v2.0/token")
        self.assertIsNone(PrivateAuthRequestFilter().process_request(request))

    def test_preserves_edgeoperator_requests_and_public_endpoints(self):
        for url in (
            "https://management.autonomous.cloud.private/providers/Microsoft.EdgeOperator/operationStatuses/test",
            "https://management.azure.com/subscriptions/test/providers/Microsoft.EdgeOperator/billingConfigurations",
        ):
            with self.subTest(url=url):
                request = SimpleNamespace(uri=url)
                self.assertIs(PrivateAuthRequestFilter().process_request(request), request)
