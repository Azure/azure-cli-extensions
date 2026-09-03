# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Fabric v2 Service Peer revoke test scenario."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def call_scenario1(test):
    """Test revoking a Service Peer attachment."""
    step_revoke(
        test,
        checks=[test.check("requestId", "revoke-attachment-request")],
    )


def step_revoke(test, checks=None):
    """Revoke a Service Peer attachment."""
    test.cmd(
        "az networkfabric fabric-v2 vrf servicepeer revoke "
        "--resource-group {rg} --fabric-v2 {fabricName} --vrf {vrfName} "
        "--resource-name {name} --consumer-resource-id {consumerResourceId} "
        "--request-generation {revokeRequestGeneration} --force {revokeForce} "
        "--reason {revokeReason}",
        checks=checks or [],
    )


class FabricV2ServicePeerRevokeScenarioTest(ScenarioTest):
    """Fabric v2 Service Peer revoke scenario test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("FABRIC_V2_SERVICE_PEER", "name"),
                "rg": CONFIG.get("FABRIC_V2_SERVICE_PEER", "resource_group"),
                "fabricName": CONFIG.get("FABRIC_V2_SERVICE_PEER", "fabric_name"),
                "vrfName": CONFIG.get("FABRIC_V2_SERVICE_PEER", "vrf_name"),
                "consumerResourceId": CONFIG.get(
                    "FABRIC_V2_SERVICE_PEER", "consumer_resource_id"
                ),
                "revokeRequestGeneration": CONFIG.get(
                    "FABRIC_V2_SERVICE_PEER", "revoke_request_generation"
                ),
                "revokeForce": CONFIG.get("FABRIC_V2_SERVICE_PEER", "revoke_force"),
                "revokeReason": CONFIG.get("FABRIC_V2_SERVICE_PEER", "revoke_reason"),
            }
        )

    def test_fabric_v2_servicepeer_revoke_scenario1(self):
        """Test the Service Peer revoke operation."""
        call_scenario1(self)
