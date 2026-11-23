# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

# """Fabric v2 VRF Peering test scenarios."""

# from azure.cli.testsdk import ScenarioTest

# from .config import CONFIG


# def call_scenario1(test):
#     """Test the VRF Peering CRUD lifecycle."""
#     step_create_scenario1(
#         test,
#         [
#             test.check("name", test.kwargs["name"].strip('"')),
#             test.check("peerAsn", int(test.kwargs["peerAsn"].strip('"'))),
#         ],
#     )
#     step_show(test, [test.check("name", test.kwargs["name"].strip('"'))])
#     step_update_scenario1(
#         test,
#         [test.check("description", test.kwargs["updatedDescription"].strip('"'))],
#     )
#     step_list(test, [test.check("[0].name", test.kwargs["name"].strip('"'))])
#     step_delete(test)


# def call_scenario2(test):
#     """Test VRF Peering create and update parameter aliases."""
#     step_create_scenario2(test)
#     step_update_scenario2(
#         test,
#         [test.check("description", test.kwargs["updatedDescription"].strip('"'))],
#     )
#     step_show_scenario2(test)
#     step_list_scenario2(test)
#     step_delete_scenario2(test)


# def call_arista_cv_config_scenario(test):
#     """Test VRF Peering Arista CloudVision configuration."""
#     step_create_arista_cv_config(test)
#     step_update_arista_cv_config(test)
#     step_delete(test)


# def call_cisco_aci_config_scenario(test):
#     """Test VRF Peering Cisco ACI configuration."""
#     step_create_cisco_aci_config(test)
#     step_update_cisco_aci_config(test)
#     step_delete(test)


# def call_platform_managed_config_scenario(test):
#     """Test VRF Peering platform-managed configuration."""
#     step_create_platform_managed_config(test)
#     step_update_platform_managed_config(test)
#     step_delete(test)


# def step_create_scenario1(test, checks=None):
#     """Create a VRF Peering."""
#     test.cmd(
#         "az networkfabric fabric-v2 vrf peering create --resource-group {rg} "
#         "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name} "
#         "--location {location} --description {description} --peer-asn {peerAsn} "
#         "--bfd-enabled {bfdEnabled} --primary-ipv4-prefix {primaryIpv4Prefix} "
#         "--primary-ipv6-prefix {primaryIpv6Prefix} "
#         "--secondary-ipv4-prefix {secondaryIpv4Prefix} "
#         "--secondary-ipv6-prefix {secondaryIpv6Prefix} "
#         "--management-policy {managementPolicy} "
#         "--tags {tags}",
#         checks=checks or [],
#     )


# def step_create_scenario2(test, checks=None):
#     """Create a VRF Peering using parameter aliases."""
#     test.cmd(
#         "az networkfabric fabric-v2 vrf peering create --resource-group {rg} "
#         "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
#         "--resource-name {name} --location {location} --desc {description} "
#         "--peer-asn {peerAsn} --bfd-enabled {bfdEnabled} "
#         "--primary-ipv4-prefix {primaryIpv4Prefix} "
#         "--primary-ipv6-prefix {primaryIpv6Prefix} "
#         "--secondary-ipv4-prefix {secondaryIpv4Prefix} "
#         "--secondary-ipv6-prefix {secondaryIpv6Prefix} "
#         "--mgt-policy {managementPolicy} --tags {tags}",
#         checks=checks or [],
#     )


# def step_show(test, checks=None):
#     """Show a VRF Peering."""
#     test.cmd(
#         "az networkfabric fabric-v2 vrf peering show --resource-group {rg} "
#         "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name}",
#         checks=checks or [],
#     )


# def step_show_scenario2(test, checks=None):
#     """Show a VRF Peering using parameter aliases."""
#     test.cmd(
#         "az networkfabric fabric-v2 vrf peering show --resource-group {rg} "
#         "--fabric-v2-name {fabricName} --vrf-name {vrfName} --resource-name {name}",
#         checks=checks or [],
#     )


# def step_update_scenario1(test, checks=None):
#     """Update a VRF Peering."""
#     test.cmd(
#         "az networkfabric fabric-v2 vrf peering update --resource-group {rg} "
#         "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name} "
#         "--description {updatedDescription} --peer-asn {peerAsn} "
#         "--bfd-enabled {updatedBfdEnabled} "
#         "--primary-ipv4-prefix {primaryIpv4Prefix} "
#         "--primary-ipv6-prefix {primaryIpv6Prefix} "
#         "--secondary-ipv4-prefix {secondaryIpv4Prefix} "
#         "--secondary-ipv6-prefix {secondaryIpv6Prefix} "
#         "--management-policy {updatedManagementPolicy} "
#         "--tags {updatedTags}",
#         checks=checks or [],
#     )


