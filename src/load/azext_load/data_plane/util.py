# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from datetime import datetime
import dateutil.parser  # pylint: disable=import-error
from knack.log import get_logger
from msrestazure.tools import is_valid_resource_id, parse_resource_id
from azext_load.vendored_sdks.loadtesting_mgmt import LoadTestMgmtClient

logger = get_logger(__name__)


def get_load_test_resource_endpoint(
    cred, load_test_resource, resource_group=None, subscription_id=None
):
    if subscription_id is None:
        return None
    if is_valid_resource_id(load_test_resource):
        # load_test_resource is a resource id
        logger.debug(
            "load-test-resource '%s' is an Azure Resource Id", load_test_resource
        )
        parsed = parse_resource_id(load_test_resource)
        resource_group, name = parsed["resource_group"], parsed["name"]
        if subscription_id != parsed["subscription"]:
            logger.info(
                "Subscription ID in load-test-resource parameter and CLI context do not match - %s and %s",
                subscription_id,
                parsed["subscription"],
            )
            return None
    else:
        # load_test_resource is a name
        logger.debug(
            "load-test-resource '%s' is an Azure Load Testing resource name. Using resource group name %s",
            load_test_resource,
            resource_group,
        )
        if resource_group is None:
            return None
        name = load_test_resource

    mgmt_client = LoadTestMgmtClient(credential=cred, subscription_id=subscription_id)
    data_plane_uri = mgmt_client.load_tests.get(resource_group, name).data_plane_uri
    logger.info("Azure Load Testing data plane URI: %s", data_plane_uri)
    return data_plane_uri


def get_timespan(_, start_time=None, end_time=None, offset=None):
    if not start_time and not end_time:
        # if neither value provided, end_time is now
        end_time = datetime.utcnow().isoformat()
    if not start_time:
        # if no start_time, apply offset backwards from end_time
        start_time = (dateutil.parser.parse(end_time) - offset).isoformat()
    elif not end_time:
        # if no end_time, apply offset fowards from start_time
        end_time = (dateutil.parser.parse(start_time) + offset).isoformat()
    timespan = f"{start_time}/{end_time}"
    return timespan


def get_login_credentials(cli_ctx, subscription_id=None):
    from azure.cli.core._profile import Profile

    credential = Profile(cli_ctx=cli_ctx).get_login_credentials(
        subscription_id=subscription_id
    )
    logger.debug("Fetched login credentials for subscription %s", subscription_id)
    return credential
