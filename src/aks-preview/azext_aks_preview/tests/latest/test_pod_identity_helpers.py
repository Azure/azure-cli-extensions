# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest

from azext_aks_preview.custom import (
    _fill_defaults_for_pod_identity_profile,
    _fill_defaults_for_pod_identity_exceptions,
    # we pin to the same version as custom.py
    ManagedClusterPodIdentityException,
    ManagedClusterPodIdentityProfile,
)


class TestPodIdentityHelpers(unittest.TestCase):
    def test_fill_defaults_for_pod_identity_exceptions(self):
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
