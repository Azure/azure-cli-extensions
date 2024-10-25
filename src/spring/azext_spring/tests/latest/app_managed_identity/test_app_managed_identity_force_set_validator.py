# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from argparse import Namespace
from azure.cli.core.azclierror import InvalidArgumentValueError
from ...._app_managed_identity_validator import (validate_app_force_set_system_identity_or_warning,
                                                 validate_app_force_set_user_identity_or_warning)

FAKE_LOWER_USER_IDENTITY_RESOURCE_ID_0 = "/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/fake-rg/providers/microsoft.managedidentity/userassignedidentities/fake-identity-name-0"
FAKE_UPPER_USER_IDENTITY_RESOURCE_ID_0 = FAKE_LOWER_USER_IDENTITY_RESOURCE_ID_0.upper()
FAKE_LOWER_USER_IDENTITY_RESOURCE_ID_1 = "/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/fake-rg/providers/microsoft.managedidentity/userassignedidentities/fake-identity-name-1"
FAKE_UPPER_USER_IDENTITY_RESOURCE_ID_1 = FAKE_LOWER_USER_IDENTITY_RESOURCE_ID_1.upper()


class TestAppForceSetSystemIdentityValitor(unittest.TestCase):

    def test_force_set_system_identity_valid_input_1(self):
        ns = Namespace(system_assigned="DISAble")
        validate_app_force_set_system_identity_or_warning(ns)
        self.assertTrue("disable", ns.system_assigned)

    def test_force_set_system_identity_valid_input_2(self):
        ns = Namespace(system_assigned="disable")
        validate_app_force_set_system_identity_or_warning(ns)
        self.assertTrue("disable", ns.system_assigned)

    def test_force_set_system_identity_valid_input_3(self):
        ns = Namespace(system_assigned="DISABLE")
        validate_app_force_set_system_identity_or_warning(ns)
        self.assertTrue("disable", ns.system_assigned)

    def test_force_set_system_identity_valid_input_4(self):
        ns = Namespace(system_assigned="enAble")
        validate_app_force_set_system_identity_or_warning(ns)
        self.assertTrue("enable", ns.system_assigned)

    def test_force_set_system_identity_valid_input_5(self):
        ns = Namespace(system_assigned="enable")
        validate_app_force_set_system_identity_or_warning(ns)
        self.assertTrue("enable", ns.system_assigned)

    def test_force_set_system_identity_valid_input_6(self):
        ns = Namespace(system_assigned="ENABLE")
        validate_app_force_set_system_identity_or_warning(ns)
        self.assertTrue("enable", ns.system_assigned)

    def test_force_set_system_identity_invalid_input(self):
        ns = Namespace(system_assigned="randomestring")
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_app_force_set_system_identity_or_warning(ns)
        self.assertTrue('Allowed values for "system-assigned" are:' in str(context.exception))


class TestAppForceSetUserIdentityValitor(unittest.TestCase):

    def test_valid_input_1(self):
        ns = Namespace(user_assigned=["DISable"])
        validate_app_force_set_user_identity_or_warning(ns)
        self.assertEqual("disable", ns.user_assigned[0])

    def test_valid_input_2(self):
        ns = Namespace(user_assigned=["disable"])
        validate_app_force_set_user_identity_or_warning(ns)
        self.assertEqual("disable", ns.user_assigned[0])

    def test_valid_input_3(self):
        ns = Namespace(user_assigned=["DISABLE"])
        validate_app_force_set_user_identity_or_warning(ns)
        self.assertEqual("disable", ns.user_assigned[0])

    def test_valid_input_4(self):
        ns = Namespace(user_assigned=[FAKE_UPPER_USER_IDENTITY_RESOURCE_ID_0])
        validate_app_force_set_user_identity_or_warning(ns)
        self.assertEqual(FAKE_LOWER_USER_IDENTITY_RESOURCE_ID_0, ns.user_assigned[0])

    def test_valid_input_5(self):
        ns = Namespace(user_assigned=[FAKE_UPPER_USER_IDENTITY_RESOURCE_ID_0, FAKE_LOWER_USER_IDENTITY_RESOURCE_ID_1])
        validate_app_force_set_user_identity_or_warning(ns)
        self.assertEqual(FAKE_LOWER_USER_IDENTITY_RESOURCE_ID_0, ns.user_assigned[0])
        self.assertEqual(FAKE_LOWER_USER_IDENTITY_RESOURCE_ID_1, ns.user_assigned[1])

    def test_invalid_input_1(self):
        ns = Namespace(user_assigned=["random_input"])
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_app_force_set_user_identity_or_warning(ns)
        self.assertTrue('Allowed values for "user-assigned" are:' in str(context.exception))

    def test_invalid_input_2(self):
        ns = Namespace(user_assigned=["ua1", "ua2"])
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_app_force_set_user_identity_or_warning(ns)
        self.assertTrue('Invalid user-assigned managed identity resource ID' in str(context.exception))
