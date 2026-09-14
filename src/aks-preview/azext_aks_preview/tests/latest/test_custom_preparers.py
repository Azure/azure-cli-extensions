# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
from unittest.mock import patch

from azext_aks_preview.tests.latest.custom_preparers import (
    AKSCustomResourceGroupPreparer,
    ENV_VAR_FORCE_RESOURCE_GROUP_LOCATION,
    skip_test_if_location_unsupported,
)


class TestAKSCustomResourceGroupPreparer(unittest.TestCase):

    def _create_preparer(self, preserve_default_location):
        return AKSCustomResourceGroupPreparer(
            location="westus2",
            preserve_default_location=preserve_default_location,
        )

    @patch.dict(os.environ, {
        "AZURE_CLI_TEST_DEV_RESOURCE_GROUP_LOCATION": "eastus",
    }, clear=True)
    def test_default_location_override_is_used(self):
        preparer = self._create_preparer(preserve_default_location=False)

        self.assertEqual(preparer.location, "eastus")
        self.assertEqual(preparer.dev_setting_location, "eastus")

    @patch.dict(os.environ, {
        "AZURE_CLI_TEST_DEV_RESOURCE_GROUP_LOCATION": "eastus",
    }, clear=True)
    def test_preserved_location_wins_over_default_override(self):
        preparer = self._create_preparer(preserve_default_location=True)

        self.assertEqual(preparer.location, "westus2")
        self.assertEqual(preparer.dev_setting_location, "westus2")

    @patch.dict(os.environ, {
        ENV_VAR_FORCE_RESOURCE_GROUP_LOCATION: "westcentralus",
        "AZURE_CLI_TEST_DEV_RESOURCE_GROUP_LOCATION": "eastus",
    }, clear=True)
    def test_force_location_wins_over_default_override(self):
        preparer = self._create_preparer(preserve_default_location=False)

        self.assertEqual(preparer.location, "westcentralus")
        self.assertEqual(preparer.dev_setting_location, "westcentralus")

    @patch.dict(os.environ, {
        ENV_VAR_FORCE_RESOURCE_GROUP_LOCATION: "westcentralus",
        "AZURE_CLI_TEST_DEV_RESOURCE_GROUP_LOCATION": "eastus",
    }, clear=True)
    def test_force_location_wins_over_preserved_location(self):
        preparer = self._create_preparer(preserve_default_location=True)

        self.assertEqual(preparer.location, "westcentralus")
        self.assertEqual(preparer.dev_setting_location, "westcentralus")


class TestSkipTestIfLocationUnsupported(unittest.TestCase):

    class _FakeTestCase:
        def __init__(self):
            self.skipped_reason = None

        def skipTest(self, reason):
            self.skipped_reason = reason
            raise unittest.SkipTest(reason)

    def test_supported_location_does_not_skip(self):
        fake = self._FakeTestCase()
        # should not raise
        skip_test_if_location_unsupported(fake, "westus2", ["westus2", "westus3"], "hosted-system")
        self.assertIsNone(fake.skipped_reason)

    def test_supported_location_is_case_and_space_insensitive(self):
        fake = self._FakeTestCase()
        skip_test_if_location_unsupported(fake, "West US 2", ["westus2", "westus3"], "hosted-system")
        self.assertIsNone(fake.skipped_reason)

    def test_unsupported_location_skips_precisely(self):
        fake = self._FakeTestCase()
        with self.assertRaises(unittest.SkipTest):
            skip_test_if_location_unsupported(fake, "eastus", ["westus2", "westus3"], "hosted-system")
        self.assertIn("hosted-system", fake.skipped_reason)
        self.assertIn("eastus", fake.skipped_reason)


if __name__ == "__main__":
    unittest.main()
