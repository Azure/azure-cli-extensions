# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Fabric v2 VRF Network test scenarios."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG
from .utils.output_checks import attr


def call_scenario1(test):
    """Test the VRF Network CRUD lifecycle."""
    step_create_scenario1(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("description", attr(test, "description")),
            test.check("vlanResourceId", attr(test, "vlanResourceId")),
            test.check("connectedSubnets", attr(test, "connectedSubnets")),
            test.check("managementPolicy", attr(test, "managementPolicy")),
            test.check("mtu", int(attr(test, "mtu"))),
            test.check("userManagedConfig", attr(test, "userManagedConfig")),
            test.check("tags", attr(test, "tags")),
        ],
    )
    step_show(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("description", attr(test, "description")),
            test.check("vlanResourceId", attr(test, "vlanResourceId")),
            test.check("connectedSubnets", attr(test, "connectedSubnets")),
            test.check("managementPolicy", attr(test, "managementPolicy")),
            test.check("mtu", int(attr(test, "mtu"))),
            test.check("userManagedConfig", attr(test, "userManagedConfig")),
            test.check("tags", attr(test, "tags")),
        ],
    )
    step_update_scenario1(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("description", attr(test, "updatedDescription")),
            test.check("vlanResourceId", attr(test, "vlanResourceId")),
            test.check("connectedSubnets", attr(test, "connectedSubnets")),
            test.check("managementPolicy", attr(test, "updatedManagementPolicy")),
            test.check("mtu", int(attr(test, "updatedMtu"))),
            test.check("userManagedConfig", attr(test, "userManagedConfig")),
            test.check("tags", attr(test, "updatedTags")),
        ],
    )
    step_list(test, [test.check("[0].name", attr(test, "name"))])
    step_delete(test)
    test.assertTrue(test.cassette.all_played)


def call_scenario2(test):
    """Test VRF Network create and update parameter aliases."""
    step_create_scenario2(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("description", attr(test, "description")),
            test.check("vlanResourceId", attr(test, "vlanResourceId")),
            test.check("connectedSubnets", attr(test, "connectedSubnets")),
            test.check("managementPolicy", attr(test, "managementPolicy")),
            test.check("mtu", int(attr(test, "mtu"))),
            test.check("userManagedConfig", attr(test, "userManagedConfig")),
            test.check("tags", attr(test, "tags")),
        ],
    )
    step_update_scenario2(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("description", attr(test, "updatedDescription")),
            test.check("vlanResourceId", attr(test, "vlanResourceId")),
            test.check("connectedSubnets", attr(test, "connectedSubnets")),
            test.check("managementPolicy", attr(test, "updatedManagementPolicy")),
            test.check("mtu", int(attr(test, "updatedMtu"))),
            test.check("userManagedConfig", attr(test, "userManagedConfig")),
            test.check("tags", attr(test, "updatedTags")),
        ],
    )
    step_show_scenario2(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("description", attr(test, "updatedDescription")),
            test.check("vlanResourceId", attr(test, "vlanResourceId")),
            test.check("connectedSubnets", attr(test, "connectedSubnets")),
            test.check("managementPolicy", attr(test, "updatedManagementPolicy")),
            test.check("mtu", int(attr(test, "updatedMtu"))),
            test.check("userManagedConfig", attr(test, "userManagedConfig")),
            test.check("tags", attr(test, "updatedTags")),
        ],
    )
    step_list_scenario2(test)
    step_delete_scenario2(test)
    test.assertTrue(test.cassette.all_played)


def call_arista_cv_config_scenario(test):
    """Test VRF Network Arista CloudVision configuration."""
    step_create_arista_cv_config(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("managementPolicy", attr(test, "managementPolicy")),
            test.check("mtu", int(attr(test, "mtu"))),
            test.check(
                "aristaCloudVisionConfig", attr(test, "expectedAristaCloudVisionConfig")
            ),
        ],
    )
    step_update_arista_cv_config(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("managementPolicy", attr(test, "managementPolicy")),
            test.check("mtu", int(attr(test, "mtu"))),
            test.check(
                "aristaCloudVisionConfig", attr(test, "expectedAristaCloudVisionConfig")
            ),
        ],
    )
    step_delete(test)
    test.assertTrue(test.cassette.all_played)