# def step_update_scenario2(test, checks=None):
#     """Update a VRF Peering using parameter aliases."""
#     test.cmd(
#         "az networkfabric fabric-v2 vrf peering update --resource-group {rg} "
#         "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
#         "--resource-name {name} --desc {updatedDescription} "
#         "--peer-asn {peerAsn} --bfd-enabled {updatedBfdEnabled} "
#         "--primary-ipv4-prefix {primaryIpv4Prefix} "
#         "--primary-ipv6-prefix {primaryIpv6Prefix} "
#         "--secondary-ipv4-prefix {secondaryIpv4Prefix} "
#         "--secondary-ipv6-prefix {secondaryIpv6Prefix} "
#         "--mgt-policy {updatedManagementPolicy} --tags {updatedTags}",
#         checks=checks or [],
#     )


# def step_create_arista_cv_config(test, checks=None):
#     """Create a VRF Peering with Arista CloudVision configuration."""
#     test.cmd(
#         "az networkfabric fabric-v2 vrf peering create --resource-group {rg} "
#         "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
#         "--resource-name {name} --location {location} "
#         "--arista-cv-config device-query={aristaDeviceQuery} "
#         "configlet-name={aristaConfigletName} "
#         "egress-acl-resource-id={aristaEgressAclResourceId} "
#         "export-route-policy={aristaExportRoutePolicy} "
#         "import-route-policy={aristaImportRoutePolicy} "
#         "ingress-acl-resource-id={aristaIngressAclResourceId} "
#         "labeled-vpn-config={aristaLabeledVpnConfig} "
#         "multihop-labeled-vpn-config={aristaMultihopLabeledVpnConfig} "
#         "peering-kind={aristaPeeringKind} "
#         "static-route-configuration={aristaStaticRouteConfiguration} "
#         "uplink-resource-id={aristaUplinkResourceId} "
#         "vrf-to-vrf-config={aristaVrfToVrfConfig}",
#         checks=checks or [],
#     )


# def step_update_arista_cv_config(test, checks=None):
#     """Update a VRF Peering with Arista CloudVision configuration."""
#     test.cmd(
#         "az networkfabric fabric-v2 vrf peering update --resource-group {rg} "
#         "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
#         "--resource-name {name} "
#         "--arista-cv-config device-query={aristaDeviceQuery} "
#         "configlet-name={aristaConfigletName} "
#         "egress-acl-resource-id={aristaEgressAclResourceId} "
#         "export-route-policy={aristaExportRoutePolicy} "
#         "import-route-policy={aristaImportRoutePolicy} "
#         "ingress-acl-resource-id={aristaIngressAclResourceId} "
#         "labeled-vpn-config={aristaLabeledVpnConfig} "
#         "multihop-labeled-vpn-config={aristaMultihopLabeledVpnConfig} "
#         "peering-kind={aristaPeeringKind} "
#         "static-route-configuration={aristaStaticRouteConfiguration} "
#         "uplink-resource-id={aristaUplinkResourceId} "
#         "vrf-to-vrf-config={aristaVrfToVrfConfig}",
#         checks=checks or [],
#     )


# def step_create_cisco_aci_config(test, checks=None):
#     """Create a VRF Peering with Cisco ACI configuration."""
#     test.cmd(
#         "az networkfabric fabric-v2 vrf peering create --resource-group {rg} "
#         "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
#         "--resource-name {name} --location {location} "
#         "--cisco-aci-config external-epg-name={ciscoExternalEpgName} "
#         "l3out-name={ciscoL3outName} "
#         "provided-contract-names={ciscoProvidedContractNames}",
#         checks=checks or [],
#     )


# def step_update_cisco_aci_config(test, checks=None):
#     """Update a VRF Peering with Cisco ACI configuration."""
#     test.cmd(
#         "az networkfabric fabric-v2 vrf peering update --resource-group {rg} "
#         "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
#         "--resource-name {name} "
#         "--cisco-aci-config external-epg-name={ciscoExternalEpgName} "
#         "l3out-name={ciscoL3outName} "
#         "provided-contract-names={ciscoProvidedContractNames}",
#         checks=checks or [],
#     )


