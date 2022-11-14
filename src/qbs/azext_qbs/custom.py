# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import json
import sys

from azure.cli.core._profile import Profile
from azure.cli.core.util import send_raw_request
from knack.log import get_logger
logger = get_logger(__name__)

RESOURCE_ID = os.environ.get("AZ_CLI_QBS_RESOURCE_ID") or "8c989307-2439-402b-86eb-5900c6132dee"
BASE_URL = os.environ.get("AZ_CLI_QBS_MANAGEMENT_URL") or "https://management.onquorum.net"


def qbs_request_with_member(cmd, resource_group_name, member_name, url_postfix, method, body=None,
                            result_plain_text=False):
    return qbs_request_with_resource_group(cmd,
                                           resource_group_name,
                                           "/providers/ConsenSys.Blockchain/blockchainMembers/" +
                                           f"{member_name}{url_postfix}",
                                           method, body, result_plain_text)


def qbs_request_with_resource_group(cmd, resource_group_name, url_postfix, method, body=None, result_plain_text=False):
    return qbs_request_with_subscriptions(cmd, f"/resourceGroups/{resource_group_name}{url_postfix}", method, body,
                                          result_plain_text)


def qbs_request_with_subscriptions(cmd, url_postfix, method, body=None, result_plain_text=False):
    profile = Profile(cli_ctx=cmd.cli_ctx)
    creds, _, _ = profile.get_raw_token(subscription=None,
                                        resource=RESOURCE_ID,
                                        scopes=None,
                                        tenant=None)
    access_token = creds[1]
    url = BASE_URL + "/subscriptions/{subscriptionId}" + url_postfix
    json_string = None
    if body is not None:
        json_string = json.dumps(body)

    r = send_raw_request(cmd.cli_ctx,
                         method,
                         url,
                         headers=[
                             f"Authorization=Bearer {access_token}",
                         ],
                         body=json_string)
    if result_plain_text:
        return r.text
    return r.json()


# BlockchainMembers
def get_show_members(cmd, resource_group_name, member_name):
    return qbs_request_with_member(cmd, resource_group_name, member_name, "", "GET")


def get_members(cmd, resource_group_name=None):
    if resource_group_name is None:
        return qbs_request_with_subscriptions(cmd, "/providers/ConsenSys.Blockchain/blockchainMembers", "GET")
    return qbs_request_with_resource_group(cmd,
                                           resource_group_name,
                                           "/providers/ConsenSys.Blockchain/blockchainMembers",
                                           "GET")


def get_member_api_keys(cmd, resource_group_name, member_name):
    return qbs_request_with_member(cmd, resource_group_name, member_name, "/listApiKeys", "POST")


def get_member_regenerate_api_keys(cmd, resource_group_name, member_name):
    return qbs_request_with_member(cmd, resource_group_name, member_name, "/regenerateApiKeys", "POST")


# ConsortiumManagement
def get_consortium_members(cmd, resource_group_name, member_name):
    return qbs_request_with_member(cmd, resource_group_name, member_name, "/consortiumMembers", "GET")


def delete_consortium_members(cmd, resource_group_name, member_name, member_name_to_remove):
    return qbs_request_with_member(cmd, resource_group_name, member_name, f"/consortiumMembers/{member_name_to_remove}",
                                   "DELETE")


def get_consortium_genesis(cmd, resource_group_name, member_name):
    return qbs_request_with_member(cmd, resource_group_name, member_name, "/genesis", "GET")


# Invites
def post_invites(cmd, resource_group_name, member_name, invitee_subscription, invitee_email, expire_in_days=None,
                 invitee_role="MEMBER", inviter_email=None):
    body = {
        "inviteeSubscriptionId": invitee_subscription,
        "inviteeEmail": invitee_email,
        "inviteeRole": invitee_role,
        "inviterEmail": inviter_email
    }

    if expire_in_days is not None:
        body["expireInDays"] = expire_in_days
    return qbs_request_with_member(cmd, resource_group_name, member_name, "/invites", "POST", body)


def get_invites(cmd, resource_group_name, member_name):
    return qbs_request_with_member(cmd, resource_group_name, member_name, "/invites", "GET")


def delete_invites(cmd, resource_group_name, member_name, invite_code):
    return qbs_request_with_member(cmd, resource_group_name, member_name, f"/invites/{invite_code}", "DELETE",
                                   result_plain_text=True)


def get_invites_valid(cmd, invite_code):
    return qbs_request_with_subscriptions(cmd,
                                          f"/providers/ConsenSys.Blockchain/isInviteCodeValid/{invite_code}",
                                          "GET")


# Locations
def get_locations(cmd, name):
    return qbs_request_with_subscriptions(cmd,
                                          f"/providers/ConsenSys.Blockchain/locations/{name}/listConsortiums",
                                          "GET")


# TransactionNodes
def get_transaction_show(cmd, resource_group_name, member_name, transaction_node_name):
    return qbs_request_with_member(cmd, resource_group_name, member_name, f"/transactionNodes/{transaction_node_name}",
                                   "GET")


def get_transaction_list(cmd, resource_group_name, member_name):
    return qbs_request_with_member(cmd, resource_group_name, member_name, "/transactionNodes", "GET")


