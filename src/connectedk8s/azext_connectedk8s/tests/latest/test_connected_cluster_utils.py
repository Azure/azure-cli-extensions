# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import patch

from azure.cli.core.azclierror import ValidationError
from azure.cli.core.azclierror import AzureResponseError, ClientRequestError, AzureInternalError
from azure.cli.core.azclierror import ValidationError, AzureResponseError, ArgumentUsageError
from azure.core.exceptions import ResourceNotFoundError
from msrestazure.azure_exceptions import CloudError
from msrest.exceptions import ValidationError as MSRestValidationError
from msrest.exceptions import AuthenticationError, HttpOperationError, TokenExpiredError

import azext_connectedk8s._connected_cluster_utils as cc_utils

class ConnectedClusterUtilsTest(unittest.TestCase):

    class MockClient():

        class ResourceTypes():
            resource_type = None
            locations = None

            def set_resource_type(self, resource_type):
                self.resource_type = resource_type

            def set_locations(self, location):
                self.locations = location

        registration_state = None
        resource_types = []
        resource_type = ResourceTypes()

        def set_registration(self):
            self.registration_state = "Registered"

        def get(self, resouce_group_name, cluster):
            if resouce_group_name is None or cluster is None:
                raise ValidationError("Test error")
            return True

        def set_resource_type(self, rs_type):
            self.resource_type.set_resource_type(rs_type)
            self.resource_types.insert(0, self.resource_type)

        def set_location(self, location):
            self.resource_type.set_locations(location)
            self.resource_types.insert(0, self.resource_type)

    class ResourceClient():
        providers = None
        def set_providers(self, provider):
            self.providers = provider


    def test_check_provider_registrations(self):
        mock_kubernetes = self.MockClient()
        mock_kubernetes_configuration = self.MockClient()

        mock_rp_client = { 'Microsoft.Kubernetes' : mock_kubernetes,
                           'Microsoft.KubernetesConfiguration': mock_kubernetes_configuration}

        try:
            cc_utils.check_provider_registrations(mock_rp_client)
            self.fail("Exception should be raised")
        except ValidationError:
            pass

        mock_kubernetes.set_registration()

        mock_rp_client = { 'Microsoft.Kubernetes' : mock_kubernetes,
                           'Microsoft.KubernetesConfiguration': mock_kubernetes_configuration}

        try:
            cc_utils.check_provider_registrations(mock_rp_client)
        except ValidationError:
            self.fail("No exception only warning")

    def test_connected_cluster_exists(self):
        client = self.MockClient()

        try:
            cc_utils.connected_cluster_exists(client, None, None)
            self.fail("Exception should be raised")
        except Exception:
            pass

        try:
            cc_utils.connected_cluster_exists(client, "test_rg", "test_cluster")
        except Exception:
            self.fail("No exception should be raised")

    @patch('azext_connectedk8s._connected_cluster_utils.cf_resource_groups', return_value={"resource_group": "test_rg"})
    def test_resource_group_exists(self, input):
        self.assertTrue(cc_utils.resource_group_exists('ctx', "resource_group"))

    def test_arm_exception_handler(self):
        try:
            cc_utils.arm_exception_handler(AuthenticationError("test exception"), "dummy", "for unit testing")
            self.fail("Exception should be raised")
        except Exception:
            pass

        try:
            cc_utils.arm_exception_handler(TokenExpiredError("test exception"), "dummy", "for unit testing")
            self.fail("Exception should be raised")
        except Exception:
            pass

        try:
            cc_utils.arm_exception_handler(MSRestValidationError("test rule", "test target", "test value"),
                                           "dummy", "for unit testing")
            self.fail("Exception should be raised")
        except Exception:
            pass

        try:
            cc_utils.arm_exception_handler(ResourceNotFoundError("test exception"), "dummy", "for unit testing")
            self.fail("Exception should be raised")
        except Exception:
            pass

    def test_validate_location(self):
        mock_kubernetes = self.MockClient()
        mock_kubernetes.set_resource_type('connectedClusters')
        mock_kubernetes.set_location("test_location")
        mock_rp_client = { 'Microsoft.Kubernetes' : mock_kubernetes}
        resource_client = self.ResourceClient()
        resource_client.set_providers(mock_rp_client)

        try:
            cc_utils.validate_location("t", resource_client) 
        except Exception:
            self.fail("No exception should be raised")

        try:
            cc_utils.validate_location("test_", resource_client) 
            self.fail("Exception should be raised")
        except Exception:
            pass