# def step_create_platform_managed_config(test, checks=None):
#     """Create a VRF Peering with platform-managed configuration."""
#     test.cmd(
#         "az networkfabric fabric-v2 vrf peering create --resource-group {rg} "
#         "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
#         "--resource-name {name} --location {location} "
#         "--platform-managed-config "
#         "egress-acl-resource-id={platformEgressAclResourceId} "
#         "export-route-policy={platformExportRoutePolicy} "
#         "import-route-policy={platformImportRoutePolicy} "
#         "ingress-acl-resource-id={platformIngressAclResourceId} "
#         "labeled-vpn-config={platformLabeledVpnConfig} "
#         "multihop-labeled-vpn-config={platformMultihopLabeledVpnConfig} "
#         "peering-kind={platformPeeringKind} "
#         "static-route-configuration={platformStaticRouteConfiguration} "
#         "uplink-resource-id={platformUplinkResourceId} "
#         "vrf-to-vrf-config={platformVrfToVrfConfig}",
#         checks=checks or [],
#     )


# def step_update_platform_managed_config(test, checks=None):
#     """Update a VRF Peering with platform-managed configuration."""
#     test.cmd(
#         "az networkfabric fabric-v2 vrf peering update --resource-group {rg} "
#         "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
#         "--resource-name {name} "
#         "--platform-managed-config "
#         "egress-acl-resource-id={platformEgressAclResourceId} "
#         "export-route-policy={platformExportRoutePolicy} "
#         "import-route-policy={platformImportRoutePolicy} "
#         "ingress-acl-resource-id={platformIngressAclResourceId} "
#         "labeled-vpn-config={platformLabeledVpnConfig} "
#         "multihop-labeled-vpn-config={platformMultihopLabeledVpnConfig} "
#         "peering-kind={platformPeeringKind} "
#         "static-route-configuration={platformStaticRouteConfiguration} "
#         "uplink-resource-id={platformUplinkResourceId} "
#         "vrf-to-vrf-config={platformVrfToVrfConfig}",
#         checks=checks or [],
#     )


# def step_list(test, checks=None):
#     """List VRF Peerings by VRF."""
#     test.cmd(
#         "az networkfabric fabric-v2 vrf peering list --resource-group {rg} "
#         "--fabric-v2 {fabricName} --vrf {vrfName}",
#         checks=checks or [],
#     )


# def step_list_scenario2(test, checks=None):
#     """List VRF Peerings by VRF using parameter aliases."""
#     test.cmd(
#         "az networkfabric fabric-v2 vrf peering list --resource-group {rg} "
#         "--fabric-v2-name {fabricName} --vrf-name {vrfName}",
#         checks=checks or [],
#     )


# def step_delete(test, checks=None):
#     """Delete a VRF Peering."""
#     test.cmd(
#         "az networkfabric fabric-v2 vrf peering delete --resource-group {rg} "
#         "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name}",
#         checks=checks or [],
#     )


# def step_delete_scenario2(test, checks=None):
#     """Delete a VRF Peering using parameter aliases."""
#     test.cmd(
#         "az networkfabric fabric-v2 vrf peering delete --resource-group {rg} "
#         "--fabric-v2-name {fabricName} --vrf-name {vrfName} --resource-name {name}",
#         checks=checks or [],
#     )


