# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from argparse import Namespace
from azure.cli.core.azclierror import InvalidArgumentValueError
from ...._app_managed_identity_validator import (validate_app_identity_remove_or_warning,
                                                 validate_app_identity_assign_or_warning)


FAKE_USER_IDENTITY_RESOURCE_ID = "/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/fake-rg/providers/microsoft.managedidentity/userassignedidentities/fake-identity-name"


class TestAppManagedIdentityRemoveValitor(unittest.TestCase):
    def test_invalid_user_identity_resource_id(self):
        fake_id = "fake-resource-id-1"
        user_assigned = [fake_id]
        ns = Namespace(user_assigned=user_assigned, system_assigned=None)
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_app_identity_remove_or_warning(ns)
        self.assertTrue("Invalid user-assigned managed identity resource ID" in str(context.exception))


    def test_invalid_user_identities(self):
        fake_id = FAKE_USER_IDENTITY_RESOURCE_ID
        user_assigned = set(fake_id)
        ns = Namespace(user_assigned=user_assigned, system_assigned=None)
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_app_identity_remove_or_warning(ns)
        self.assertTrue("Parameter value for \"user-assigned\" should be empty or a list of space-separated managed identity resource ID." in str(context.exception))


class TestAppManagedIdentityAssignValitor(unittest.TestCase):
    def test_scope_and_role_not_used_together_1(self):
        ns = Namespace(
            role="fake-role",
            scope=None,
            system_assigned=None,
            user_assigned=None)
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_app_identity_assign_or_warning(ns)
        self.assertTrue("Parameter \"role\" and \"scope\" should be used together." in str(context.exception))


    def test_scope_and_role_not_used_together_2(self):
        ns = Namespace(
            role=None,
            scope="fake-scope",
            system_assigned=None,
            user_assigned=None)
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_app_identity_assign_or_warning(ns)
        self.assertTrue("Parameter \"role\" and \"scope\" should be used together." in str(context.exception))


    def test_scope_and_role_not_used_together_3(self):
        ns = Namespace(
            role="fake-role",
            scope=None,
            system_assigned=True,
            user_assigned=None)
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_app_identity_assign_or_warning(ns)
        self.assertTrue("Parameter \"role\" and \"scope\" should be used together." in str(context.exception))


    def test_scope_and_role_not_used_together_4(self):
        ns = Namespace(
            role="fake-role",
            scope=None,
            system_assigned=True,
            user_assigned=["ua1"])
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_app_identity_assign_or_warning(ns)
        self.assertTrue("Parameter \"role\" and \"scope\" should be used together." in str(context.exception))


    def test_scope_and_role_not_used_together_5(self):
        ns = Namespace(
            role=None,
            scope="fake-scope",
            system_assigned=True,
            user_assigned=None)
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_app_identity_assign_or_warning(ns)
        self.assertTrue("Parameter \"role\" and \"scope\" should be used together." in str(context.exception))


    def test_scope_and_role_not_used_together_6(self):
        ns = Namespace(
            role=None,
            scope="fake-scope",
            system_assigned=True,
            user_assigned=["ua1"])
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_app_identity_assign_or_warning(ns)
        self.assertTrue("Parameter \"role\" and \"scope\" should be used together." in str(context.exception))


    def test_scope_and_role_without_system_identity_but_with_user_identity_1(self):
        ns = Namespace(
            role="fake-role",
            scope="fake-scope",
            system_assigned=None,
            user_assigned=["ua1"])
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_app_identity_assign_or_warning(ns)
        self.assertTrue("Invalid to use parameter \"role\" and \"scope\" with \"user-assigned\" parameter." in str(context.exception))


    def test_scope_and_role_without_system_identity_but_with_user_identity_2(self):
        ns = Namespace(
            role="fake-role",
            scope="fake-scope",
            system_assigned=False,
            user_assigned=["ua1"])
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_app_identity_assign_or_warning(ns)
        self.assertTrue("Invalid to use parameter \"role\" and \"scope\" with \"user-assigned\" parameter." in str(context.exception))


    def test_invalid_user_identity_resource_id_1(self):
        ns = Namespace(
            role=None,
            scope=None,
            system_assigned=True,
            user_assigned=["ua1"])
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_app_identity_assign_or_warning(ns)
        self.assertTrue("Invalid user-assigned managed identity resource ID" in str(context.exception))


    def test_invalid_user_identity_resource_id_2(self):
        ns = Namespace(
            role=None,
            scope=None,
            system_assigned=False,
            user_assigned=["ua1"])
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_app_identity_assign_or_warning(ns)
        self.assertTrue("Invalid user-assigned managed identity resource ID" in str(context.exception))


    def test_invalid_user_identity_resource_id_3(self):
        ns = Namespace(
            role=None,
            scope=None,
            system_assigned=None,
            user_assigned=["ua1"])
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_app_identity_assign_or_warning(ns)
        self.assertTrue("Invalid user-assigned managed identity resource ID" in str(context.exception))


    def test_invalid_user_identity_resource_id_4(self):
        ns = Namespace(
            role=None,
            scope=None,
            system_assigned=None,
            user_assigned=[FAKE_USER_IDENTITY_RESOURCE_ID])
        validate_app_identity_assign_or_warning(ns)