def call_cisco_aci_config_scenario(test):
    """Test VRF Network Cisco ACI configuration."""
    step_create_cisco_aci_config(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("managementPolicy", attr(test, "managementPolicy")),
            test.check("mtu", int(attr(test, "mtu"))),
            test.check("ciscoAciConfig", attr(test, "expectedCiscoAciConfig")),
        ],
    )
    step_update_cisco_aci_config(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("managementPolicy", attr(test, "managementPolicy")),
            test.check("mtu", int(attr(test, "mtu"))),
            test.check("ciscoAciConfig", attr(test, "expectedCiscoAciConfig")),
        ],
    )
    step_delete(test)
    test.assertTrue(test.cassette.all_played)


def call_platform_managed_config_scenario(test):
    """Test VRF Network platform-managed configuration."""
    step_create_platform_managed_config(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("managementPolicy", attr(test, "managementPolicy")),
            test.check("mtu", int(attr(test, "mtu"))),
            test.check(
                "platformManagedConfig", attr(test, "expectedPlatformManagedConfig")
            ),
        ],
    )
    step_update_platform_managed_config(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("managementPolicy", attr(test, "managementPolicy")),
            test.check("mtu", int(attr(test, "mtu"))),
            test.check(
                "platformManagedConfig", attr(test, "expectedPlatformManagedConfig")
            ),
        ],
    )
    step_delete(test)
    test.assertTrue(test.cassette.all_played)


def step_create_scenario1(test, checks=None):
    """Create a VRF Network."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network create --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name} "
        "--location {location} --description {description} "
        "--vlan-resource-id {vlanResourceId} --connected-subnets {connectedSubnets} "
        "--management-policy {managementPolicy} --mtu {mtu} "
        "--user-managed-config {userManagedConfig} --tags {tags}",
        checks=checks or [],
    )


def step_create_scenario2(test, checks=None):
    """Create a VRF Network using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network create --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
        "--resource-name {name} --location {location} --desc {description} "
        "--vlan-id {vlanResourceId} --conn-subnets {connectedSubnets} "
        "--mgt-policy {managementPolicy} --mtu {mtu} "
        "--um-config {userManagedConfig} --tags {tags}",
        checks=checks or [],
    )


def step_show(test, checks=None):
    """Show a VRF Network."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network show --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name}",
        checks=checks or [],
    )


def step_show_scenario2(test, checks=None):
    """Show a VRF Network using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network show --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} --resource-name {name}",
        checks=checks or [],
    )


def step_update_scenario1(test, checks=None):
    """Update a VRF Network."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network update --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name} "
        "--description {updatedDescription} --vlan-resource-id {vlanResourceId} "
        "--connected-subnets {connectedSubnets} "
        "--management-policy {updatedManagementPolicy} --mtu {updatedMtu} "
        "--user-managed-config {userManagedConfig} --tags {updatedTags}",
        checks=checks or [],
    )


def step_update_scenario2(test, checks=None):
    """Update a VRF Network using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network update --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
        "--resource-name {name} --desc {updatedDescription} "
        "--vlan-id {vlanResourceId} --conn-subnets {connectedSubnets} "
        "--mgt-policy {updatedManagementPolicy} --mtu {updatedMtu} "
        "--um-config {userManagedConfig} "
        "--tags {updatedTags}",
        checks=checks or [],
    )