# class FabricV2VrfPeeringScenarioTest(ScenarioTest):
#     """Fabric v2 VRF Peering scenario test."""

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.kwargs.update(
#             {
#                 "name": CONFIG.get("FABRIC_V2_VRF_PEERING", "name"),
#                 "rg": CONFIG.get("FABRIC_V2_VRF_PEERING", "resource_group"),
#                 "fabricName": CONFIG.get("FABRIC_V2_VRF_PEERING", "fabric_name"),
#                 "vrfName": CONFIG.get("FABRIC_V2_VRF_PEERING", "vrf_name"),
#                 "location": CONFIG.get("FABRIC_V2_VRF_PEERING", "location"),
#                 "description": CONFIG.get("FABRIC_V2_VRF_PEERING", "description"),
#                 "updatedDescription": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "updated_description"
#                 ),
#                 "bfdEnabled": CONFIG.get("FABRIC_V2_VRF_PEERING", "bfd_enabled"),
#                 "updatedBfdEnabled": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "updated_bfd_enabled"
#                 ),
#                 "peerAsn": CONFIG.get("FABRIC_V2_VRF_PEERING", "peer_asn"),
#                 "managementPolicy": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "management_policy"
#                 ),
#                 "updatedManagementPolicy": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "updated_management_policy"
#                 ),
#                 "primaryIpv4Prefix": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "primary_ipv4_prefix"
#                 ),
#                 "primaryIpv6Prefix": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "primary_ipv6_prefix"
#                 ),
#                 "secondaryIpv4Prefix": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "secondary_ipv4_prefix"
#                 ),
#                 "secondaryIpv6Prefix": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "secondary_ipv6_prefix"
#                 ),
#                 "aristaDeviceQuery": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "arista_device_query"
#                 ),
#                 "aristaConfigletName": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "arista_configlet_name"
#                 ),
#                 "aristaEgressAclResourceId": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "arista_egress_acl_resource_id"
#                 ),
#                 "aristaExportRoutePolicy": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "arista_export_route_policy"
#                 ),
#                 "aristaImportRoutePolicy": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "arista_import_route_policy"
#                 ),
#                 "aristaIngressAclResourceId": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "arista_ingress_acl_resource_id"
#                 ),
#                 "aristaLabeledVpnConfig": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "arista_labeled_vpn_config"
#                 ),
#                 "aristaMultihopLabeledVpnConfig": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "arista_multihop_labeled_vpn_config"
#                 ),
#                 "aristaPeeringKind": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "arista_peering_kind"
#                 ),
#                 "aristaStaticRouteConfiguration": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "arista_static_route_configuration"
#                 ),
#                 "aristaUplinkResourceId": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "arista_uplink_resource_id"
#                 ),
#                 "aristaVrfToVrfConfig": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "arista_vrf_to_vrf_config"
#                 ),
#                 "ciscoExternalEpgName": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "cisco_external_epg_name"
#                 ),
#                 "ciscoL3outName": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "cisco_l3out_name"
#                 ),
#                 "ciscoProvidedContractNames": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "cisco_provided_contract_names"
#                 ),
#                 "platformEgressAclResourceId": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "platform_egress_acl_resource_id"
#                 ),
#                 "platformExportRoutePolicy": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "platform_export_route_policy"
#                 ),
#                 "platformImportRoutePolicy": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "platform_import_route_policy"
#                 ),
#                 "platformIngressAclResourceId": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "platform_ingress_acl_resource_id"
#                 ),
#                 "platformLabeledVpnConfig": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "platform_labeled_vpn_config"
#                 ),
#                 "platformMultihopLabeledVpnConfig": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "platform_multihop_labeled_vpn_config"
#                 ),
#                 "platformPeeringKind": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "platform_peering_kind"
#                 ),
#                 "platformStaticRouteConfiguration": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "platform_static_route_configuration"
#                 ),
#                 "platformUplinkResourceId": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "platform_uplink_resource_id"
#                 ),
#                 "platformVrfToVrfConfig": CONFIG.get(
#                     "FABRIC_V2_VRF_PEERING", "platform_vrf_to_vrf_config"
#                 ),
#                 "tags": CONFIG.get("FABRIC_V2_VRF_PEERING", "tags"),
#                 "updatedTags": CONFIG.get("FABRIC_V2_VRF_PEERING", "updated_tags"),
#             }
#         )

#     def test_GA_fabric_v2_vrf_peering_scenario1(self):
#         """Test Fabric v2 VRF Peering CRUD operations."""
#         call_scenario1(self)

#     def test_GA_fabric_v2_vrf_peering_scenario2(self):
#         """Test Fabric v2 VRF Peering CRUD operations with parameter aliases."""
#         call_scenario2(self)

#     def test_GA_fabric_v2_vrf_peering_arista_cv_config(self):
#         """Test Fabric v2 VRF Peering Arista CloudVision configuration."""
#         call_arista_cv_config_scenario(self)

#     def test_GA_fabric_v2_vrf_peering_cisco_aci_config(self):
#         """Test Fabric v2 VRF Peering Cisco ACI configuration."""
#         call_cisco_aci_config_scenario(self)

#     def test_GA_fabric_v2_vrf_peering_platform_managed_config(self):
#         """Test Fabric v2 VRF Peering platform-managed configuration."""
#         call_platform_managed_config_scenario(self)
