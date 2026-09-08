# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from azext_fleet.custom import _build_propagation_policy
from azext_fleet.vendored_sdks.v2026_06_02_preview.models import (
    PlacementProfile,
    PlacementProfilePatch,
    PlacementV1ClusterResourcePlacementSpec,
    PlacementV1ClusterResourcePlacementSpecPatch,
    PlacementV1PlacementPolicy,
    PlacementV1PlacementPolicyPatch,
    PropagationPolicy,
    PropagationPolicyPatch,
)


class TestManagedNamespaceModels(unittest.TestCase):
    """Verify create and update commands use their corresponding generated model graphs."""

    def test_create_uses_resource_models(self):
        """Create payloads use the normal resource models."""
        policy = _build_propagation_policy(["member-1"])

        self.assertIsInstance(policy, PropagationPolicy)
        self.assertIsInstance(policy.placement_profile, PlacementProfile)
        placement = policy.placement_profile.default_cluster_resource_placement
        self.assertIsInstance(placement, PlacementV1ClusterResourcePlacementSpec)
        self.assertIsInstance(placement.policy, PlacementV1PlacementPolicy)
        self.assertEqual(placement.policy.cluster_names, ["member-1"])
        self.assertEqual(policy.serialize(), {
            "type": "Placement",
            "placementProfile": {
                "defaultClusterResourcePlacement": {
                    "policy": {
                        "placementType": "PickFixed",
                        "clusterNames": ["member-1"],
                    },
                },
            },
        })

    def test_update_uses_patch_models(self):
        """Update payloads use PATCH models without changing the wire shape."""
        policy = _build_propagation_policy(["member-1"], patch=True)

        self.assertIsInstance(policy, PropagationPolicyPatch)
        self.assertIsInstance(policy.placement_profile, PlacementProfilePatch)
        placement = policy.placement_profile.default_cluster_resource_placement
        self.assertIsInstance(placement, PlacementV1ClusterResourcePlacementSpecPatch)
        self.assertIsInstance(placement.policy, PlacementV1PlacementPolicyPatch)
        self.assertEqual(placement.policy.cluster_names, ["member-1"])
        self.assertEqual(policy.serialize(), {
            "type": "Placement",
            "placementProfile": {
                "defaultClusterResourcePlacement": {
                    "policy": {
                        "placementType": "PickFixed",
                        "clusterNames": ["member-1"],
                    },
                },
            },
        })


if __name__ == "__main__":
    unittest.main()