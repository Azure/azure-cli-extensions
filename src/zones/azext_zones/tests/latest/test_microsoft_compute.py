# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import ScenarioTest
from ..._resourceTypeValidation import (
    getResourceTypeValidator,
    load_validators,
    ZoneRedundancyValidationResult,
)


class test_microsoft_app(ScenarioTest):
    resource_disk_zr = {"type": "microsoft.compute/disks", "zones": ["1", "2", "3"]}

    resource_disk_nonzr = {"type": "microsoft.compute/disks", "zones": None}

    resource_vmss_zr = {
        "type": "microsoft.compute/virtualmachinescalesets",
        "zones": ["1", "2", "3"],
    }

    resource_vmss_nonzr = {
        "type": "microsoft.compute/virtualmachinescalesets",
        "zones": None,
    }

    resource_vm_zr = {
        "type": "microsoft.compute/virtualmachines",
        "zones": ["1", "2", "3"],
    }

    resource_vm_nonzr = {"type": "microsoft.compute/virtualmachines", "zones": None}

    validator = None

    @classmethod
    def setUpClass(cls):
        super(test_microsoft_app, cls).setUpClass()
        # Load the resource type validators
        load_validators()

        resourceProvider = cls.resource_disk_zr["type"].split("/")[0]
        cls.validator = getResourceTypeValidator(resourceProvider)

    def test_disk_zr(self):
        # Test for zone redundancy scenario
        zrResult = self.validator.validate(self.resource_disk_zr)
        self.assertEqual(zrResult, ZoneRedundancyValidationResult.Yes)

    def test_disk_nonzr(self):
        # Test for non-zone redundancy scenario
        zrResult = self.validator.validate(self.resource_disk_nonzr)
        self.assertEqual(zrResult, ZoneRedundancyValidationResult.No)

    def test_vmss_zr(self):
        # Test for zone redundancy scenario
        zrResult = self.validator.validate(self.resource_vmss_zr)
        self.assertEqual(zrResult, ZoneRedundancyValidationResult.Yes)

    def test_vmss_nonzr(self):
        # Test for non-zone redundancy scenario
        zrResult = self.validator.validate(self.resource_vmss_nonzr)
        self.assertEqual(zrResult, ZoneRedundancyValidationResult.No)

    def test_vm_zr(self):
        # Test for zone redundancy scenario
        zrResult = self.validator.validate(self.resource_vm_zr)
        self.assertEqual(zrResult, ZoneRedundancyValidationResult.Yes)

    def test_vm_nonzr(self):
        # Test for non-zone redundancy scenario
        zrResult = self.validator.validate(self.resource_vm_nonzr)
        self.assertEqual(zrResult, ZoneRedundancyValidationResult.No)
