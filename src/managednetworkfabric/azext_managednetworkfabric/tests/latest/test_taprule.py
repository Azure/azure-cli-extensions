# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Network Tap Rule tests scenarios
"""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def setup_scenario2(test):
    """Env setup_scenario2"""
    pass


def cleanup_scenario2(test):
    """Env cleanup_scenario2"""
    pass


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario1(test)
    step_create_scenario1(test, checks=[])
    step_show(test, checks=[])
    step_list_subscription(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_update_scenario1(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def call_scenario2(test):
    """Testcase: scenario2"""
    setup_scenario2(test)
    step_create_scenario2(test, checks=[])
    step_update_scenario2(test, checks=[])
    cleanup_scenario2(test)


def step_create_scenario1(test, checks=None):
    """Network Tap Rule create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric taprule create --resource-group {rg} --location {location} --resource-name {name} --configuration-type {configurationType} --dynamic-match-configurations {dynamicMatchConfigurations}"
        " --global-network-tap-rule-actions {globalNetworkTapRuleActions} --match-configurations {matchConfigurations} --polling-interval-in-seconds {pollingIntervalInSeconds} --tap-rules-url {tapRulesUrl}"
        " --identity-selector {identitySelector} --mi-user-assigned {userAssignedIdentity} --mi-system-assigned {systemAssignedIdentity} --annotation {annotation} ",
        checks=checks,
    )


def step_create_scenario2(test, checks=None):
    """Network Tap Rule create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric taprule create --resource-group {rg} --location {location} --resource-name {name} --configuration-type {configurationType} --dynamic-match-configs {dynamicMatchConfigurations}"
        " --global-ntr-actions {globalNetworkTapRuleActions} --match-configurations {matchConfigurations} --polling-interval {pollingIntervalInSeconds} --tap-rules-url {tapRulesUrl}"
        " --identity-selector {identitySelector} --user-assigned {userAssignedIdentity} --system-assigned {systemAssignedIdentity} --annotation {annotation} ",
        checks=checks,
    )


def step_show(test, checks=None):
    """Network Tap Rule show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric taprule show --resource-name {name} --resource-group {rg}"
    )


def step_list_resource_group(test, checks=None):
    """Network Tap Rule list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkfabric taprule list --resource-group {rg}")


def step_list_subscription(test, checks=None):
    """Network Tap Rule list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkfabric taprule list")


def step_update_scenario1(test, checks=None):
    """Network Tap Rule update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric taprule update --resource-name {deleteName} --resource-group {rg} --match-configurations {updatedMatchConfigurations}"
        " --tap-rules-url {tapRulesUrl} --identity-selector {identitySelector} --mi-user-assigned {userAssignedIdentity} --mi-system-assigned {systemAssignedIdentity}"
        " --dynamic-match-configurations {dynamicMatchConfigurations} --annotation {annotation} --global-network-tap-rule-actions {globalNetworkTapRuleActions}"
        " --configuration-type {configurationType}",
        checks=checks,
    )


def step_update_scenario2(test, checks=None):
    """Network Tap Rule update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric taprule update --resource-name {deleteName} --resource-group {rg} --match-configurations {updatedMatchConfigurations}"
        " --tap-rules-url {tapRulesUrl} --identity-selector {identitySelector} --user-assigned {userAssignedIdentity} --system-assigned {systemAssignedIdentity}"
        " --dynamic-match-configs {dynamicMatchConfigurations} --annotation {annotation} --global-ntr-actions {globalNetworkTapRuleActions}"
        " --configuration-type {configurationType}",
        checks=checks,
    )


def step_delete(test, checks=None):
    """Network Tap Rule delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric taprule delete --resource-name {deleteName} --resource-group {rg}"
    )


class GA_TapRuleScenarioTest1(ScenarioTest):
    """Network Tap Rule Scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_TAP_RULE", "name"),
                "deleteName": CONFIG.get("NETWORK_TAP_RULE", "delete_name"),
                "rg": CONFIG.get("NETWORK_TAP_RULE", "resource_group"),
                "location": CONFIG.get("NETWORK_TAP_RULE", "location"),
                "annotation": CONFIG.get("NETWORK_TAP_RULE", "annotation"),
                "pollingIntervalInSeconds": CONFIG.get(
                    "NETWORK_TAP_RULE", "polling_interval_in_seconds"
                ),
                "configurationType": CONFIG.get(
                    "NETWORK_TAP_RULE", "configuration_type"
                ),
                "dynamicMatchConfigurations": CONFIG.get(
                    "NETWORK_TAP_RULE", "dynamic_match_configurations"
                ),
                "matchConfigurations": CONFIG.get(
                    "NETWORK_TAP_RULE", "match_configurations"
                ),
                "globalNetworkTapRuleActions": CONFIG.get(
                    "NETWORK_TAP_RULE", "global_network_tap_rule_actions"
                ),
                "updatedMatchConfigurations": CONFIG.get(
                    "NETWORK_TAP_RULE", "updated_match_configurations"
                ),
                "tapRulesUrl": CONFIG.get("NETWORK_TAP_RULE", "tap_rules_url"),
                "identitySelector": CONFIG.get("MANAGED_IDENTITY", "identity_selector"),
                "userAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "user_assigned_identity"
                ),
                "systemAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "system_assigned_identity"
                ),
            }
        )

    def test_GA_taprule_scenario1(self):
        """test scenario for Network Tap Rule CRUD operations"""
        call_scenario1(self)