def step_create_arista_cv_config(test, checks=None):
    """Create a VRF Network with Arista CloudVision configuration."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network create --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
        "--resource-name {name} --location {location} "
        "--arista-cv-config device-query={aristaDeviceQuery} "
        "configlet-name={aristaConfigletName} "
        "egress-acl-resource-id={aristaEgressAclResourceId} "
        "export-route-policy={aristaExportRoutePolicy} "
        "import-route-policy={aristaImportRoutePolicy} "
        "ingress-acl-resource-id={aristaIngressAclResourceId} "
        "bgp-configuration={aristaBgpConfiguration} "
        "static-route-configuration={aristaStaticRouteConfiguration}",
        checks=checks or [],
    )


def step_update_arista_cv_config(test, checks=None):
    """Update a VRF Network with Arista CloudVision configuration."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network update --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
        "--resource-name {name} "
        "--arista-cv-config device-query={aristaDeviceQuery} "
        "configlet-name={aristaConfigletName} "
        "egress-acl-resource-id={aristaEgressAclResourceId} "
        "export-route-policy={aristaExportRoutePolicy} "
        "import-route-policy={aristaImportRoutePolicy} "
        "ingress-acl-resource-id={aristaIngressAclResourceId} "
        "bgp-configuration={aristaBgpConfiguration} "
        "static-route-configuration={aristaStaticRouteConfiguration}",
        checks=checks or [],
    )


def step_create_cisco_aci_config(test, checks=None):
    """Create a VRF Network with Cisco ACI configuration."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network create --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
        "--resource-name {name} --location {location} "
        "--cisco-aci-config bridge-domain-name={ciscoBridgeDomainName} "
        "consumed-contracts={ciscoConsumedContracts} epg-name={ciscoEpgName} "
        "provided-contracts={ciscoProvidedContracts} vrf-name={ciscoVrfName}",
        checks=checks or [],
    )


def step_update_cisco_aci_config(test, checks=None):
    """Update a VRF Network with Cisco ACI configuration."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network update --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
        "--resource-name {name} "
        "--cisco-aci-config bridge-domain-name={ciscoBridgeDomainName} "
        "consumed-contracts={ciscoConsumedContracts} epg-name={ciscoEpgName} "
        "provided-contracts={ciscoProvidedContracts} vrf-name={ciscoVrfName}",
        checks=checks or [],
    )


def step_create_platform_managed_config(test, checks=None):
    """Create a VRF Network with platform-managed configuration."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network create --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
        "--resource-name {name} --location {location} "
        "--platform-managed-config bgp-configuration={platformBgpConfiguration} "
        "egress-acl-resource-id={platformEgressAclResourceId} "
        "export-route-policy={platformExportRoutePolicy} "
        "import-route-policy={platformImportRoutePolicy} "
        "ingress-acl-resource-id={platformIngressAclResourceId} "
        "static-route-configuration={platformStaticRouteConfiguration}",
        checks=checks or [],
    )


def step_update_platform_managed_config(test, checks=None):
    """Update a VRF Network with platform-managed configuration."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network update --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
        "--resource-name {name} "
        "--platform-managed-config bgp-configuration={platformBgpConfiguration} "
        "egress-acl-resource-id={platformEgressAclResourceId} "
        "export-route-policy={platformExportRoutePolicy} "
        "import-route-policy={platformImportRoutePolicy} "
        "ingress-acl-resource-id={platformIngressAclResourceId} "
        "static-route-configuration={platformStaticRouteConfiguration}",
        checks=checks or [],
    )


def step_list(test, checks=None):
    """List VRF Networks by VRF."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network list --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName}",
        checks=checks or [],
    )


def step_list_scenario2(test, checks=None):
    """List VRF Networks by VRF using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network list --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName}",
        checks=checks or [],
    )


def step_delete(test, checks=None):
    """Delete a VRF Network."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network delete --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name}",
        checks=checks or [],
    )


def step_delete_scenario2(test, checks=None):
    """Delete a VRF Network using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network delete --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} --resource-name {name}",
        checks=checks or [],
    )


