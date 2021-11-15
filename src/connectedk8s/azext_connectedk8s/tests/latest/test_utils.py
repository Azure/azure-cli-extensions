# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
from unittest.mock import patch

import azext_connectedk8s._utils as utils

class UtilsTest(unittest.TestCase):

    def test_check_features_to_update(self):
        features_to_update = []
        self.assertEqual((False, False, False), utils.check_features_to_update(features_to_update))
        features_to_update.insert(0, 'cluster-connect')
        self.assertEqual((True, False, False), utils.check_features_to_update(features_to_update))
        features_to_update.insert(1, 'azure-rbac')
        self.assertEqual((True, True, False), utils.check_features_to_update(features_to_update))
        features_to_update.insert(2, 'custom-locations')
        self.assertEqual((True, True, True), utils.check_features_to_update(features_to_update))

    def test_user_confirmation_true(self):
        try:
            utils.user_confirmation("test message", True)
        except Exception:
            self.fail("No exception should have occured")

    @patch('azext_connectedk8s._utils.user_input', return_value=False)
    def test_user_confirmation_user_input_false(self, input):
        try:
            utils.user_confirmation("test message")
            self.fail("Exception should have occured")
        except Exception:
            return

    @patch('azext_connectedk8s._utils.user_input', return_value=True)
    def test_user_confirmation_user_input_true(self, input):
        try:
            utils.user_confirmation("test message")
        except Exception:
            self.fail("No exception should have occured")

    def test_is_guid(self):
        self.assertFalse(utils.is_guid("fake"))
        self.assertTrue(utils.is_guid("7cea1ec0-298e-11ec-9621-0242ac130002"))

    def test_generate_public_private_key(self):
        try:
            utils.generate_public_private_key()
        except Exception:
            self.fail("No exception should have occured")

    def test_get_values_file(self):
        file = "'testfile.json'"
        os.environ["HELMVALUESPATH"] = file
        f = open(file, "a")
        f.write("{\"key\":\"value\"}")
        f.close()
        self.assertEqual((True, 'testfile.json'), utils.get_values_file())

    def test_check_process(self):
        # check non existing process
        self.assertFalse(utils.check_process('test'))

    def test_check_if_port_is_open(self):
        # check non open port
        self.assertFalse(utils.check_if_port_is_open(12445))

    def test_generate_request_payload(self):
        location = "test_location"
        agent_public_key_certificate = "key"
        tags = "tag"
        distribution = "testDistro"
        infrastructure = "generic"
        cc = utils.generate_request_payload(location, agent_public_key_certificate, tags, distribution, infrastructure)

        self.assertEqual(location, cc.location)
        self.assertEqual(agent_public_key_certificate, cc.agent_public_key_certificate)
        self.assertEqual(tags, cc.tags)
        self.assertEqual(distribution, cc.distribution)
        self.assertEqual(infrastructure, cc.infrastructure)

        tags = None
        cc = utils.generate_request_payload(location, agent_public_key_certificate, tags, distribution, infrastructure)
        self.assertEqual({}, cc.tags)
