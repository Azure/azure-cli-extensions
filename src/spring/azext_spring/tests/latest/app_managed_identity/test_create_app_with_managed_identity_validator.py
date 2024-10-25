# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from argparse import Namespace
from azure.cli.core.azclierror import InvalidArgumentValueError
from ...._app_managed_identity_validator import (validate_create_app_with_system_identity_or_warning,
                                                 validate_create_app_with_user_identity_or_warning)

FAKE_USER_IDENTITY_RESOURCE_ID = "/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/fake-rg/providers/microsoft.managedidentity/userassignedidentities/fake-identity-name"


class TestCreateAppWithManagedIdentityValitorWithConflict(unittest.TestCase):

    def test_system_identity_override_1(self):
        ns = Namespace(system_assigned=None,
                       assign_identity=False)
        validate_create_app_with_system_identity_or_warning(ns)
        self.assertEqual(ns.system_assigned, False)

    def test_system_identity_override_2(self):
        ns = Namespace(system_assigned=None,
                       assign_identity=True)
        validate_create_app_with_system_identity_or_warning(ns)
        self.assertEqual(ns.system_assigned, True)

    def test_system_identity_override_3(self):
        ns = Namespace(system_assigned=True,
                       assign_identity=None)
        validate_create_app_with_system_identity_or_warning(ns)
        self.assertEqual(ns.system_assigned, True)

    def test_system_identity_override_4(self):
        ns = Namespace(system_assigned=False,
                       assign_identity=None)
        validate_create_app_with_system_identity_or_warning(ns)
        self.assertEqual(ns.system_assigned, False)


class TestCreateAppWithManagedIdentityValitorWithConflict(unittest.TestCase):

    def test_conflict_parameter_1(self):
        ns = Namespace(system_assigned=None,
                       assign_identity=None)
        validate_create_app_with_system_identity_or_warning(ns)

    def test_conflict_parameter_2(self):
        ns = Namespace(system_assigned=False,
                       assign_identity=None)
        validate_create_app_with_system_identity_or_warning(ns)

    def test_conflict_parameter_3(self):
        ns = Namespace(system_assigned=True,
                       assign_identity=None)
        validate_create_app_with_system_identity_or_warning(ns)

    def test_conflict_parameter_4(self):
        ns = Namespace(system_assigned=None,
                       assign_identity=False)
        validate_create_app_with_system_identity_or_warning(ns)

    def test_conflict_parameter_5(self):
        ns = Namespace(system_assigned=False,
                       assign_identity=False)
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_create_app_with_system_identity_or_warning(ns)
        self.assertTrue(
            'Parameter "system-assigned" should not use together with "assign-identity".' in str(context.exception))

    def test_conflict_parameter_6(self):
        ns = Namespace(system_assigned=True,
                       assign_identity=False)
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_create_app_with_system_identity_or_warning(ns)
        self.assertTrue(
            'Parameter "system-assigned" should not use together with "assign-identity".' in str(context.exception))

    def test_conflict_parameter_7(self):
        ns = Namespace(system_assigned=None,
                       assign_identity=True)
        validate_create_app_with_system_identity_or_warning(ns)

    def test_conflict_parameter_8(self):
        ns = Namespace(system_assigned=False,
                       assign_identity=True)
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_create_app_with_system_identity_or_warning(ns)
        self.assertTrue(
            'Parameter "system-assigned" should not use together with "assign-identity".' in str(context.exception))

    def test_conflict_parameter_9(self):
        ns = Namespace(system_assigned=True,
                       assign_identity=True)
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_create_app_with_system_identity_or_warning(ns)
        self.assertTrue(
            'Parameter "system-assigned" should not use together with "assign-identity".' in str(context.exception))


class TestCreateAppWithManagedIdentityValitorWithUserIdentityId(unittest.TestCase):

    def test_user_identity_resource_id_1(self):
        ns = Namespace(user_assigned=None)
        validate_create_app_with_user_identity_or_warning(ns)

    def test_user_identity_resource_id_2(self):
        ns = Namespace(user_assigned=[FAKE_USER_IDENTITY_RESOURCE_ID])
        validate_create_app_with_user_identity_or_warning(ns)

    def test_user_identity_resource_id_3(self):
        ns = Namespace(user_assigned=["ua1"])
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_create_app_with_user_identity_or_warning(ns)
        self.assertTrue("Invalid user-assigned managed identity resource ID" in str(context.exception))
