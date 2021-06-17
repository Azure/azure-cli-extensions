# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from azext_spring_cloud.custom import get_connection_string_or_instrumentation_key

class SimplifiedApplicationInsightsCompoent:
    def __init__(self):
        self.connection_string = None
        self.instrumentation_key = None


class AzureSpringCloudTestCase(unittest.TestCase):
    def setUp(self):
        self._connection_string = "InstrumentationKey=11111111-0000-0000-0000-000000000000;IngestionEndpoint=https://11111111.00.0000000000000000000.00000.000/"
        self._instrumentation_key = "11111111-0000-0000-0000-000000000000"


    def test_get_conenction_string_or_instrumentation_key_case_1_connection_string_exists(self):
        appinsights = SimplifiedApplicationInsightsCompoent()
        appinsights.connection_string = self._connection_string
        appinsights.instrumentation_key = self._instrumentation_key
        self.assertEqual(self._connection_string, get_connection_string_or_instrumentation_key(appinsights))


    def test_get_conenction_string_or_instrumentation_key_case_2_connection_string_not_exist(self):
        appinsights = SimplifiedApplicationInsightsCompoent()
        appinsights.connection_string = None
        appinsights.instrumentation_key = self._instrumentation_key
        self.assertEqual(self._instrumentation_key, get_connection_string_or_instrumentation_key(appinsights))


    def test_get_conenction_string_or_instrumentation_key_case_3_no_credential(self):
        appinsights = SimplifiedApplicationInsightsCompoent()
        appinsights.connection_string = None
        appinsights.instrumentation_key = None
        self.assertIsNone(get_connection_string_or_instrumentation_key(appinsights))


if __name__ == '__main__':
    unittest.main()
