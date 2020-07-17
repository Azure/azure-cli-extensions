# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

# region AzureFirewalls
helps['network firewall'] = """
    type: group
    short-summary: Manage and configure Azure Firewalls.
"""

helps['network firewall create'] = """
    type: command
    short-summary: Create an Azure Firewall.
    examples:
    - name: Create a Azure firewall with private ranges
      text: |
        az network firewall create -g MyResourceGroup -n MyFirewall --private-ranges 10.0.0.0 10.0.0.0/16 IANAPrivateRanges
"""

helps['network firewall delete'] = """
    type: command
    short-summary: Delete an Azure Firewall.
"""

helps['network firewall list'] = """
    type: command
    short-summary: List Azure Firewalls.
"""

helps['network firewall show'] = """
    type: command
    short-summary: Get the details of an Azure Firewall.
"""

helps['network firewall update'] = """
    type: command
    short-summary: Update an Azure Firewall.
"""
# endregion

# region AzureFirewall IP Configurations
helps['network firewall ip-config'] = """
    type: group
    short-summary: Manage and configure Azure Firewall IP configurations.
"""

helps['network firewall ip-config create'] = """
    type: command
    short-summary: Create an Azure Firewall IP configuration.
"""

helps['network firewall ip-config delete'] = """
    type: command
    short-summary: Delete an Azure Firewall IP configuration.
"""

helps['network firewall ip-config list'] = """
    type: command
    short-summary: List Azure Firewall IP configurations.
"""

helps['network firewall ip-config show'] = """
    type: command
    short-summary: Get the details of an Azure Firewall IP configuration.
"""
# endregion

# region AzureFirewall Management IP Configurations
helps['network firewall management-ip-config'] = """
    type: group
    short-summary: Manage and configure Azure Firewall Management IP configurations.
"""

helps['network firewall management-ip-config update'] = """
    type: command
    short-summary: Update an Azure Firewall Management IP configuration.
"""

helps['network firewall management-ip-config show'] = """
    type: command
    short-summary: Get the details of an Azure Firewall Management IP configuration.
"""
# endregion

# region AzureFirewall Threat Intelligence Whitelist
helps['network firewall threat-intel-whitelist'] = """
    type: group
    short-summary: Manage and configure Azure Firewall Threat Intelligence Whitelist.
"""

helps['network firewall threat-intel-whitelist create'] = """
    type: command
    short-summary: Create an Azure Firewall Threat Intelligence Whitelist.
    examples:
        - name: Create a threat intelligence whitelist
          text: |
            az network firewall threat-intel-whitelist create -g MyResourceGroup -n MyFirewall --ip-addresses 10.0.0.0 10.0.0.1 --fqdns *.microsoft.com www.bing.com *google.com
"""

helps['network firewall threat-intel-whitelist delete'] = """
    type: command
    short-summary: Delete an Azure Firewall Threat Intelligence Whitelist.
"""

helps['network firewall threat-intel-whitelist update'] = """
    type: command
    short-summary: Update Azure Firewall Threat Intelligence Whitelist.
"""

helps['network firewall threat-intel-whitelist show'] = """
    type: command
    short-summary: Get the details of an Azure Firewall Threat Intelligence Whitelist.
"""
# endregion

# region AzureFirewall Network Rules
helps['network firewall network-rule'] = """
    type: group
    short-summary: Manage and configure Azure Firewall network rules.
"""

helps['network firewall network-rule create'] = """
    type: command
    short-summary: Create an Azure Firewall network rule.
"""

helps['network firewall network-rule delete'] = """
    type: command
    short-summary: Delete an Azure Firewall network rule.
"""

helps['network firewall network-rule list'] = """
    type: command
    short-summary: List Azure Firewall network rules.
"""

helps['network firewall network-rule show'] = """
    type: command
    short-summary: Get the details of an Azure Firewall network rule.
"""

helps['network firewall network-rule collection'] = """
    type: group
    short-summary: Manage and configure Azure Firewall network rule collections.
    long-summary: Collections are created as part of the `az network firewall network-rule create` command.
"""

helps['network firewall network-rule collection delete'] = """
    type: command
    short-summary: Delete an Azure Firewall network rule collection.
"""

helps['network firewall network-rule collection list'] = """
    type: command
    short-summary: List Azure Firewall network rule collections.
"""

helps['network firewall network-rule collection show'] = """
    type: command
    short-summary: Get the details of an Azure Firewall network rule collection.
"""
# endregion

