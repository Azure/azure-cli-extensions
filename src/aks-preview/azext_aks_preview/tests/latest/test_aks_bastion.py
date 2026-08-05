# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from azext_aks_preview.bastion.bastion import (
    BastionResource,
    _aks_bastion_launch_tunnel,
    aks_bastion_parse_bastion_resource,
)


class TestAksBastionParseResource(unittest.TestCase):
    def test_cross_subscription_resource_id_preserves_bastion_subscription(self):
        # the bastion lives in a different (hub) subscription than the cluster
        bastion_id = (
            "/subscriptions/hub-sub-id/resourceGroups/bastion-rg/"
            "providers/Microsoft.Network/bastionHosts/my-bastion"
        )
        resource = aks_bastion_parse_bastion_resource(
            bastion_id, ["node-rg"], subscription_id="aks-sub-id"
        )
        self.assertEqual(resource.name, "my-bastion")
        self.assertEqual(resource.resource_group, "bastion-rg")
        # the subscription from the bastion resource ID must win over the cluster subscription
        self.assertEqual(resource.subscription, "hub-sub-id")

    def test_resource_id_without_subscription_falls_back_to_cluster_subscription(self):
        # parse_resource_id may not yield a subscription; fall back to the cluster one
        bastion_id = (
            "/subscriptions/hub-sub-id/resourceGroups/bastion-rg/"
            "providers/Microsoft.Network/bastionHosts/my-bastion"
        )
        with patch(
            "azext_aks_preview.bastion.bastion.parse_resource_id",
            return_value={"name": "my-bastion", "resource_group": "bastion-rg"},
        ):
            resource = aks_bastion_parse_bastion_resource(
                bastion_id,
                ["node-rg"],
                subscription_id="aks-sub-id",
            )
        self.assertEqual(resource.subscription, "aks-sub-id")


class TestAksBastionLaunchTunnel(unittest.IsolatedAsyncioTestCase):
    async def test_tunnel_uses_bastion_subscription(self):
        # regression guard: the inner `az network bastion tunnel` must be scoped to the
        # bastion's subscription, not the cluster subscription (see azure-cli#33579)
        bastion_resource = BastionResource(
            name="my-bastion",
            resource_group="bastion-rg",
            subscription="hub-sub-id",
        )
        mock_process = MagicMock()
        mock_process.wait = AsyncMock(return_value=0)
        mock_process.returncode = 0

        with patch(
            "azext_aks_preview.bastion.bastion.asyncio.create_subprocess_exec",
            new=AsyncMock(return_value=mock_process),
        ) as mock_exec:
            await _aks_bastion_launch_tunnel(
                bastion_resource,
                port=12345,
                mc_id="/subscriptions/aks-sub-id/resourceGroups/aks-rg/"
                "providers/Microsoft.ContainerService/managedClusters/cluster",
                subscription_id="aks-sub-id",
            )

        args = mock_exec.call_args.args
        self.assertIn("--subscription", args)
        sub_index = args.index("--subscription")
        self.assertEqual(args[sub_index + 1], "hub-sub-id")
        self.assertNotIn("aks-sub-id", args[sub_index + 1])

    async def test_tunnel_falls_back_to_cluster_subscription(self):
        # when the bastion has no subscription of its own (name-based discovery in the
        # node resource group), the cluster subscription is used
        bastion_resource = BastionResource(
            name="my-bastion",
            resource_group="node-rg",
            subscription=None,
        )
        mock_process = MagicMock()
        mock_process.wait = AsyncMock(return_value=0)
        mock_process.returncode = 0

        with patch(
            "azext_aks_preview.bastion.bastion.asyncio.create_subprocess_exec",
            new=AsyncMock(return_value=mock_process),
        ) as mock_exec:
            await _aks_bastion_launch_tunnel(
                bastion_resource,
                port=12345,
                mc_id="/subscriptions/aks-sub-id/resourceGroups/aks-rg/"
                "providers/Microsoft.ContainerService/managedClusters/cluster",
                subscription_id="aks-sub-id",
            )

        args = mock_exec.call_args.args
        self.assertIn("--subscription", args)
        sub_index = args.index("--subscription")
        self.assertEqual(args[sub_index + 1], "aks-sub-id")


if __name__ == "__main__":
    unittest.main()
