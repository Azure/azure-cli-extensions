# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest)
from ..._resourceTypeValidation import getResourceTypeValidator, ZoneRedundancyValidationResult


class test_microsoft_apimanagement(ScenarioTest):

    resource_zr = \
        {
            "type": "microsoft.apimanagement/service",
            "sku": {
                "name": "Premium",
                "capacity": 3
            },
            "zones": [
                "1",
                "2",
                "3"
            ]
        }

    resource_nonzr = \
        {
            "type": "microsoft.apimanagement/service",
            "sku": {
                "name": "Premium",
                "capacity": 1
            },
            "tags": {},
            "zones": None
        }
    
    validator = None

    @classmethod
    def setUpClass(cls):
        super(test_microsoft_apimanagement, cls).setUpClass()
        resourceProvider = cls.resource_zr['type'].split('/')[0]
        cls.validator = getResourceTypeValidator(resourceProvider)


    def test_zr(self):
        # Test for zone redundancy scenario
        zrResult = self.validator.validate(self.resource_zr)
        self.assertEqual(zrResult, ZoneRedundancyValidationResult.Yes)

    def test_nonzr(self):
        # Test for non-zone redundancy scenario
        zrResult = self.validator.validate(self.resource_nonzr)
        self.assertEqual(zrResult, ZoneRedundancyValidationResult.No)