# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from unittest.mock import patch
from azure.cli.core.azclierror import  ArgumentUsageError

import azext_connectedk8s._custom_location_utils as cl_utils

class A:
    cli_ctx = ""
cmd = A()

class CustomLocationUtilsTest(unittest.TestCase):

    class MockRPClient():

        class Registration():
            registration_state = None
            def set_registration(self, str):
                self.registration_state = str

        registration = Registration()
        registration.set_registration("Registered")

        def get(self, str):
            return self.registration

        def set_registration(self, str):
            self.registration.set_registration(str)
            return self

    class ClientServicePrincipals:
        class temp:
            displayName = "Custom Locations RP"
            object_id =1

        def set_display_name(self, str):
            self.displayName = str

        def list(self, filter=None, custom_headers=None, raw=False, **operation_config):
            return [self.temp(), self.temp()]

    @patch.object(cl_utils, 'get_graph_client_service_principals', return_value=ClientServicePrincipals())
    def test_get_custom_locations_oid(self, input):
        self.assertEqual(1, cl_utils.get_custom_locations_oid(cmd, 2))
        self.assertEqual(1, cl_utils.get_custom_locations_oid(cmd, None))

#    @patch.object(cl_utils, 'get_graph_client_service_principals', return_value=ClientServicePrincipals().set_display_name("test"))
#    def test_get_custom_locations_oid_wrong_display_name(self, input):
#        self.assertEqual(2, cl_utils.get_custom_locations_oid(cmd, 2))
#        self.assertEqual('', cl_utils.get_custom_locations_oid(cmd, None))

    @patch.object(cl_utils, 'get_graph_client_service_principals', return_value=ArgumentUsageError("test"))
    def test_get_custom_locations_oid_exception(self, input):
        self.assertEqual(1, cl_utils.get_custom_locations_oid(cmd, 1))
        self.assertEqual('', cl_utils.get_custom_locations_oid(cmd, None))

    @patch.object(cl_utils, '_resource_providers_client', return_value=ArgumentUsageError("test"))
    @patch.object(cl_utils, 'get_custom_locations_oid', return_value=1)
    def test_check_cl_registration_and_get_oid_exception(self, input, input1):
        self.assertEqual((False, ""), cl_utils.check_cl_registration_and_get_oid(cmd, 1))

    @patch.object(cl_utils, 'get_custom_locations_oid', return_value=2)
    def test_check_cl_registration_and_get_oid(self, input):
        with patch.object(cl_utils, '_resource_providers_client', return_value=self.MockRPClient()):
            self.assertEqual((True, 2), cl_utils.check_cl_registration_and_get_oid(cmd, 1))

    @patch.object(cl_utils, 'get_custom_locations_oid', return_value='')
    def test_check_cl_registration_and_get_oid_null(self, input):
        with patch.object(cl_utils, '_resource_providers_client', return_value=self.MockRPClient().set_registration("Registered")):
            self.assertEqual((False, ""), cl_utils.check_cl_registration_and_get_oid(cmd, 1))

    @patch.object(cl_utils, 'get_custom_locations_oid', return_value='')
    def test_check_cl_registration_and_get_oid_not_registered(self, input):
        with patch.object(cl_utils, '_resource_providers_client', return_value=self.MockRPClient().set_registration("NotRegistered")):
            self.assertEqual((False, ""), cl_utils.check_cl_registration_and_get_oid(cmd, 1))
