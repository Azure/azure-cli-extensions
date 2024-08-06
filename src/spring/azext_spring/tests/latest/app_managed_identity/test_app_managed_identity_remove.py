# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from argparse import Namespace
from ....vendored_sdks.appplatform.v2024_05_01_preview.models import ManagedIdentityType
from ....app_managed_identity import (_get_new_identity_type_for_remove)


class TestAppManagedIdentityRemoveForTypeNone(unittest.TestCase):

    def test_get_new_identity_type_for_remove_for_type_none_1(self):
        exist_identity_type = ManagedIdentityType.NONE
        is_remove_system_identity = False
        new_user_identities = []
        new_identity_type = _get_new_identity_type_for_remove(exist_identity_type,
                                                              is_remove_system_identity,
                                                              new_user_identities)
        self.assertEqual(new_identity_type, ManagedIdentityType.NONE)

    def test_get_new_identity_type_for_remove_for_type_none_2(self):
        exist_identity_type = ManagedIdentityType.NONE
        is_remove_system_identity = True
        new_user_identities = []
        new_identity_type = _get_new_identity_type_for_remove(exist_identity_type,
                                                              is_remove_system_identity,
                                                              new_user_identities)
        self.assertEqual(new_identity_type, ManagedIdentityType.NONE)


class TestAppManagedIdentityRemoveForTypeSystemAssigned(unittest.TestCase):

    def test_get_new_identity_type_for_remove_for_system_assigned_1(self):
        exist_identity_type = ManagedIdentityType.SYSTEM_ASSIGNED
        is_remove_system_identity = False
        new_user_identities = []
        new_identity_type = _get_new_identity_type_for_remove(exist_identity_type,
                                                              is_remove_system_identity,
                                                              new_user_identities)
        self.assertEqual(new_identity_type, ManagedIdentityType.SYSTEM_ASSIGNED)

    def test_get_new_identity_type_for_remove_for_system_assigned_2(self):
        exist_identity_type = ManagedIdentityType.SYSTEM_ASSIGNED
        is_remove_system_identity = True
        new_user_identities = []
        new_identity_type = _get_new_identity_type_for_remove(exist_identity_type,
                                                              is_remove_system_identity,
                                                              new_user_identities)
        self.assertEqual(new_identity_type, ManagedIdentityType.NONE)

    def test_get_new_identity_type_for_remove_for_system_assigned_3(self):
        exist_identity_type = ManagedIdentityType.SYSTEM_ASSIGNED
        is_remove_system_identity = False
        new_user_identities = ["ua1"]
        new_identity_type = _get_new_identity_type_for_remove(exist_identity_type,
                                                              is_remove_system_identity,
                                                              new_user_identities)
        self.assertEqual(new_identity_type, ManagedIdentityType.SYSTEM_ASSIGNED)

    def test_get_new_identity_type_for_remove_for_system_assigned_4(self):
        exist_identity_type = ManagedIdentityType.SYSTEM_ASSIGNED
        is_remove_system_identity = True
        new_user_identities = ["ua1"]
        new_identity_type = _get_new_identity_type_for_remove(exist_identity_type,
                                                              is_remove_system_identity,
                                                              new_user_identities)
        self.assertEqual(new_identity_type, ManagedIdentityType.NONE)

    def test_get_new_identity_type_for_remove_for_system_assigned_5(self):
        exist_identity_type = ManagedIdentityType.SYSTEM_ASSIGNED
        is_remove_system_identity = None
        new_user_identities = ["ua1"]
        new_identity_type = _get_new_identity_type_for_remove(exist_identity_type,
                                                              is_remove_system_identity,
                                                              new_user_identities)
        self.assertEqual(new_identity_type, ManagedIdentityType.SYSTEM_ASSIGNED)


