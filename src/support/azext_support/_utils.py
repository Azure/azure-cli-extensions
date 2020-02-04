# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re

from azure.cli.core._profile import Profile
from knack.log import get_logger
from knack.util import CLIError

logger = get_logger(__name__)


def is_billing_ticket(service_name):
    return "517f2da6-78fd-0498-4e22-ad26996b1dfc" in service_name


def is_quota_ticket(service_name):
    return "06bfd9d3-516b-d5c6-5802-169c800dec89" in service_name


def is_subscription_mgmt_ticket(service_name):
    return "f3dc5421-79ef-1efa-41a5-42bf3cbb52c6" in service_name


def is_technical_ticket(service_name):
    return (not is_billing_ticket(service_name)) and \
           (not is_quota_ticket(service_name)) and \
           (not is_subscription_mgmt_ticket(service_name))


def parse_support_area_path(problem_classification_id):
    service_id_prefix = "/providers/Microsoft.Support/services/".lower()
    guid_regex = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    sap_regex = re.compile('^{0}({1})/problemclassifications/({1})$'.format(service_id_prefix, guid_regex))
    match = sap_regex.search(problem_classification_id.lower())

    if match is not None and len(match.groups()) == 2:
        return {"service_name": match.group(1), "problem_classifications_name": match.group(2)}

    return None


def get_bearer_token(cmd, tenant_id):
    client = Profile(cli_ctx=cmd.cli_ctx)

    try:
        logger.debug("Retrieving access token for tenant %s", tenant_id)
        creds, _, _ = client.get_raw_token(tenant=tenant_id)
    except CLIError:
        raise CLIError("Can't find authorization for {0}. ".format(tenant_id) +
                       "Run \'az login -t <tenant_name> --allow-no-subscriptions\' and try again.")

    return "Bearer " + creds[1]
