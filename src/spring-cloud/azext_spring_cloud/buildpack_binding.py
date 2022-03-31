# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order
from .vendored_sdks.appplatform.v2022_01_01_preview import models
from ._app_insights import create_app_insights
from azure.cli.core.util import sdk_no_wait
from knack.log import get_logger

logger = get_logger(__name__)

DEFAULT_BUILDER_NAME = "default"
DEFAULT_BINDING_NAME = "default"
DEFAULT_BUILD_SERVICE_NAME = "default"


def create_or_update_buildpack_binding(cmd, client, resource_group, service,
                                       name, type, builder_name=None, properties=None, secrets=None):
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
    creation_failed_warn = 'Unable to create the Application Insights for the Azure Spring Cloud. ' \
                           'Please use the Azure Portal to manually create and configure the Application Insights, ' \
                           'if needed.'

    sampling_rate = sampling_rate or 10
    connection_string = _safe_get_connection_string(cmd, resource_group, service_name, location, app_insights_key)
    if not connection_string:
        return None

    launch_properties = models.BuildpackBindingLaunchProperties(properties={
        "connection-string": connection_string,
        "sampling-percentage": sampling_rate,
    })

    return models.BuildpackBindingProperties(binding_type="ApplicationInsights", launch_properties=launch_properties)


def _safe_get_connection_string(cmd, resource_group, service_name, location, app_insights_key):
    connection_string = app_insights_key
    if not connection_string:
        try:
            app_insights = create_app_insights(cmd, resource_group, service_name, location)
            connection_string = app_insights.connection_string
            portal_url = get_portal_uri(cmd.cli_ctx)
            # We make this success message as a warning to no interfere with regular JSON output in stdout
            logger.warning('Application Insights \"%s\" was created for this Azure Spring Cloud. '
                           'You can visit %s/#resource%s/overview to view your '
                           'Application Insights component', appinsights.name, portal_url, appinsights.id)
        except Exception:
            logger.warning(creation_failed_warn)
            return None
    return connection_string
