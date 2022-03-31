# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._clierror import ApplicationInsightsNotFoundError
from azure.cli.core.azclierror import CLIInternalError
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient
from msrestazure.tools import parse_resource_id, is_valid_resource_id
from knack.log import get_logger

logger = get_logger(__name__)


def get_app_insights_connection_string(cmd, resource_group, app_insights):
    """Get connection string from:
    1) application insights name
    2) application insights resource id
    """

    if not app_insights:
        return None

    if is_valid_resource_id(app_insights):
        resource_id_dict = parse_resource_id(app_insights)
        connection_string = get_app_insights_connection_string_by_name(
            cmd.cli_ctx, resource_id_dict['resource_group'], resource_id_dict['resource_name'])
    else:
        connection_string = get_app_insights_connection_string_by_name(cmd.cli_ctx, resource_group, app_insights)

    if not connection_string:
        raise ApplicationInsightsNotFoundError("Cannot find Connection string from application insights:{}".format(app_insights))

    return connection_string


def get_app_insights_connection_string_by_name(cli_ctx, resource_group, name):
    appinsights_client = get_mgmt_service_client(cli_ctx, ApplicationInsightsManagementClient)
    appinsights = appinsights_client.components.get(resource_group, name)

    if not appinsights or not appinsights.connection_string:
        raise ApplicationInsightsNotFoundError("App Insights {} under resource group {} was not found.".format(name, resource_group))

    return appinsights.connection_string


def create_app_insights(cmd, resource_group, name, location):
    ai_resource_group_name = resource_group
    ai_name = name
    ai_location = location
    ai_properties = {
        "name": ai_name,
        "location": ai_location,
        "kind": "web",
        "properties": {
            "Application_Type": "web"
        }
    }

    app_insights_client = get_mgmt_service_client(cmd.cli_ctx, ApplicationInsightsManagementClient)
    appinsights = app_insights_client.components.create_or_update(ai_resource_group_name, ai_name, ai_properties)

    if not appinsights or not appinsights.connection_string:
        raise CLIInternalError('Unable to create the Application Insights for the Azure Spring Cloud.')

    return appinsights
