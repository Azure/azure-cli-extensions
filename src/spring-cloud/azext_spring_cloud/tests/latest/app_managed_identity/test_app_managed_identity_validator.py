# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from argparse import Namespace
from azure.cli.core.azclierror import InvalidArgumentValueError
from ...._app_validator import (validate_app_identity_remove_or_warning)


class TestAppManagedIdentityRemoveValitor(unittest.TestCase):
    def test_invalid_user_identity_resource_id(self):
        fake_id = "fake-resource-id-1"
        user_assigned = [fake_id]
        ns = Namespace(user_assigned=user_assigned, system_assigned=None)
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_app_identity_remove_or_warning(ns)
        self.assertTrue("Invalid user-assigned managed identity resource ID" in str(context.exception))


    def test_invalid_user_identities(self):
        fake_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/fake-rg/providers/microsoft.managedidentity/userassignedidentities/fake-identity-name"
        user_assigned = set(fake_id)
        ns = Namespace(user_assigned=user_assigned, system_assigned=None)
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_app_identity_remove_or_warning(ns)
        self.assertTrue("Parameter value for \"user-assigned\" should be empty or a list of space-separated managed identity resource ID." in str(context.exception))