class FabricV2VrfNetworkScenarioTest(ScenarioTest):
    """Fabric v2 VRF Network scenario test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("FABRIC_V2_VRF_NETWORK", "name"),
                "rg": CONFIG.get("FABRIC_V2_VRF_NETWORK", "resource_group"),
                "fabricName": CONFIG.get("FABRIC_V2_VRF_NETWORK", "fabric_name"),
                "vrfName": CONFIG.get("FABRIC_V2_VRF_NETWORK", "vrf_name"),
                "location": CONFIG.get("FABRIC_V2_VRF_NETWORK", "location"),
                "description": CONFIG.get("FABRIC_V2_VRF_NETWORK", "description"),
                "updatedDescription": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "updated_description"
                ),
                "vlanResourceId": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "vlan_resource_id"
                ),
                "connectedSubnets": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "connected_subnets"
                ),
                "managementPolicy": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "management_policy"
                ),
                "updatedManagementPolicy": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "updated_management_policy"
                ),
                "mtu": CONFIG.get("FABRIC_V2_VRF_NETWORK", "mtu"),
                "updatedMtu": CONFIG.get("FABRIC_V2_VRF_NETWORK", "updated_mtu"),
                "aristaDeviceQuery": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "arista_device_query"
                ),
                "aristaConfigletName": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "arista_configlet_name"
                ),
                "aristaEgressAclResourceId": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "arista_egress_acl_resource_id"
                ),
                "aristaExportRoutePolicy": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "arista_export_route_policy"
                ),
                "aristaImportRoutePolicy": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "arista_import_route_policy"
                ),
                "aristaIngressAclResourceId": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "arista_ingress_acl_resource_id"
                ),
                "aristaBgpConfiguration": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "arista_bgp_configuration"
                ),
                "aristaStaticRouteConfiguration": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "arista_static_route_configuration"
                ),
                "ciscoBridgeDomainName": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "cisco_bridge_domain_name"
                ),
                "ciscoConsumedContracts": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "cisco_consumed_contracts"
                ),
                "ciscoEpgName": CONFIG.get("FABRIC_V2_VRF_NETWORK", "cisco_epg_name"),
                "ciscoProvidedContracts": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "cisco_provided_contracts"
                ),
                "ciscoVrfName": CONFIG.get("FABRIC_V2_VRF_NETWORK", "cisco_vrf_name"),
                "platformBgpConfiguration": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "platform_bgp_configuration"
                ),
                "platformEgressAclResourceId": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "platform_egress_acl_resource_id"
                ),
                "platformExportRoutePolicy": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "platform_export_route_policy"
                ),
                "platformImportRoutePolicy": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "platform_import_route_policy"
                ),
                "platformIngressAclResourceId": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "platform_ingress_acl_resource_id"
                ),
                "platformStaticRouteConfiguration": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "platform_static_route_configuration"
                ),
                "userManagedConfig": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "user_managed_config"
                ),
                "tags": CONFIG.get("FABRIC_V2_VRF_NETWORK", "tags"),
                "updatedTags": CONFIG.get("FABRIC_V2_VRF_NETWORK", "updated_tags"),
                "expectedAristaCloudVisionConfig": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "expected_arista_cloud_vision_config"
                ),
                "expectedCiscoAciConfig": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "expected_cisco_aci_config"
                ),
                "expectedPlatformManagedConfig": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "expected_platform_managed_config"
                ),
                "expectedProvisioningState": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "expected_provisioning_state"
                ),
            }
        )
        self.vcr.match_on = (*self.vcr.match_on, "body")

    def test_GA_fabric_v2_vrf_network_scenario1(self):
        """Test Fabric v2 VRF Network CRUD operations."""
        call_scenario1(self)

    def test_GA_fabric_v2_vrf_network_scenario2(self):
        """Test Fabric v2 VRF Network CRUD operations with parameter aliases."""
        call_scenario2(self)

    def test_GA_fabric_v2_vrf_network_arista_cv_config(self):
        """Test Fabric v2 VRF Network Arista CloudVision configuration."""
        call_arista_cv_config_scenario(self)

    def test_GA_fabric_v2_vrf_network_cisco_aci_config(self):
        """Test Fabric v2 VRF Network Cisco ACI configuration."""
        call_cisco_aci_config_scenario(self)

    def test_GA_fabric_v2_vrf_network_platform_managed_config(self):
        """Test Fabric v2 VRF Network platform-managed configuration."""
        call_platform_managed_config_scenario(self)
