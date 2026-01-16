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


class test_microsoft_network(ScenarioTest):
    resource_applicationgateways_zr = {
        "type": "microsoft.network/applicationgateways",
        "zones": ["1", "2", "3"],
    }

    resource_applicationgateways_nonzr = {
        "type": "microsoft.network/applicationgateways",
        "zones": None,
    }

    resource_azurefirewalls_zr = {
        "type": "microsoft.network/azurefirewalls",
        "sku": {"capacity": 3},
        "zones": ["1", "2", "3"],
    }

    resource_azurefirewalls_nonzr = {
        "type": "microsoft.network/azurefirewalls",
        "sku": {"capacity": 1},
        "zones": None,
    }

    resource_loadbalancers_zr = {
        "type": "microsoft.network/loadbalancers",
        "properties": {"frontendIPConfigurations": [{"zones": ["1", "2", "3"]}]},
    }
    resource_loadbalancers_nonzr = {
        "type": "microsoft.network/loadbalancers",
        "properties": {"frontendIPConfigurations": [{"zones": None}]},
    }

    resource_publicipaddresses_zr = {
        "type": "microsoft.network/publicipaddresses",
        "sku": {"name": "Standard"},
        "zones": ["1", "2", "3"],
    }

    resource_publicipaddresses_nonzr = {
        "type": "microsoft.network/publicipaddresses",
        "sku": {"name": "Basic"},
        "zones": None,
    }

    resource_virtualnetworkgateways_zr = {
        "type": "microsoft.network/virtualnetworkgateways",
        "properties": {
            "sku": {
                "name": "VpnGw2AZ",
            }
        },
    }

    resource_virtualnetworkgateways_nonzr = {
        "type": "microsoft.network/virtualnetworkgateways",
        "properties": {
            "sku": {
                "name": "VpnGw2",
            }
        },
    }

    validator = None

    @classmethod
    def setUpClass(cls):
        super(test_microsoft_network, cls).setUpClass()
        # Load the resource type validators
        load_validators()
                
        resourceProvider = cls.resource_applicationgateways_zr["type"].split("/")[0]
        cls.validator = getResourceTypeValidator(resourceProvider)

    def test_applicationgateways_zr(self):
        # Test for zone redundancy scenario
        zrResult = self.validator.validate(self.resource_applicationgateways_zr)
        self.assertEqual(zrResult, ZoneRedundancyValidationResult.Yes)

    def test_applicationgateways_nonzr(self):
        # Test for non-zone redundancy scenario
        zrResult = self.validator.validate(self.resource_applicationgateways_nonzr)
        self.assertEqual(zrResult, ZoneRedundancyValidationResult.No)

    def test_azurefirewalls_zr(self):
        # Test for zone redundancy scenario
        zrResult = self.validator.validate(self.resource_azurefirewalls_zr)
        self.assertEqual(zrResult, ZoneRedundancyValidationResult.Yes)

    def test_azurefirewalls_nonzr(self):
        # Test for non-zone redundancy scenario
        zrResult = self.validator.validate(self.resource_azurefirewalls_nonzr)
        self.assertEqual(zrResult, ZoneRedundancyValidationResult.No)

    def test_loadbalancers_zr(self):
        # Test for zone redundancy scenario
        zrResult = self.validator.validate(self.resource_loadbalancers_zr)
        self.assertEqual(zrResult, ZoneRedundancyValidationResult.Yes)

    def test_loadbalancers_nonzr(self):
        # Test for non-zone redundancy scenario
        zrResult = self.validator.validate(self.resource_loadbalancers_nonzr)
        self.assertEqual(zrResult, ZoneRedundancyValidationResult.No)

    def test_publicipaddresses_zr(self):
        # Test for zone redundancy scenario
        zrResult = self.validator.validate(self.resource_publicipaddresses_zr)
        self.assertEqual(zrResult, ZoneRedundancyValidationResult.Yes)

    def test_publicipaddresses_nzr(self):
        # Test for non-zone redundancy scenario
        zrResult = self.validator.validate(self.resource_publicipaddresses_nonzr)
        self.assertEqual(zrResult, ZoneRedundancyValidationResult.No)

    def test_virtualnetworkgateways_zr(self):
        # Test for zone redundancy scenario
        zrResult = self.validator.validate(self.resource_virtualnetworkgateways_zr)
        self.assertEqual(zrResult, ZoneRedundancyValidationResult.Yes)

    def test_virtualnetworkgateways_nonzr(self):
        # Test for non-zone redundancy scenario
        zrResult = self.validator.validate(self.resource_virtualnetworkgateways_nonzr)
        self.assertEqual(zrResult, ZoneRedundancyValidationResult.No)
