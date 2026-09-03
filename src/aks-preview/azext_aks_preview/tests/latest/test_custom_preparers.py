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


if __name__ == "__main__":
    unittest.main()
