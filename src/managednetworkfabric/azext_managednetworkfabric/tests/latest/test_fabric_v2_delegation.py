# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Fabric v2 Delegation test scenarios."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def call_scenario1(test):
    """Test the Fabric Delegation CRUD lifecycle."""
    step_create_scenario1(
        test,
        [
            test.check("name", test.kwargs["name"].strip('"')),
            test.check("administrativeState", test.kwargs["adminState"].strip('"')),
        ],
    )
    step_show(test, [test.check("name", test.kwargs["name"].strip('"'))])
    step_update_scenario1(
        test,
        [
            test.check(
                "administrativeState",
                test.kwargs["updatedAdminState"].strip('"'),
            )
        ],
    )
    step_list(test, [test.check("[0].name", test.kwargs["name"].strip('"'))])
    step_delete(test)


def call_scenario2(test):
    """Test Fabric Delegation create and update parameter aliases."""
    step_create_scenario2(test)
    step_update_scenario2(
        test,
        [
            test.check(
                "administrativeState",
                test.kwargs["updatedAdminState"].strip('"'),
            )
        ],
    )


def step_create_scenario1(test, checks=None):
    """Create a Fabric Delegation."""
    test.cmd(
        "az networkfabric fabric-v2 delegation create --resource-group {rg} "
        "--fabric-v2 {fabricName} --resource-name {name} --location {location} "
        "--address-prefixes {addressPrefixes} "
        "--admin-state {adminState} --allowed-egress-networks {allowedEgressNetworks} "
        "--customer-rg-name {customerResourceGroup} "
        "--customer-sub-id {customerSubscriptionId} "
        "--customer-tenant-id {customerTenantId} "
        "--default-routing-domain-limits {defaultRoutingDomainLimits} "
        "--routing-domain-budget {routingDomainBudget} --tags {tags}",
        checks=checks or [],
    )


def step_create_scenario2(test, checks=None):
    """Create a Fabric Delegation using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 delegation create --resource-group {rg} "
        "--fabric-v2-name {fabricName} --resource-name {name} --location {location} "
        "--address-prefixes {addressPrefixes} --admin-state {adminState} "
        "--allowed-egr-nets {allowedEgressNetworks} "
        "--customer-rg {customerResourceGroup} "
        "--customer-sub {customerSubscriptionId} "
        "--customer-tenant {customerTenantId} "
        "--drd-limits {defaultRoutingDomainLimits} "
        "--rd-budget {routingDomainBudget} --tags {tags}",
        checks=checks or [],
    )


def step_show(test, checks=None):
    """Show a Fabric Delegation."""
    test.cmd(
        "az networkfabric fabric-v2 delegation show --resource-group {rg} "
        "--fabric-v2 {fabricName} --resource-name {name}",
        checks=checks or [],
    )


def step_update_scenario1(test, checks=None):
    """Update a Fabric Delegation."""
    test.cmd(
        "az networkfabric fabric-v2 delegation update --resource-group {rg} "
        "--fabric-v2 {fabricName} --resource-name {name} "
        "--admin-state {updatedAdminState} "
        "--address-prefixes {updatedAddressPrefixes} "
        "--allowed-egress-networks {updatedAllowedEgressNetworks} "
        "--default-routing-domain-limits {updatedDefaultRoutingDomainLimits} "
        "--routing-domain-budget {updatedRoutingDomainBudget} "
        "--tags {updatedTags}",
        checks=checks or [],
    )


def step_update_scenario2(test, checks=None):
    """Update a Fabric Delegation using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 delegation update --resource-group {rg} "
        "--fabric-v2-name {fabricName} --resource-name {name} "
        "--admin-state {updatedAdminState} "
        "--address-prefixes {updatedAddressPrefixes} "
        "--allowed-egr-nets {updatedAllowedEgressNetworks} "
        "--drd-limits {updatedDefaultRoutingDomainLimits} "
        "--rd-budget {updatedRoutingDomainBudget} --tags {updatedTags}",
        checks=checks or [],
    )


def step_list(test, checks=None):
    """List Fabric Delegations by Fabric."""
    test.cmd(
        "az networkfabric fabric-v2 delegation list --resource-group {rg} "
        "--fabric-v2 {fabricName}",
        checks=checks or [],
    )


def step_delete(test, checks=None):
    """Delete a Fabric Delegation."""
    test.cmd(
        "az networkfabric fabric-v2 delegation delete --resource-group {rg} "
        "--fabric-v2 {fabricName} --resource-name {name}",
        checks=checks or [],
    )


class FabricV2DelegationScenarioTest(ScenarioTest):
    """Fabric v2 Delegation scenario test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("FABRIC_V2_DELEGATION", "name"),
                "rg": CONFIG.get("FABRIC_V2_DELEGATION", "resource_group"),
                "fabricName": CONFIG.get("FABRIC_V2_DELEGATION", "fabric_name"),
                "location": CONFIG.get("FABRIC_V2_DELEGATION", "location"),
                "adminState": CONFIG.get("FABRIC_V2_DELEGATION", "admin_state"),
                "updatedAdminState": CONFIG.get(
                    "FABRIC_V2_DELEGATION", "updated_admin_state"
                ),
                "allowedEgressNetworks": CONFIG.get(
                    "FABRIC_V2_DELEGATION", "allowed_egress_networks"
                ),
                "customerResourceGroup": CONFIG.get(
                    "FABRIC_V2_DELEGATION", "customer_resource_group"
                ),
                "customerSubscriptionId": CONFIG.get(
                    "FABRIC_V2_DELEGATION", "customer_subscription_id"
                ),
                "customerTenantId": CONFIG.get(
                    "FABRIC_V2_DELEGATION", "customer_tenant_id"
                ),
                "defaultRoutingDomainLimits": CONFIG.get(
                    "FABRIC_V2_DELEGATION", "default_routing_domain_limits"
                ),
                "routingDomainBudget": CONFIG.get(
                    "FABRIC_V2_DELEGATION", "routing_domain_budget"
                ),
                "addressPrefixes": CONFIG.get(
                    "FABRIC_V2_DELEGATION", "address_prefixes"
                ),
                "tags": CONFIG.get("FABRIC_V2_DELEGATION", "tags"),
                "updatedAddressPrefixes": CONFIG.get(
                    "FABRIC_V2_DELEGATION", "updated_address_prefixes"
                ),
                "updatedAllowedEgressNetworks": CONFIG.get(
                    "FABRIC_V2_DELEGATION", "updated_allowed_egress_networks"
                ),
                "updatedDefaultRoutingDomainLimits": CONFIG.get(
                    "FABRIC_V2_DELEGATION",
                    "updated_default_routing_domain_limits",
                ),
                "updatedRoutingDomainBudget": CONFIG.get(
                    "FABRIC_V2_DELEGATION", "updated_routing_domain_budget"
                ),
                "updatedTags": CONFIG.get("FABRIC_V2_DELEGATION", "updated_tags"),
            }
        )

    def test_fabric_v2_delegation_scenario1(self):
        """Test Fabric Delegation CRUD operations."""
        call_scenario1(self)

    def test_fabric_v2_delegation_scenario2(self):
        """Test Fabric Delegation CRUD operations with parameter aliases."""
        call_scenario2(self)