class TestAppManagedIdentityRemoveForTypeUserAssigned(unittest.TestCase):

    def test_get_new_identity_type_for_remove_for_user_assigned_1(self):
        exist_identity_type = ManagedIdentityType.USER_ASSIGNED
        is_remove_system_identity = True
        new_user_identities = []
        new_identity_type = _get_new_identity_type_for_remove(exist_identity_type,
                                                              is_remove_system_identity,
                                                              new_user_identities)
        self.assertEqual(new_identity_type, ManagedIdentityType.NONE)

    def test_get_new_identity_type_for_remove_for_user_assigned_2(self):
        exist_identity_type = ManagedIdentityType.USER_ASSIGNED
        is_remove_system_identity = False
        new_user_identities = []
        new_identity_type = _get_new_identity_type_for_remove(exist_identity_type,
                                                              is_remove_system_identity,
                                                              new_user_identities)
        self.assertEqual(new_identity_type, ManagedIdentityType.NONE)

    def test_get_new_identity_type_for_remove_for_user_assigned_3(self):
        exist_identity_type = ManagedIdentityType.USER_ASSIGNED
        is_remove_system_identity = None
        new_user_identities = []
        new_identity_type = _get_new_identity_type_for_remove(exist_identity_type,
                                                              is_remove_system_identity,
                                                              new_user_identities)
        self.assertEqual(new_identity_type, ManagedIdentityType.NONE)

    def test_get_new_identity_type_for_remove_for_user_assigned_4(self):
        exist_identity_type = ManagedIdentityType.USER_ASSIGNED
        is_remove_system_identity = True
        new_user_identities = ["ua1"]
        new_identity_type = _get_new_identity_type_for_remove(exist_identity_type,
                                                              is_remove_system_identity,
                                                              new_user_identities)
        self.assertEqual(new_identity_type, ManagedIdentityType.USER_ASSIGNED)

    def test_get_new_identity_type_for_remove_for_user_assigned_5(self):
        exist_identity_type = ManagedIdentityType.USER_ASSIGNED
        is_remove_system_identity = False
        new_user_identities = ["ua1"]
        new_identity_type = _get_new_identity_type_for_remove(exist_identity_type,
                                                              is_remove_system_identity,
                                                              new_user_identities)
        self.assertEqual(new_identity_type, ManagedIdentityType.USER_ASSIGNED)

    def test_get_new_identity_type_for_remove_for_user_assigned_6(self):
        exist_identity_type = ManagedIdentityType.USER_ASSIGNED
        is_remove_system_identity = None
        new_user_identities = ["ua1"]
        new_identity_type = _get_new_identity_type_for_remove(exist_identity_type,
                                                              is_remove_system_identity,
                                                              new_user_identities)
        self.assertEqual(new_identity_type, ManagedIdentityType.USER_ASSIGNED)


class TestAppManagedIdentityRemoveForTypeBothAssigned(unittest.TestCase):

    def test_get_new_identity_type_for_remove_for_both_assigned_1(self):
        exist_identity_type = ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED
        is_remove_system_identity = True
        new_user_identities = []
        new_identity_type = _get_new_identity_type_for_remove(exist_identity_type,
                                                              is_remove_system_identity,
                                                              new_user_identities)
        self.assertEqual(new_identity_type, ManagedIdentityType.NONE)

    def test_get_new_identity_type_for_remove_for_both_assigned_2(self):
        exist_identity_type = ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED
        is_remove_system_identity = False
        new_user_identities = []
        new_identity_type = _get_new_identity_type_for_remove(exist_identity_type,
                                                              is_remove_system_identity,
                                                              new_user_identities)
        self.assertEqual(new_identity_type, ManagedIdentityType.SYSTEM_ASSIGNED)

    def test_get_new_identity_type_for_remove_for_both_assigned_3(self):
        exist_identity_type = ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED
        is_remove_system_identity = None
        new_user_identities = []
        new_identity_type = _get_new_identity_type_for_remove(exist_identity_type,
                                                              is_remove_system_identity,
                                                              new_user_identities)
        self.assertEqual(new_identity_type, ManagedIdentityType.SYSTEM_ASSIGNED)

    def test_get_new_identity_type_for_remove_for_both_assigned_4(self):
        exist_identity_type = ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED
        is_remove_system_identity = True
        new_user_identities = ["ua1"]
        new_identity_type = _get_new_identity_type_for_remove(exist_identity_type,
                                                              is_remove_system_identity,
                                                              new_user_identities)
        self.assertEqual(new_identity_type, ManagedIdentityType.USER_ASSIGNED)

    def test_get_new_identity_type_for_remove_for_both_assigned_5(self):
        exist_identity_type = ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED
        is_remove_system_identity = False
        new_user_identities = ["ua1"]
        new_identity_type = _get_new_identity_type_for_remove(exist_identity_type,
                                                              is_remove_system_identity,
                                                              new_user_identities)
        self.assertEqual(new_identity_type, ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED)

    def test_get_new_identity_type_for_remove_for_both_assigned_6(self):
        exist_identity_type = ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED
        is_remove_system_identity = None
        new_user_identities = ["ua1"]
        new_identity_type = _get_new_identity_type_for_remove(exist_identity_type,
                                                              is_remove_system_identity,
                                                              new_user_identities)
        self.assertEqual(new_identity_type, ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED)
