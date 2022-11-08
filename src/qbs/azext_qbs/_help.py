# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['qbs'] = """
type: group
short-summary: Commands to interact with "Quorum Blockchain Service" Azure Managed Applications.
"""

helps['qbs consortium'] = """
type: group
short-summary: Manage consortium (private blockchain network), where the blockchain network is limited to specific network participants.
"""

helps['qbs consortium remove'] = """
type: command
short-summary: As an administrator, remove a member from the consortium you are part of. The leaving member will no longer be part of the consortium, but will retain all their data unless they choose to delete their managed app.
parameters:
  - name: --member-name-to-remove
    type: string
    short-summary: The name of the blockchain member that will get removed.
"""

helps['qbs consortium genesis'] = """
type: command
short-summary: Get the genesis file for the consortium.
"""

helps['qbs consortium list'] = """
type: command
short-summary: List consortium members.
"""

helps['qbs member'] = """
type: group
short-summary: Manage individual blockchain members.
"""

helps['qbs member list'] = """
type: command
short-summary: Lists the blockchain members for a subscription or specific resource group.
"""

helps['qbs member list-api-keys'] = """
    type: command
    short-summary: Gets the Member API keys for an installation of Quorum Blockchain Service.
"""

helps['qbs member regenerate-api-keys'] = """
    type: command
    short-summary: Regenerate the API keys for the blockchain member nodes.
"""

helps['qbs member show'] = """
    type: command
    short-summary: Get the details of the blockchain member.
"""

helps['qbs member pause'] = """
    type: command
    short-summary: Pause the nodes for a blockchain member.
"""

helps['qbs member resume'] = """
    type: command
    short-summary: Resume the nodes for a blockchain member.
"""

helps['qbs firewall'] = """
type: group
short-summary: Configure firewall rules to limit which IP addresses, or IP address ranges, are allowed to attempt to connect to your nodes.
"""

helps['qbs firewall add'] = """
type: command
short-summary: Add a firewall rule to QBS member or transaction node.
parameters:
  - name: --end-id-address
    type: string
    short-summary: The end of the valid IP range for the firewall rule.
  - name: --start-ip-address
    type: string
    short-summary: The start of the valid IP range for the firewall rule.
"""

helps['qbs firewall remove'] = """
type: command
short-summary: Remove a firewall rule to QBS member or transaction node.
"""

helps['qbs firewall clear'] = """
type: command
short-summary: Remove all firewall rules of a QBS member or transaction node.
"""

helps['qbs firewall list'] = """
type: command
short-summary: List all firewall rules of a QBS member or transaction node.
"""

helps['qbs invite'] = """
type: group
short-summary: Invite a member to join a consortium. More information available at https://consensys.net/docs/qbs/en/latest/concepts/consortiums/
"""

helps['qbs invite list'] = """
type: command
short-summary: List invites for an existing consortium. All inviter members with the Owner role can list any invite for the consortium.
"""

helps['qbs invite revoke'] = """
type: command
short-summary: Revoke an invite to join an existing consortium. All inviter members with the Owner role can revoke any invite for the consortium.
"""

helps['qbs invite validate'] = """
type: command
short-summary: Validate an invite code for an invitee's subscriptionId.
"""

helps['qbs invite create'] = """
type: command
short-summary: Create an invite to join an existing consortium. More information is available at https://consensys.net/docs/qbs/en/latest/Concepts/Consortium-Management/ .
parameters:
  - name: --expire-in-days
    type: number
    short-summary: Number of days before invite expires.
  - name: --invitee-role
    type: string
    short-summary: Role of the invitee (OWNER or MEMBER).
  - name: --inviter-email
    type: string
    short-summary: Optionally, you can add your own inviter email to get cc'd a copy of the invite.
  - name: --invitee-email
    type: string
    short-summary: Invitee contact email.
  - name: --invitee-subscription
    type: string
    short-summary: Subscription id of the invitee.
"""

helps['qbs location'] = """
type: group
short-summary: List blockchain members by location.
"""

helps['qbs location list'] = """
type: command
short-summary: Lists the available consortiums for a subscription.
parameters:
  - name: --name
    type: string
    short-summary: >
        Azure region name. Example: "japaneast".
"""

helps['qbs transaction-node'] = """
type: group
short-summary: Add or remove additional transaction nodes to your blockchain member.
"""

helps['qbs transaction-node add'] = """
type: command
short-summary: Adds a transaction node.
"""

helps['qbs transaction-node list'] = """
type: command
short-summary: Lists the transaction nodes for a blockchain member.
"""

helps['qbs transaction-node list-api-keys'] = """
type: command
short-summary: List the API keys for the transaction node.
"""

helps['qbs transaction-node regenerate-api-keys'] = """
type: command
short-summary: Regenerate the API keys for the transaction node.
"""

helps['qbs transaction-node remove'] = """
type: command
short-summary: Removes a transaction node.
"""

helps['qbs transaction-node show'] = """
type: command
short-summary: Get the details of the transaction node.
"""

helps['qbs scheduled-restart'] = """
type: group
short-summary: Schedule planned restarts for the VMs in your blockchain member.
"""

helps['qbs scheduled-restart list'] = """
type: command
short-summary: Get the details of scheduled restarts; past, current and future.
"""

helps['qbs scheduled-restart remove'] = """
type: command
short-summary: Remove a scheduled restart, will not cancel in-progress restarts.
parameters:
  - name: --scheduled-restart-id
    type: string
    short-summary: Id of the scheduled restart event.
"""

helps['qbs scheduled-restart add'] = """
type: command
short-summary: Schedule the restart of a consortium member.
parameters:
  - name: --scheduled-restart-time
    type: string
    short-summary: >
        Time in ISO-8601 format. Example: "2023-08-09T03:06:27.769Z".
"""

helps['qbs backup'] = """
type: group
short-summary: Backup the state of the blockchain.
"""

helps['qbs backup list'] = """
type: command
short-summary: Get the details of existing backups.
"""

helps['qbs backup start'] = """
type: command
short-summary: Start the backup process.
"""
