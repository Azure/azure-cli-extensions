# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.util import sdk_no_wait
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient
from knack.log import get_logger
from msrestazure.tools import parse_resource_id, is_valid_resource_id

from ._utils import get_portal_uri
from .custom import try_create_application_insights
from .vendored_sdks.appplatform.v2024_05_01_preview import models

logger = get_logger(__name__)
DEFAULT_APM_NAME = "default"


def create_or_update_apm(cmd, client, resource_group, service,
                         name, type, properties=None, secrets=None, no_wait=False):
    logger.warning('[1/1] Creating or updating APM, (this operation can take a while to complete).')
    apm_resource = _build_apm_resource(type, properties, secrets)
    return sdk_no_wait(no_wait, client.apms.begin_create_or_update, resource_group, service, name, apm_resource)


def apm_show(cmd, client, resource_group, service, name):
    apm_resource = client.apms.get(resource_group, service, name)
    secrets_keys = client.apms.list_secret_keys(resource_group, service, name)
    if secrets_keys and secrets_keys.value:
        secrets = {}
        for key in secrets_keys.value:
            secrets[key] = '*'

        apm_resource.properties.secrets = secrets

    return apm_resource


def apm_list(cmd, client, resource_group, service):
    return client.apms.list(resource_group, service)


def list_support_apm_types(cmd, client, resource_group, service):
    return client.services.list_supported_apm_types(resource_group, service)


def list_apms_enabled_globally(cmd, client, resource_group, service):
    return client.services.list_globally_enabled_apms(resource_group, service)


def enable_apm_globally(cmd, client, resource_group, service, name, no_wait=False):
    apm_resource = client.apms.get(resource_group, service, name)
    apm_reference = models.ApmReference(resource_id=apm_resource.id)
    return sdk_no_wait(no_wait, client.services.begin_enable_apm_globally, resource_group, service, apm_reference)


def disable_apm_globally(cmd, client, resource_group, service, name, no_wait=False):
    apm_resource = client.apms.get(resource_group, service, name)
    apm_reference = models.ApmReference(resource_id=apm_resource.id)
    return sdk_no_wait(no_wait, client.services.begin_disable_apm_globally, resource_group, service, apm_reference)


def apm_delete(cmd, client, resource_group, service, name, no_wait=False):
    logger.warning('[1/1] Deleting APM, (this operation can take a while to complete).')
    return sdk_no_wait(no_wait, client.apms.begin_delete, resource_group, service, name)


def create_default_apm_for_application_insights(cmd, client, resource_group, service_name, location,
                                                app_insights_key, app_insights, sampling_rate):
    logger.warning("Start configure Application Insights")
    apm_resource = models.ApmResource()
    apm_resource.properties = _get_apm_properties(cmd, resource_group, service_name, location, app_insights_key,
                                                  app_insights,
                                                  sampling_rate)

    if apm_resource.properties:
        return client.apms.begin_create_or_update(resource_group, service_name, DEFAULT_APM_NAME, apm_resource)


def _build_apm_resource(type, properties_dict, secrets_dict):
    apm_properties = models.ApmProperties(type=type, properties=properties_dict, secrets=secrets_dict)

    return models.ApmResource(properties=apm_properties)


def _get_apm_properties(cmd, resource_group, service_name, location,
                        app_insights_key, app_insights, sampling_rate):
    connection_string = _get_connection_string(cmd, resource_group, service_name, location, app_insights_key,
                                               app_insights)

    if not connection_string:
        return None

    sampling_rate = sampling_rate or 10

    return models.ApmProperties(type="ApplicationInsights", properties={
        "connection-string": connection_string,
        "sampling-percentage": sampling_rate,
    })


def _get_connection_string(cmd, resource_group, service_name, location, app_insights_key, app_insights):
    return app_insights_key or \
        _get_connection_string_from_app_insights(cmd, resource_group, app_insights) or \
        _create_app_insights_and_get_connection_string(cmd, resource_group, service_name, location)


def _create_app_insights_and_get_connection_string(cmd, resource_group, service_name, location):
    try:
        created_app_insights = try_create_application_insights(cmd, resource_group, service_name, location)
        if created_app_insights:
            return created_app_insights.connection_string
    except Exception:  # pylint: disable=broad-except
        logger.warning(
            'Error while trying to create and configure an Application Insights for the Azure Spring Apps. '
            'Please use the Azure Portal to create and configure the Application Insights, if needed.')
    return None


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

    # Customer has specify the resourceId or application insights name.
    # Raise exception when connection string not found in this scenario.
    if not connection_string:
        raise InvalidArgumentValueError(
            "Cannot find Connection string from application insights:{}".format(app_insights))

    return connection_string


def _get_app_insights_connection_string(cli_ctx, resource_group, name):
    appinsights_client = get_mgmt_service_client(cli_ctx, ApplicationInsightsManagementClient)
    appinsights = appinsights_client.components.get(resource_group, name)

    if not appinsights or not appinsights.connection_string:
        raise ResourceNotFoundError(
            "Application Insights {} under resource group {} was not found.".format(name, resource_group))

    return appinsights.connection_string
