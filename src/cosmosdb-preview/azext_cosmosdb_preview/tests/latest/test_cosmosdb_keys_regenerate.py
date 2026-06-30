# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import (
    DatabaseAccountRegenerateKeyParameters,
    KeyKind,
)


class CosmosDBKeysRegenerateBodyTest(unittest.TestCase):
    """Validate the regenerate-key request body honors the backend wire contract.

    The generated Cosmos DB SDK serializes the optional flag as the camelCase
    property ``skipAccountKeysLastUsageCheck``. The property must be omitted
    entirely when the CLI flag is not supplied so existing behavior is unchanged.
    """

    def test_skip_check_omitted_when_not_specified(self):
        params = DatabaseAccountRegenerateKeyParameters(key_kind=KeyKind.PRIMARY)
        body = params.serialize()
        self.assertEqual(body, {"keyKind": "primary"})
        self.assertNotIn("skipAccountKeysLastUsageCheck", body)

    def test_skip_check_true(self):
        params = DatabaseAccountRegenerateKeyParameters(
            key_kind=KeyKind.PRIMARY, skip_account_keys_last_usage_check=True)
        body = params.serialize()
        self.assertEqual(body.get("skipAccountKeysLastUsageCheck"), True)

    def test_skip_check_false(self):
        params = DatabaseAccountRegenerateKeyParameters(
            key_kind=KeyKind.SECONDARY, skip_account_keys_last_usage_check=False)
        body = params.serialize()
        self.assertEqual(body.get("skipAccountKeysLastUsageCheck"), False)


if __name__ == '__main__':
    unittest.main()