def get_transaction_list_api_keys(cmd, resource_group_name, member_name, transaction_node_name):
    return qbs_request_with_member(cmd,
                                   resource_group_name,
                                   member_name,
                                   f"/transactionNodes/{transaction_node_name}/listApiKeys",
                                   "GET")


def post_transaction_regenerate_api_keys(cmd, resource_group_name, member_name, transaction_node_name):
    return qbs_request_with_member(cmd,
                                   resource_group_name,
                                   member_name,
                                   f"/transactionNodes/{transaction_node_name}/regenerateApiKeys",
                                   "POST")


def put_transaction(cmd, resource_group_name, member_name, transaction_node_name, archive_node=False):
    is_archive_node_text = "true" if archive_node else "false"
    return qbs_request_with_member(cmd,
                                   resource_group_name,
                                   member_name,
                                   f"/transactionNodes/{transaction_node_name}?isArchiveNode={is_archive_node_text}",
                                   "PUT",
                                   result_plain_text=True)


def delete_transaction(cmd, resource_group_name, member_name, transaction_node_name):
    return qbs_request_with_member(cmd,
                                   resource_group_name,
                                   member_name,
                                   f"/transactionNodes/{transaction_node_name}",
                                   "DELETE",
                                   result_plain_text=True)


# Firewall
def get_firewall_list(cmd, resource_group_name, member_name, transaction_node_name=None):
    if transaction_node_name is None:
        return get_show_members(cmd, resource_group_name, member_name)["properties"]["firewallRules"]
    node = get_transaction_show(cmd, resource_group_name, member_name, transaction_node_name)
    return node["properties"]["firewallRules"]


def patch_firewall_add(cmd, resource_group_name, member_name, firewall_rule_name, start_ip_address, end_id_address,
                       transaction_node_name=None):
    body = [
        {
            "op": "add",
            "path": "/firewallRules/-",
            "value": {
                "ruleName": firewall_rule_name,
                "startIpAddress": start_ip_address,
                "endIpAddress": end_id_address
            }
        }
    ]
    return patch_firewall(cmd, member_name, resource_group_name, transaction_node_name, body)


def patch_firewall_remove(cmd, resource_group_name, member_name, firewall_rule_name, transaction_node_name=None):
    all_rules = get_firewall_list(cmd, resource_group_name, member_name, transaction_node_name)
    all_names = list(map(lambda x: x["ruleName"], all_rules))

    if firewall_rule_name not in all_names:
        logger.error("\"%s\" rule not found.", firewall_rule_name)
        if len(all_names) > 0:
            logger.error("List of current firewall rules: %s", ", ".join(all_names))
        else:
            logger.error("No current firewall rules.")
        sys.exit(1)

    index = all_names.index(firewall_rule_name)

    body = [
        {
            "op": "remove",
            "path": "/firewallRules/" + str(index),
        }
    ]
    return patch_firewall(cmd, member_name, resource_group_name, transaction_node_name, body)


def patch_firewall_clear(cmd, resource_group_name, member_name, transaction_node_name=None):
    body = [
        {
            "op": "replace",
            "path": "/firewallRules",
            "value": []
        }
    ]
    return patch_firewall(cmd, member_name, resource_group_name, transaction_node_name, body)


def patch_firewall(cmd, member_name, resource_group_name, transaction_node_name, body):
    if transaction_node_name is None:
        return qbs_request_with_member(cmd,
                                       resource_group_name,
                                       member_name,
                                       "",
                                       "PATCH",
                                       body)
    return qbs_request_with_member(cmd,
                                   resource_group_name,
                                   member_name,
                                   f"/transactionNodes/{transaction_node_name}",
                                   "PATCH",
                                   body)


# Scheduled restart
def get_scheduled_restarts(cmd, member_name, resource_group_name):
    return qbs_request_with_member(cmd, resource_group_name, member_name, "/scheduledRestarts", "GET")


def delete_scheduled_restarts(cmd, member_name, resource_group_name, scheduled_restart_id):
    return qbs_request_with_member(cmd,
                                   resource_group_name,
                                   member_name,
                                   f"/scheduledRestarts/{scheduled_restart_id}",
                                   "DELETE",
                                   result_plain_text=True)


def post_scheduled_restarts(cmd, member_name, resource_group_name, scheduled_restart_time):
    return qbs_request_with_member(cmd,
                                   resource_group_name,
                                   member_name,
                                   "/scheduledRestarts",
                                   "POST",
                                   {
                                       "time": scheduled_restart_time
                                   })


def get_backup(cmd, member_name, resource_group_name):
    return qbs_request_with_member(cmd,
                                   resource_group_name,
                                   member_name,
                                   "/backup/listBackups",
                                   "GET")


def put_backup(cmd, member_name, resource_group_name):
    return qbs_request_with_member(cmd,
                                   resource_group_name,
                                   member_name,
                                   "/backup",
                                   "PUT",
                                   result_plain_text=True)


def post_member_pause(cmd, member_name, resource_group_name):
    return qbs_request_with_member(cmd,
                                   resource_group_name,
                                   member_name,
                                   "/pause",
                                   "POST",
                                   result_plain_text=True)


def post_member_resume(cmd, member_name, resource_group_name):
    return qbs_request_with_member(cmd,
                                   resource_group_name,
                                   member_name,
                                   "/resume",
                                   "POST",
                                   result_plain_text=True)