# region AzureFirewall NAT Rules
helps['network firewall nat-rule'] = """
    type: group
    short-summary: Manage and configure Azure Firewall NAT rules.
"""

helps['network firewall nat-rule create'] = """
    type: command
    short-summary: Create an Azure Firewall NAT rule.
"""

helps['network firewall nat-rule delete'] = """
    type: command
    short-summary: Delete an Azure Firewall NAT rule.
"""

helps['network firewall nat-rule list'] = """
    type: command
    short-summary: List Azure Firewall NAT rules.
"""

helps['network firewall nat-rule show'] = """
    type: command
    short-summary: Get the details of an Azure Firewall NAT rule.
"""

helps['network firewall nat-rule collection'] = """
    type: group
    short-summary: Manage and configure Azure Firewall NAT rules.
    long-summary: Collections are created as part of the `az network firewall nat-rule create` command.
"""

helps['network firewall nat-rule collection delete'] = """
    type: command
    short-summary: Delete an Azure Firewall NAT rule collection.
"""

helps['network firewall nat-rule collection list'] = """
    type: command
    short-summary: List Azure Firewall NAT rule collections.
"""

helps['network firewall nat-rule collection show'] = """
    type: command
    short-summary: Get the details of an Azure Firewall NAT rule collection.
"""
# endregion

# region AzureFirewall Application Rules
helps['network firewall application-rule'] = """
    type: group
    short-summary: Manage and configure Azure Firewall application rules.
"""

helps['network firewall application-rule create'] = """
    type: command
    short-summary: Create an Azure Firewall application rule.
"""

helps['network firewall application-rule delete'] = """
    type: command
    short-summary: Delete an Azure Firewall application rule.
"""

helps['network firewall application-rule list'] = """
    type: command
    short-summary: List Azure Firewall application rules.
"""

helps['network firewall application-rule show'] = """
    type: command
    short-summary: Get the details of an Azure Firewall application rule.
"""

helps['network firewall application-rule collection'] = """
    type: group
    short-summary: Manage and configure Azure Firewall application rule collections.
    long-summary: Collections are created as part of the `az network firewall application-rule create` command.
"""

helps['network firewall application-rule collection delete'] = """
    type: command
    short-summary: Delete an Azure Firewall application rule collection.
"""

helps['network firewall application-rule collection list'] = """
    type: command
    short-summary: List Azure Firewall application rule collections.
"""

helps['network firewall application-rule collection show'] = """
    type: command
    short-summary: Get the details of an Azure Firewall application rule collection.
"""
# endregion

# region AzureFirewall Policy
helps['network firewall application-rule'] = """
    type: group
    short-summary: Manage and configure Azure Firewall application rules.
"""

helps['network firewall application-rule create'] = """
    type: command
    short-summary: Create an Azure Firewall application rule.
"""

helps['network firewall application-rule delete'] = """
    type: command
    short-summary: Delete an Azure Firewall application rule.
"""

helps['network firewall application-rule list'] = """
    type: command
    short-summary: List Azure Firewall application rules.
"""

helps['network firewall application-rule show'] = """
    type: command
    short-summary: Get the details of an Azure Firewall application rule.
"""

helps['network firewall application-rule collection'] = """
    type: group
    short-summary: Manage and configure Azure Firewall application rule collections.
    long-summary: Collections are created as part of the `az network firewall application-rule create` command.
"""

helps['network firewall application-rule collection delete'] = """
    type: command
    short-summary: Delete an Azure Firewall application rule collection.
"""

helps['network firewall application-rule collection list'] = """
    type: command
    short-summary: List Azure Firewall application rule collections.
"""

helps['network firewall application-rule collection show'] = """
    type: command
    short-summary: Get the details of an Azure Firewall application rule collection.
"""
# endregion

# region AzureFirewall Policy
helps['network firewall policy'] = """
    type: group
    short-summary: Manage and configure Azure firewall policy.
"""

helps['network firewall policy create'] = """
    type: command
    short-summary: Create an Azure firewall policy.
"""

helps['network firewall policy update'] = """
    type: command
    short-summary: Update an Azure firewall policy.
"""

helps['network firewall policy delete'] = """
    type: command
    short-summary: Delete an Azure firewall policy.
"""

helps['network firewall policy show'] = """
    type: command
    short-summary: Show an Azure firewall policy.
"""

helps['network firewall policy list'] = """
    type: command
    short-summary: List all Azure firewall policies.
"""

helps['network firewall policy rule-collection-group'] = """
    type: group
    short-summary: Manage and configure Azure firewall policy rule collection group.
"""

