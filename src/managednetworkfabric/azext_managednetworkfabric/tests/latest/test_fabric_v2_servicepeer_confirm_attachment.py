# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Fabric v2 Service Peer confirm-attachment test scenario."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def call_scenario1(test):
    """Test confirming a Service Peer attachment."""
    step_confirm_attachment(
        test,
        checks=[test.check("requestId", "confirm-attachment-request")],
    )


def step_confirm_attachment(test, checks=None):
    """Confirm a Service Peer attachment."""
    test.cmd(
        "az networkfabric fabric-v2 vrf servicepeer confirm-attachment "
        "--resource-group {rg} --fabric-v2 {fabricName} --vrf {vrfName} "
        "--resource-name {name} --consumer-resource-id {consumerResourceId} "
        "--request-generation {confirmRequestGeneration} "
        "--spa-token {servicePeerAttachmentToken}",
        checks=checks or [],
    )


class FabricV2ServicePeerConfirmAttachmentScenarioTest(ScenarioTest):
    """Fabric v2 Service Peer confirm-attachment scenario test."""

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
                "confirmRequestGeneration": CONFIG.get(
                    "FABRIC_V2_SERVICE_PEER", "confirm_request_generation"
                ),
                "servicePeerAttachmentToken": CONFIG.get(
                    "FABRIC_V2_SERVICE_PEER", "service_peer_attachment_token"
                ),
            }
        )

    def test_fabric_v2_servicepeer_confirm_attachment_scenario1(self):
        """Test the Service Peer confirm-attachment operation."""
        call_scenario1(self)
