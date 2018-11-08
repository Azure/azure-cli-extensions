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
