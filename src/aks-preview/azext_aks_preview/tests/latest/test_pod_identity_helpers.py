# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest

from azext_aks_preview.__init__ import register_aks_preview_resource_type
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview._podidentity import (
    _fill_defaults_for_pod_identity_exceptions,
    _fill_defaults_for_pod_identity_profile,
)
from azext_aks_preview.managed_cluster_decorator import (
    AKSPreviewManagedClusterModels,
)
from azext_aks_preview.tests.latest.mocks import MockCLI, MockCmd


class TestPodIdentityHelpers(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        # store all the models used by nat gateway
        self.pod_identity_models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW).pod_identity_models

    def test_fill_defaults_for_pod_identity_exceptions(self):
        # get models
        ManagedClusterPodIdentityException = self.pod_identity_models.ManagedClusterPodIdentityException

        # None value should not throw error
        _fill_defaults_for_pod_identity_exceptions(None)

        # Empty value should not throw error
        excs = []
        _fill_defaults_for_pod_identity_exceptions(excs)
        self.assertEqual(len(excs), 0)

        # Backfill pod labels
        excs = [
            ManagedClusterPodIdentityException(
                namespace="test-ns",
                name="test-exc-1",
                pod_labels=None,
            ),
            ManagedClusterPodIdentityException(
                namespace="test-ns",
                name="test-exc-2",
                pod_labels=None,
            ),
        ]
        _fill_defaults_for_pod_identity_exceptions(excs)
        self.assertEqual(len(excs), 2)
        self.assertEqual(excs[0].pod_labels, {})
        self.assertEqual(excs[0].name, "test-exc-1")
        self.assertEqual(excs[1].pod_labels, {})
        self.assertEqual(excs[1].name, "test-exc-2")

        # Backfill again
        _fill_defaults_for_pod_identity_exceptions(excs)
        self.assertEqual(len(excs), 2)
        self.assertEqual(excs[0].pod_labels, {})
        self.assertEqual(excs[0].name, "test-exc-1")
        self.assertEqual(excs[1].pod_labels, {})
        self.assertEqual(excs[1].name, "test-exc-2")

    def test_fill_defaults_for_pod_identity_profile(self):
        # get models
        ManagedClusterPodIdentityProfile = self.pod_identity_models.ManagedClusterPodIdentityProfile
        ManagedClusterPodIdentityException = self.pod_identity_models.ManagedClusterPodIdentityException

        # None value should not throw error
        _fill_defaults_for_pod_identity_profile(None)

        # Empty value should not throw error
        profile = ManagedClusterPodIdentityProfile()
        _fill_defaults_for_pod_identity_profile(profile)
        self.assertIsNone(profile.user_assigned_identity_exceptions)

        # Backfill pod labels
        profile = ManagedClusterPodIdentityProfile(
            user_assigned_identity_exceptions=[
                ManagedClusterPodIdentityException(
                    namespace="test-ns",
                    name="test-exc-1",
                    pod_labels=None,
                ),
                ManagedClusterPodIdentityException(
                    namespace="test-ns",
                    name="test-exc-2",
                    pod_labels=None,
                ),
            ]
        )
        _fill_defaults_for_pod_identity_profile(profile)
        excs = profile.user_assigned_identity_exceptions
        self.assertEqual(len(excs), 2)
        self.assertEqual(excs[0].pod_labels, {})
        self.assertEqual(excs[0].name, "test-exc-1")
        self.assertEqual(excs[1].pod_labels, {})
        self.assertEqual(excs[1].name, "test-exc-2")

        # Backfill again
        _fill_defaults_for_pod_identity_profile(profile)
        excs = profile.user_assigned_identity_exceptions
        self.assertEqual(len(excs), 2)
        self.assertEqual(excs[0].pod_labels, {})
        self.assertEqual(excs[0].name, "test-exc-1")
        self.assertEqual(excs[1].pod_labels, {})
        self.assertEqual(excs[1].name, "test-exc-2")


if __name__ == '__main__':
    unittest.main()
