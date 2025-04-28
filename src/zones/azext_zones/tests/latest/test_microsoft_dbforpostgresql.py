# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest)
from ..._resourceTypeValidation import getResourceTypeValidator, ZoneRedundancyValidationResult


class test_microsoft_dbforpostgresql(ScenarioTest):

    resource_zr = \
        {
            "type": "microsoft.dbforpostgresql/flexibleservers",
            "properties": {
                "highAvailability": {
                    "mode": "ZoneRedundant"
                }
            }
        }
    
    resource_nonzr = \
        {
            "type": "microsoft.dbforpostgresql/flexibleservers",
            "properties": {
                "highAvailability": {
                    "state": "NotEnabled",
                    "mode": "Disabled"
                }
            }
        }
    
    validator = None

    @classmethod
    def setUpClass(cls):
        super(test_microsoft_dbforpostgresql, cls).setUpClass()
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