# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Fabric v2 Service Peer prepare-attachment test scenario."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def call_scenario1(test):
    """Test preparing a Service Peer attachment."""
    step_prepare_attachment(
        test,
        checks=[
            test.check("localAsn", 65001),
            test.check("localIpv4Address", "10.0.0.1"),
            test.check("peerIpv4Address", "10.0.0.2"),
            test.check("prefixLength", 30),
        ],
    )


def step_prepare_attachment(test, checks=None):
    """Prepare a Service Peer attachment."""
    test.cmd(
        "az networkfabric fabric-v2 vrf servicepeer prepare-attachment "
        "--resource-group {rg} --fabric-v2 {fabricName} --vrf {vrfName} "
        "--resource-name {name} --consumer-resource-id {consumerResourceId} "
        "--request-generation {prepareRequestGeneration}",
        checks=checks or [],
    )


class FabricV2ServicePeerPrepareAttachmentScenarioTest(ScenarioTest):
    """Fabric v2 Service Peer prepare-attachment scenario test."""

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
                "prepareRequestGeneration": CONFIG.get(
                    "FABRIC_V2_SERVICE_PEER", "prepare_request_generation"
                ),
            }
        )

    def test_fabric_v2_servicepeer_prepare_attachment_scenario1(self):
        """Test the Service Peer prepare-attachment operation."""
        call_scenario1(self)
