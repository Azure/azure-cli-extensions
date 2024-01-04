# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
from knack.util import CLIError
from azure.cli.core.azclierror import (
    UnknownError
)
from .constants import (
    RP_API, ClUSTER_RESOURCE_API, CLUSTER_RESOURCE_ID
)
from ..._client_factory import (
    cf_resources, cf_resource_groups, cf_log_analytics)
from azure.core.exceptions import HttpResponseError
from ... import consts


def sanitize_resource_id(resource_id):
    resource_id = resource_id.strip()
    if not resource_id.startswith("/"):
        resource_id = "/" + resource_id
    if resource_id.endswith("/"):
        resource_id = resource_id.rstrip("/")
    return resource_id.lower()


def post_request(cmd, subscription_id, rp_name, headers):
    from azure.cli.core.util import send_raw_request
    armendpoint = cmd.cli_ctx.cloud.endpoints.resource_manager
    customUrl = "{0}/subscriptions/{1}/providers/{2}/register?api-version={3}".format(
        armendpoint,
        subscription_id,
        rp_name,
        RP_API,
    )
    try:
        send_raw_request(cmd.cli_ctx, "POST", customUrl, headers=headers)
    except CLIError as e:
        raise CLIError(e)


# pylint: disable=line-too-long
def rp_registrations(cmd, subscription_id):
    from azure.cli.core.util import send_raw_request
    # Get list of RP's for RP's subscription
    try:
        headers = ['User-Agent=arc-azuremonitormetrics.get_mac_sub_list']
        armendpoint = cmd.cli_ctx.cloud.endpoints.resource_manager
        customUrl = "{0}/subscriptions/{1}/providers?api-version={2}&$select=namespace,registrationstate".format(
            armendpoint,
            subscription_id,
            RP_API
        )
        r = send_raw_request(cmd.cli_ctx, "GET", customUrl, headers=headers)
    except CLIError as e:
        raise CLIError(e)
    isInsightsRpRegistered = False
    isAlertsManagementRpRegistered = False
    isMoniotrRpRegistered = False
    isDashboardRpRegistered = False
    json_response = json.loads(r.text)
    values_array = json_response["value"]
    for value in values_array:
        if value["namespace"].lower() == "microsoft.insights" and value["registrationState"].lower() == "registered":
            isInsightsRpRegistered = True
        if value["namespace"].lower() == "microsoft.alertsmanagement" and value["registrationState"].lower() == "registered":
            isAlertsManagementRpRegistered = True
        if value["namespace"].lower() == "microsoft.monitor" and value["registrationState"].lower() == "registered":
            isAlertsManagementRpRegistered = True
        if value["namespace"].lower() == "microsoft.dashboard" and value["registrationState"].lower() == "registered":
            isAlertsManagementRpRegistered = True
    if isInsightsRpRegistered is False:
        print(f"Registering microsoft.insights RP for the subscription {subscription_id}")
        headers = ['User-Agent=arc-azuremonitormetrics.register_insights_rp']
        post_request(cmd, subscription_id, "microsoft.insights", headers)
    if isAlertsManagementRpRegistered is False:
        print(f"Registering microsoft.alertsmanagement RP for the subscription {subscription_id}")
        headers = ['User-Agent=arc-azuremonitormetrics.register_alertsmanagement_rp']
        post_request(cmd, subscription_id, "microsoft.alertsmanagement", headers)
    if isMoniotrRpRegistered is False:
        print(f"Registering microsoft.monitor RP for the subscription {subscription_id}")
        headers = ['User-Agent=arc-azuremonitormetrics.register_monitor_rp']
        post_request(cmd, subscription_id, "microsoft.monitor", headers)
    if isDashboardRpRegistered is False:
        print(f"Registering microsoft.dashboard RP for the subscription {subscription_id}")
        headers = ['User-Agent=arc-azuremonitormetrics.register_dashboard_rp']
        post_request(cmd, subscription_id, "microsoft.dashboard", headers)


def get_cluster_region(cmd, cluster_rp, subscription_id, cluster_resource_group_name, cluster_name, cluster_type):
    cluster_region = ''
    resources = cf_resources(cmd.cli_ctx, subscription_id)
    cluster_resource_id = CLUSTER_RESOURCE_ID.format(
        subscription_id, cluster_resource_group_name, cluster_rp, cluster_type, cluster_name)
    try:
        if cluster_rp.lower() == consts.HYBRIDCONTAINERSERVICE_RP:
            resource = resources.get_by_id(cluster_resource_id, consts.HYBRIDCONTAINERSERVICE_API_VERSION)
        else:
            resource = resources.get_by_id(cluster_resource_id, ClUSTER_RESOURCE_API)
        cluster_region = resource.location.lower()
    except HttpResponseError as ex:
        raise ex
    return cluster_region


def safe_key_check(key_to_check, strStrDict):
    if strStrDict is None or key_to_check is None:
        return False
    if key_to_check.lower() in [key.lower() for key in strStrDict.keys()]:
        return True
    return False


def safe_value_get(key_to_find, strStrDict):
    for key in strStrDict:
        if key.lower() == key_to_find.lower():
            return strStrDict[key]
    return ""
