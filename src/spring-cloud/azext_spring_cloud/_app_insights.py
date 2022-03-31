# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._utils import get_portal_uri
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient
from msrestazure.tools import parse_resource_id, is_valid_resource_id
from knack.log import get_logger

logger = get_logger(__name__)


def get_connection_string_from_exist_or_new_create_app_insights(cmd,
                                                                 resource_group,
                                                                 service_name,
                                                                 location,
                                                                 app_insights_key=None,
                                                                 app_insights=None):
    """
    To get connection string in order, and return after first condition met.
    1. From app_insights_key
    2. From app_insights_name
    3. Create an app insights, and get connection string from it
    """
    connection_string = app_insights_key or \
                        _get_connection_string_from_app_insights(cmd, resource_group, app_insights) or \
                        _create_app_insights_and_get_connection_string(cmd, resource_group, service_name, location)

    if not connection_string:
        raise InvalidArgumentValueError('Error while trying to get the ConnectionString of Application Insights for the Azure Spring Cloud. '
                                        'Please use the Azure Portal to create and configure the Application Insights, if needed.')


def _get_connection_string_from_app_insights(cmd, resource_group, app_insights):
    """Get connection string from:
    1) application insights name
    2) application insights resource id
    """

    if not app_insights:
        return None

    if is_valid_resource_id(app_insights):
        resource_id_dict = parse_resource_id(app_insights)
        connection_string = _get_app_insights_connection_string(
            cmd.cli_ctx, resource_id_dict['resource_group'], resource_id_dict['resource_name'])
    else:
        connection_string = _get_app_insights_connection_string(cmd.cli_ctx, resource_group, app_insights)

    if not connection_string:
        logger.warning(
            "Cannot find Connection string from application insights:{}".format(app_insights))

    return connection_string


def _get_app_insights_connection_string(cli_ctx, resource_group, name):
    appinsights_client = get_mgmt_service_client(cli_ctx, ApplicationInsightsManagementClient)
    appinsights = appinsights_client.components.get(resource_group, name)

    if not appinsights or not appinsights.connection_string:
        raise ResourceNotFoundError("App Insights {} under resource group {} was not found.".format(name, resource_group))

    return appinsights.connection_string


def _create_app_insights_and_get_connection_string(cmd, resource_group, service_name, location):

    try:
        created_app_insights = _try_create_application_insights(cmd, resource_group, service_name, location)
        if created_app_insights:
            return created_app_insights.connection_string
    except Exception:  # pylint: disable=broad-except
        logger.warning(
            'Error while trying to create and configure an Application Insights for the Azure Spring Cloud. '
            'Please use the Azure Portal to create and configure the Application Insights, if needed.')
    return None


def _try_create_application_insights(cmd, resource_group, name, location):
    creation_failed_warn = 'Unable to create the Application Insights for the Azure Spring Cloud. ' \
                           'Please use the Azure Portal to manually create and configure the Application Insights, ' \
                           'if needed.'

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
        logger.warning(creation_failed_warn)
        return None

    portal_url = get_portal_uri(cmd.cli_ctx)
    # We make this success message as a warning to no interfere with regular JSON output in stdout
    logger.warning('Application Insights \"%s\" was created for this Azure Spring Cloud. '
                   'You can visit %s/#resource%s/overview to view your '
                   'Application Insights component', appinsights.name, portal_url, appinsights.id)

    return appinsights
