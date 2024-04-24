# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order
from .vendored_sdks.appplatform.v2024_05_01_preview import models
from azure.cli.core.util import sdk_no_wait
from ._utils import get_portal_uri
from .custom import try_create_application_insights
from msrestazure.tools import parse_resource_id, is_valid_resource_id
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient
from azure.core.exceptions import ResourceNotFoundError
from knack.log import get_logger

logger = get_logger(__name__)

DEFAULT_BUILDER_NAME = "default"
DEFAULT_BINDING_NAME = "default"
DEFAULT_BUILD_SERVICE_NAME = "default"


def create_or_update_buildpack_binding(cmd, client, resource_group, service,
                                       name, type, builder_name=None, properties=None, secrets=None):
    logger.warning('Editing bindings will regenerate images for all app deployments using this builder. These new images will ' +
                   'be used after app restart either manually by yourself or automatically by Azure Spring Apps in regular maintenance tasks. ' +
                   'Use CLI command --"az spring build-service builder show-deployments" to view the app deployment list of the builder.')
    if not builder_name:
        builder_name = DEFAULT_BUILDER_NAME
        logger.warning('Option --builder-name is not provided, will use default builder name "{}".'.format(builder_name))

    logger.warning('[1/1] Creating or updating to buildpack binding for builder "{}", (this operation can take a while to complete).'.format(builder_name))

    binding_resource = _build_buildpack_binding_resource(type, properties, secrets)
    return sdk_no_wait(False, client.buildpack_binding.begin_create_or_update, resource_group,
                       service, DEFAULT_BUILD_SERVICE_NAME, builder_name, name, binding_resource)


def buildpack_binding_show(cmd, client, resource_group, service, name, builder_name=None):
    if not builder_name:
        builder_name = DEFAULT_BUILDER_NAME
        logger.warning('Option --builder-name is not provided, will use default builder name "{}".'.format(builder_name))

    return client.buildpack_binding.get(resource_group, service, DEFAULT_BUILD_SERVICE_NAME,
                                        builder_name, name)


def buildpack_binding_list(cmd, client, resource_group, service, builder_name=None):
    if not builder_name:
        builder_name = DEFAULT_BUILDER_NAME
        logger.warning('Option --builder-name is not provided, will use default builder name "{}".'.format(builder_name))

    return client.buildpack_binding.list(resource_group, service, DEFAULT_BUILD_SERVICE_NAME, builder_name)


def buildpack_binding_delete(cmd, client, resource_group, service, name, builder_name=None):
    logger.warning('Deleting bindings will regenerate images for all app deployments using this builder. These new images will ' +
                   'be used after app restart either manually by yourself or automatically by Azure Spring Apps in regular maintenance tasks. ' +
                   'Use CLI command --"az spring build-service builder show-deployments" to view the app deployment list of the builder.')
    if not builder_name:
        builder_name = DEFAULT_BUILDER_NAME
        logger.warning('Option --builder-name is not provided, will use default builder name "{}".'.format(builder_name))

    logger.warning('[1/1] Deleting buildpack binding for builder "{}", (this operation can take a while to complete).'.format(builder_name))

    return sdk_no_wait(False, client.buildpack_binding.begin_delete, resource_group,
                       service, DEFAULT_BUILD_SERVICE_NAME, builder_name, name)


def create_default_buildpack_binding_for_application_insights(cmd, client, resource_group, name, location,
                                                              app_insights_key, app_insights, sampling_rate):
    logger.warning("Start configure Application Insights")
    binding_resource = models.BuildpackBindingResource()
    binding_resource.properties = _get_buildpack_binding_properties(cmd, resource_group, name, location, app_insights_key, app_insights, sampling_rate)

    if binding_resource.properties:
        return client.buildpack_binding.begin_create_or_update(resource_group, name, DEFAULT_BUILD_SERVICE_NAME,
                                                               DEFAULT_BUILDER_NAME, DEFAULT_BINDING_NAME, binding_resource)


def _build_buildpack_binding_resource(binding_type, properties_dict, secrets_dict):
    launch_properties = models.BuildpackBindingLaunchProperties(properties=properties_dict,
                                                                secrets=secrets_dict)
    binding_properties = models.BuildpackBindingProperties(binding_type=binding_type,
                                                           launch_properties=launch_properties)
    return models.BuildpackBindingResource(properties=binding_properties)


def _get_buildpack_binding_properties(cmd, resource_group, service_name, location,
                                      app_insights_key, app_insights, sampling_rate):
    connection_string = _get_connection_string(cmd, resource_group, service_name, location, app_insights_key, app_insights)

    if not connection_string:
        return None

    sampling_rate = sampling_rate or 10
    launch_properties = models.BuildpackBindingLaunchProperties(properties={
        "connection-string": connection_string,
        "sampling-percentage": sampling_rate,
    })

    return models.BuildpackBindingProperties(binding_type="ApplicationInsights", launch_properties=launch_properties)


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
        raise ResourceNotFoundError("App Insights {} under resource group {} was not found.".format(name, resource_group))

    return appinsights.connection_string