helps['network firewall policy rule-collection-group create'] = """
    type: command
    short-summary: Create an Azure firewall policy rule collection group.
"""

helps['network firewall policy rule-collection-group update'] = """
    type: command
    short-summary: Update an Azure firewall policy rule collection group.
"""

helps['network firewall policy rule-collection-group list'] = """
    type: command
    short-summary: List all Azure firewall policy rule collection groups.
"""

helps['network firewall policy rule-collection-group show'] = """
    type: command
    short-summary: Show an Azure firewall policy rule collection group.
"""

helps['network firewall policy rule-collection-group delete'] = """
    type: command
    short-summary: Delete an Azure Firewall policy rule collection group.
"""

helps['network firewall policy rule-collection-group collection'] = """
    type: group
    short-summary: Manage and configure Azure firewall policy rule collections in the rule collection group.
    long-summary: |
        Currently, Azure Firewall policy support two kinds of rule collections which are Filter collection and NAT collection. There are three kinds of rules which are application rule, network rule and nat rule.
        NAT collection support having a list of nat rule. Filter collection support including a list of rules(network rule or application rule) in it. But all of rules should be the same type.
"""

helps['network firewall policy rule-collection-group collection add-filter-collection'] = """
    type: command
    short-summary: Add a filter collection into an Azure firewall policy rule collection group.
    long-summary: |
        Common Rule Arguments are used for both Network rule and Application rule. If you want to add more rules into filter collection, please use "az network policy rule-collection-group collection rule add/remove"
    examples:
        - name: Add a filter collection with Network rule into the rule collection group
          text: az network firewall policy rule-collection-group collection add-filter-collection -g {rg} --policy-name {policy} --rule-collection-group-name {collectiongroup}
                --name filter_collection --action Allow --rule-name network_rule --rule-type NetworkRule
                --description "test" --destination-addresses "202.120.36.15" --source-addresses "202.120.36.13" "202.120.36.14" --destination-ports 12003 12004
                --ip-protocols TCP UDP --collection-priority 11002
        - name: Add a filter collection with Application rule into the rule collection group
          text: az network firewall policy rule-collection-group collection add-filter-collection -g {rg} --policy-name {policy} --rule-collection-group-name {collectiongroup}
                --name filter_collection --action Allow --rule-name application_rule --rule-type ApplicationRule --description "test"
                --destination-addresses "202.120.36.15" "202.120.36.16" --source-addresses "202.120.36.13" "202.120.36.14"
                --protocols Http=12800 Https=12801 --fqdn-tags AzureBackup HDInsight --collection-priority 11100
"""

helps['network firewall policy rule-collection-group collection add-nat-collection'] = """
    type: command
    short-summary: Add a NAT collection into an Azure firewall policy rule collection group.
    examples:
        - name: Add a NAT collection into the rule collection group
          text: az network firewall policy rule-collection-group collection add-nat-collection -n nat_collection --collection-priority 10003
                --policy-name {policy} -g {rg} --rule-collection-group-name {collectiongroup} --action DNAT
                --rule-name network_rule --description "test" --destination-addresses "202.120.36.15"
                --source-addresses "202.120.36.13" "202.120.36.14" --translated-address 128.1.1.1
                --translated-port 1234 --destination-ports 12000 12001 --ip-protocols TCP UDP
"""

helps['network firewall policy rule-collection-group collection list'] = """
    type: command
    short-summary: List all rule collections of an Azure firewall policy rule collection group.
"""

helps['network firewall policy rule-collection-group collection remove'] = """
    type: command
    short-summary: Remove a rule collection from an Azure firewall policy rule collection group.
"""

helps['network firewall policy rule-collection-group collection rule'] = """
    type: group
    short-summary: Manage and configure the rule of a filter collection in the rule collection group of Azure firewall policy.
    long-summary: |
        Filter collection supports having a list of network rules or application rules.
        NatRule collection supports including a list of nat rules.
"""

helps['network firewall policy rule-collection-group collection rule add'] = """
    type: command
    short-summary: Add a rule into an Azure firewall policy rule collection.
    long-summary: |
        Filter collection supports having a list of network rules or application rules.
        NatRule collection supports including a list of nat rules.
"""

helps['network firewall policy rule-collection-group collection rule remove'] = """
    type: command
    short-summary: Remove a rule from an Azure firewall policy rule collection.
    long-summary: |
        Filter collection supports having a list of network rules or application rules.
        NatRule collection supports including a list of nat rules.
"""
# endregion
