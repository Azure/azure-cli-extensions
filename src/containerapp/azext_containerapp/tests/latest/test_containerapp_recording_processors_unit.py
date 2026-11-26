# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import unittest

from vcr.request import Request

from azext_containerapp.tests.latest.utils import LogAnalyticsSharedKeyReplacer


class TestLogAnalyticsSharedKeyReplacer(unittest.TestCase):
    def test_sanitizes_vcr_request_body(self):
        request = Request("PUT", "https://example.test", b'{"properties":{"sharedKey":"secret"}}', {})

        result = LogAnalyticsSharedKeyReplacer().process_request(request)

        self.assertIs(result, request)
        self.assertEqual(json.loads(result.body)["properties"]["sharedKey"], "fake-log-analytics-key")

    def test_sanitizes_response_body(self):
        response = {"body": {"string": '{"primarySharedKey":"secret","secondarySharedKey":"secret"}'}}

        result = LogAnalyticsSharedKeyReplacer().process_response(response)

        self.assertEqual(json.loads(result["body"]["string"]), {
            "primarySharedKey": "fake-log-analytics-key",
            "secondarySharedKey": "fake-log-analytics-key",
        })
