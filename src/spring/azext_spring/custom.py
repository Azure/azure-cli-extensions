# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument, logging-format-interpolation, protected-access, wrong-import-order, too-many-lines
import logging
import requests
import re
import os
import time
from azure.cli.core._profile import Profile
from azure.core.exceptions import HttpResponseError
from azure.mgmt.loganalytics import LogAnalyticsManagementClient

from ._websocket import WebSocketConnection, recv_remote, send_stdin, EXEC_PROTOCOL_CTRL_C_MSG
from azure.mgmt.cosmosdb import CosmosDBManagementClient
from azure.mgmt.redis import RedisManagementClient
from requests.auth import HTTPBasicAuth
import yaml  # pylint: disable=import-error
from time import sleep
from ._stream_utils import stream_logs
from azure.mgmt.core.tools import (parse_resource_id, is_valid_resource_id)
from ._utils import (get_portal_uri, get_spring_sku, get_proxy_api_endpoint, BearerAuth)
from knack.util import CLIError
from .vendored_sdks.appplatform.v2024_05_01_preview import models, AppPlatformManagementClient
from knack.log import get_logger
from azure.cli.core.azclierror import ClientRequestError, FileOperationError, InvalidArgumentValueError, ResourceNotFoundError
from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_subscription_id
from azure.cli.core.util import sdk_no_wait
from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient
from azure.cli.core.commands import cached_put
from ._resource_quantity import validate_cpu, validate_memory
from six.moves.urllib import parse
from threading import Thread
import sys
import json
import base64
from collections import defaultdict
from ._log_stream import LogStream
from ._build_service import _update_default_build_agent_pool
from .log_stream.log_stream_operations import log_stream_from_url

logger = get_logger(__name__)
DEFAULT_DEPLOYMENT_NAME = "default"
DEPLOYMENT_CREATE_OR_UPDATE_SLEEP_INTERVAL = 5
APP_CREATE_OR_UPDATE_SLEEP_INTERVAL = 2

# pylint: disable=line-too-long
NO_PRODUCTION_DEPLOYMENT_ERROR = "No production deployment found, use --deployment to specify deployment or create deployment with: az spring app deployment create"
NO_PRODUCTION_DEPLOYMENT_SET_ERROR = "This app has no production deployment, use \"az spring app deployment create\" to create a deployment and \"az spring app set-deployment\" to set production deployment."
DELETE_PRODUCTION_DEPLOYMENT_WARNING = "You are going to delete production deployment, the app will be inaccessible after this operation."
LOG_RUNNING_PROMPT = "This command usually takes minutes to run. Add '--verbose' parameter if needed."
APP_INSIGHTS_CREATION_FAILURE_WARNING = 'Unable to create the Application Insights for the Azure Spring Apps. ' \
                                        'Please use the Azure Portal to manually create and configure the Application Insights, if needed.'


def _warn_enable_java_agent(enable_java_agent, **_):
    if enable_java_agent is not None:
        logger.warn("Java in process agent is now GA-ed and used by default when Application Insights enabled. "
                    "The parameter '--enable-java-agent' is no longer needed and will be removed in future release.")


def _update_application_insights_asc_create(cmd,
                                            resource_group,
                                            name,
                                            location,
                                            app_insights_key=None,
                                            app_insights=None,
                                            sampling_rate=None,
                                            disable_app_insights=None,
                                            no_wait=None,
                                            **_):
    monitoring_setting_resource = models.MonitoringSettingResource()
    if disable_app_insights is not True:
        client_preview = get_mgmt_service_client(cmd.cli_ctx, AppPlatformManagementClient)
        logger.warning("Start configure Application Insights")
        monitoring_setting_properties = update_java_agent_config(
            cmd, resource_group, name, location, app_insights_key, app_insights, sampling_rate)
        if monitoring_setting_properties is not None:
            monitoring_setting_resource.properties = monitoring_setting_properties
            sdk_no_wait(no_wait, client_preview.monitoring_settings.begin_update_put,
                        resource_group_name=resource_group, service_name=name,
                        monitoring_setting_resource=monitoring_setting_resource)


def spring_update(cmd, client, resource_group, name, app_insights_key=None, app_insights=None,
                  disable_app_insights=None, sku=None, tags=None, build_pool_size=None,
                  enable_log_stream_public_endpoint=None, enable_dataplane_public_endpoint=None,
                  ingress_read_timeout=None, enable_planned_maintenance=False, planned_maintenance_day=None,
                  planned_maintenance_start_hour=None, no_wait=False):
    """
    TODO (jiec) app_insights_key, app_insights and disable_app_insights are marked as deprecated.
    Will be decommissioned in future releases.
    :param app_insights_key: Connection string or Instrumentation key
    """
    updated_resource = models.ServiceResource()
    update_service_tags = False
    update_service_sku = False
    update_dataplane_public_endpoint = False

    # update service sku
    if sku is not None:
        updated_resource.sku = sku
        update_service_sku = True

    resource = client.services.get(resource_group, name)
    location = resource.location
    updated_resource_properties = models.ClusterResourceProperties()
    updated_resource_properties.zone_redundant = None

    if enable_log_stream_public_endpoint is not None or enable_dataplane_public_endpoint is not None:
        val = enable_log_stream_public_endpoint if enable_log_stream_public_endpoint is not None else \
            enable_dataplane_public_endpoint
        updated_resource_properties.vnet_addons = models.ServiceVNetAddons(
            data_plane_public_endpoint=val,
            log_stream_public_endpoint=val
        )
        update_dataplane_public_endpoint = True
    else:
        updated_resource_properties.vnet_addons = None

    _update_application_insights_asc_update(cmd, resource_group, name, location,
                                            app_insights_key, app_insights, disable_app_insights, no_wait)

    _update_default_build_agent_pool(
        cmd, client, resource_group, name, build_pool_size)

    _update_ingress_config(updated_resource_properties, ingress_read_timeout)

    # update planned maintenance
    update_planned_maintenance, updated_resource_properties.maintenance_schedule_configuration = _update_planned_maintenance(
        legacy_configuration=resource.properties.maintenance_schedule_configuration,
        enable_planned_maintenance=enable_planned_maintenance,
        planned_maintenance_day=planned_maintenance_day,
        planned_maintenance_start_hour=planned_maintenance_start_hour
    )

    # update service tags
    if tags is not None:
        updated_resource.tags = tags
        update_service_tags = True

    if update_service_tags is False and update_service_sku is False and update_dataplane_public_endpoint is False \
            and update_planned_maintenance is False and ingress_read_timeout is None:
        return resource

    updated_resource.properties = updated_resource_properties
    return sdk_no_wait(no_wait, client.services.begin_update,
                       resource_group_name=resource_group, service_name=name, resource=updated_resource)


def _update_ingress_config(updated_resource_properties, ingress_read_timeout=None):
    if ingress_read_timeout:
        ingress_configuration = models.IngressConfig(read_timeout_in_seconds=ingress_read_timeout)
        updated_resource_properties.network_profile = models.NetworkProfile(
            ingress_config=ingress_configuration)


def _update_application_insights_asc_update(cmd, resource_group, name, location,
                                            app_insights_key, app_insights, disable_app_insights, no_wait):
    """If app_insights_key, app_insights and disable_app_insights are all None, do nothing here
    """
    update_app_insights = False
    app_insights_target_status = False

    client_preview = get_mgmt_service_client(cmd.cli_ctx, AppPlatformManagementClient)
    monitoring_setting_properties = client_preview.monitoring_settings.get(resource_group, name).properties
    trace_enabled = monitoring_setting_properties.trace_enabled if monitoring_setting_properties is not None else False

    if app_insights or app_insights_key or disable_app_insights is False:
        app_insights_target_status = True
        if trace_enabled is False:
            update_app_insights = True
        elif app_insights or (
                app_insights_key and app_insights_key != monitoring_setting_properties.app_insights_instrumentation_key):
            update_app_insights = True
    elif disable_app_insights is True:
        app_insights_target_status = False
        if trace_enabled is True:
            update_app_insights = True

    # update application insights
    if update_app_insights is True:
        if app_insights_target_status is False:
            monitoring_setting_properties = models.MonitoringSettingProperties(trace_enabled=False)
        elif monitoring_setting_properties.app_insights_instrumentation_key and not app_insights and not app_insights_key:
            monitoring_setting_properties.trace_enabled = app_insights_target_status
        else:
            monitoring_setting_properties = update_java_agent_config(
                cmd, resource_group, name, location, app_insights_key, app_insights, None)
        if monitoring_setting_properties is not None:
            monitoring_setting_resource = models.MonitoringSettingResource(properties=monitoring_setting_properties)
            sdk_no_wait(no_wait, client_preview.monitoring_settings.begin_update_put,
                        resource_group_name=resource_group, service_name=name,
                        monitoring_setting_resource=monitoring_setting_resource)


def _update_planned_maintenance(legacy_configuration, enable_planned_maintenance=False, planned_maintenance_day=None,
                                planned_maintenance_start_hour=None):
    if enable_planned_maintenance is True:
        if planned_maintenance_day is None or planned_maintenance_start_hour is None:
            return False, legacy_configuration
        return True, models.WeeklyMaintenanceScheduleConfiguration(
            day=planned_maintenance_day,
            hour=planned_maintenance_start_hour
        )
    return False, legacy_configuration


def spring_delete(cmd, client, resource_group, name, no_wait=False):
    logger.warning("Stop using Azure Spring Apps? We appreciate your feedback: https://aka.ms/asa_exitsurvey")
    return sdk_no_wait(no_wait, client.services.begin_delete, resource_group_name=resource_group, service_name=name)


def spring_start(cmd, client, resource_group, name, no_wait=False):
    resource = client.services.get(resource_group, name)
    state = resource.properties.provisioning_state
    power_state = resource.properties.power_state
    if state != "Succeeded" or power_state != "Stopped":
        raise ClientRequestError("Service is in Provisioning State({}) and Power State({}), starting cannot be performed.".format(state, power_state))
    return sdk_no_wait(no_wait, client.services.begin_start, resource_group_name=resource_group, service_name=name)


def spring_stop(cmd, client, resource_group, name, no_wait=False):
    resource = client.services.get(resource_group, name)
    state = resource.properties.provisioning_state
    power_state = resource.properties.power_state
    if state != "Succeeded" or power_state != "Running":
        raise ClientRequestError("Service is in Provisioning State({}) and Power State({}), stopping cannot be performed.".format(state, power_state))
    return sdk_no_wait(no_wait, client.services.begin_stop, resource_group_name=resource_group, service_name=name)


def spring_flush_vnet_dns_setting(cmd, client, resource_group, name, no_wait=False):
    resource = client.services.get(resource_group, name)
    state = resource.properties.provisioning_state
    power_state = resource.properties.power_state
    if state != "Succeeded" or power_state != "Running":
        raise ClientRequestError("Service is in Provisioning State({}) and Power State({}), flush vnet dns setting cannot be performed.".format(state, power_state))
    return sdk_no_wait(no_wait, client.services.begin_flush_vnet_dns_setting, resource_group_name=resource_group, service_name=name)


def spring_list(cmd, client, resource_group=None):
    if resource_group is None:
        return client.services.list_by_subscription()
    return client.services.list(resource_group)


def spring_get(cmd, client, resource_group, name):
    return client.services.get(resource_group, name)


def enable_test_endpoint(cmd, client, resource_group, name):
    return client.services.enable_test_endpoint(resource_group, name)


def disable_test_endpoint(cmd, client, resource_group, name):
    return client.services.disable_test_endpoint(resource_group, name)


def list_keys(cmd, client, resource_group, name, app=None, deployment=None):
    keys = client.services.list_test_keys(resource_group, name)
    if not keys.enabled:
        return None
    if app:
        deployment_resource = deployment_get(cmd, client, resource_group, name, app, deployment) \
            if deployment else app_get(cmd, client, resource_group, name, app).properties.active_deployment
        if deployment_resource:
            keys.primary_test_endpoint = "{}/{}/{}/".format(keys.primary_test_endpoint, app, deployment_resource.name)
            keys.secondary_test_endpoint = "{}/{}/{}/".format(keys.secondary_test_endpoint, app, deployment_resource.name)
    return keys


# pylint: disable=redefined-builtin
def regenerate_keys(cmd, client, resource_group, name, type):
    return client.services.regenerate_test_key(resource_group, name,
                                               models.RegenerateTestKeyRequestPayload(key_type=type))


def app_append_persistent_storage(cmd, client, resource_group, service, name,
                                  storage_name,
                                  persistent_storage_type,
                                  mount_path,
                                  share_name=None,
                                  mount_options=None,
                                  read_only=None,
                                  enable_sub_path=None):
    resource = client.services.get(resource_group, service)
    storage_id = None
    if resource.sku.tier.upper() == 'STANDARDGEN2':
        storage_id = storage_name
    else:
        storage_resource = client.storages.get(resource_group, service, storage_name)
        storage_id = storage_resource.id

    app = client.apps.get(resource_group, service, name)

    custom_persistent_disks = []
    if app.properties.custom_persistent_disks:
        for disk in app.properties.custom_persistent_disks:
            custom_persistent_disks.append(disk)

    custom_persistent_disk_properties = models.AzureFileVolume(
        type=persistent_storage_type,
        share_name=share_name,
        mount_path=mount_path,
        mount_options=mount_options,
        read_only=read_only,
        enable_sub_path=enable_sub_path)

    custom_persistent_disks.append(
        models.CustomPersistentDiskResource(
            storage_id=storage_id,
            custom_persistent_disk_properties=custom_persistent_disk_properties))

    app.properties.custom_persistent_disks = custom_persistent_disks
    app.properties.secrets = None
    logger.warning("[1/1] updating app '{}'".format(name))

    poller = client.apps.begin_update(
        resource_group, service, name, app)
    while poller.done() is False:
        sleep(APP_CREATE_OR_UPDATE_SLEEP_INTERVAL)

    app_updated = client.apps.get(resource_group, service, name)
    return app_updated


def app_delete(cmd, client,
               resource_group,
               service,
               name):
    client.apps.get(resource_group, service, name)
    return client.apps.begin_delete(resource_group, service, name)


def app_start(cmd, client,
              resource_group,
              service,
              name,
              deployment=None,
              no_wait=False):
    logger.warning("Successfully triggered the action 'start' for the app '{}'".format(name))
    return sdk_no_wait(no_wait, client.deployments.begin_start,
                       resource_group, service, name, deployment.name)


def app_stop(cmd, client,
             resource_group,
             service,
             name,
             deployment=None,
             no_wait=False):
    logger.warning("Successfully triggered the action 'stop' for the app '{}'".format(name))
    return sdk_no_wait(no_wait, client.deployments.begin_stop,
                       resource_group, service, name, deployment.name)


def deployment_enable_remote_debugging(cmd, client, resource_group, service, name, remote_debugging_port=None, deployment=None, no_wait=False):
    logger.warning("Enable remote debugging for the app '{}', deployment '{}'".format(name, deployment.name))
    remote_debugging_payload = models.RemoteDebuggingPayload(port=remote_debugging_port)
    return sdk_no_wait(no_wait, client.deployments.begin_enable_remote_debugging,
                       resource_group, service, name, deployment.name, remote_debugging_payload)


def deployment_disable_remote_debugging(cmd, client, resource_group, service, name, deployment=None, no_wait=False):
    logger.warning("Disable remote debugging for the app '{}', deployment '{}'".format(name, deployment.name))
    return sdk_no_wait(no_wait, client.deployments.begin_disable_remote_debugging,
                       resource_group, service, name, deployment.name)


def deployment_get_remote_debugging(cmd, client, resource_group, service, name, deployment=None):
    return client.deployments.get_remote_debugging_config(resource_group, service, name, deployment.name)


def app_restart(cmd, client,
                resource_group,
                service,
                name,
                deployment=None,
                no_wait=False):
    logger.warning("Successfully triggered the action 'restart' for the app '{}'".format(name))
    return sdk_no_wait(no_wait, client.deployments.begin_restart,
                       resource_group, service, name, deployment.name)


def app_list(cmd, client,
             resource_group,
             service):
    apps = list(client.apps.list(resource_group, service))
    deployments = list(
        client.deployments.list_for_cluster(resource_group, service))
    for app in apps:
        app.properties.active_deployment = next(iter(x for x in deployments
                                                if x.properties.active and x.id.startswith(app.id + '/deployments/')), None)
    return apps


def app_get(cmd, client,
            resource_group,
            service,
            name):
    app = client.apps.get(resource_group, service, name)
    deployments = client.deployments.list(resource_group, service, name)
    app.properties.active_deployment = next((x for x in deployments if x.properties.active), None)
    if not app.properties.active_deployment:
        logger.warning(NO_PRODUCTION_DEPLOYMENT_SET_ERROR)

    return app


def app_scale(cmd, client, resource_group, service, name,
              deployment=None,
              cpu=None,
              memory=None,
              instance_count=None,
              # StandardGen2
              min_replicas=None,
              max_replicas=None,
              scale_rule_name=None,
              scale_rule_type=None,
              scale_rule_http_concurrency=None,
              scale_rule_metadata=None,
              scale_rule_auth=None,
              no_wait=False):
    cpu = validate_cpu(cpu)
    memory = validate_memory(memory)

    resource = client.services.get(resource_group, service)
    _validate_instance_count(resource.sku.tier, instance_count)

    resource_requests = models.ResourceRequests(cpu=cpu, memory=memory)
    scale_def = format_scale(min_replicas, max_replicas, scale_rule_name, scale_rule_type, scale_rule_http_concurrency,
                             scale_rule_metadata, scale_rule_auth)
    deployment_settings = models.DeploymentSettings(resource_requests=resource_requests, scale=scale_def)
    properties = models.DeploymentResourceProperties(
        deployment_settings=deployment_settings)
    sku = models.Sku(name="S0", tier="STANDARD", capacity=instance_count)
    deployment_resource = models.DeploymentResource(properties=properties, sku=sku)
    return sdk_no_wait(no_wait, client.deployments.begin_update,
                       resource_group, service, name, deployment.name, deployment_resource)


def format_scale(min_replicas=None, max_replicas=None, scale_rule_name=None, scale_rule_type=None,
                 scale_rule_http_concurrency=None, scale_rule_metadata=None, scale_rule_auth=None, **_):
    scale_def = None
    if min_replicas is None and max_replicas is None and scale_rule_name is None:
        return scale_def
    scale_def = models.Scale(min_replicas=min_replicas, max_replicas=max_replicas)
    if scale_rule_name:
        scale_rule_def = None
        if not scale_rule_type:
            scale_rule_type = "http"
        scale_rule_type = scale_rule_type.lower()
        curr_metadata = {}
        if scale_rule_http_concurrency:
            if scale_rule_type in ('http', 'tcp'):
                curr_metadata["concurrentRequests"] = str(scale_rule_http_concurrency)
        metadata_def = parse_metadata_flags(scale_rule_metadata, curr_metadata)
        auth_def = parse_auth_flags(scale_rule_auth)

        if scale_rule_type == "http":
            http_scale_rule = models.HttpScaleRule(metadata=metadata_def, auth=auth_def)
            scale_rule_def = models.ScaleRule(name=scale_rule_name, http=http_scale_rule)
        else:
            custom_scale_rule = models.CustomScaleRule(type=scale_rule_type, metadata=metadata_def, auth=auth_def)
            scale_rule_def = models.ScaleRule(name=scale_rule_name, custom=custom_scale_rule)
        scale_def.rules = [scale_rule_def]
    return scale_def


def parse_metadata_flags(metadata_list, metadata_def):
    if not metadata_list:
        return metadata_def
    for pair in metadata_list:
        key_val = pair.split('=', 1)
        if len(key_val) != 2:
            raise InvalidArgumentValueError("Metadata must be in format \"<key>=<value> <key>=<value> ...\".")
        if key_val[0] in metadata_def:
            raise InvalidArgumentValueError("Duplicate metadata \"{metadata}\" found, metadata keys must be unique.".format(
                metadata=key_val[0]))
        metadata_def[key_val[0]] = key_val[1]

    return metadata_def


def parse_auth_flags(auth_list):
    auth_def = []
    auth_pairs = {}
    if not auth_list:
        return auth_def
    for pair in auth_list:
        key_val = pair.split('=', 1)
        if len(key_val) != 2:
            raise InvalidArgumentValueError(
                "Auth parameters must be in format \"<triggerParameter>=<secretRef> <triggerParameter>=<secretRef> ...\".")
        if key_val[0] in auth_pairs:
            raise InvalidArgumentValueError(
                "Duplicate trigger parameter \"{param}\" found, trigger paramaters must be unique.".format(
                    param=key_val[0]))
        auth_pairs[key_val[0]] = key_val[1]

    for key, value in auth_pairs.items():
        auth_def.append(
            models.ScaleRuleAuth(trigger_parameter=key, secret_ref=value)
        )

    return auth_def


def app_get_build_log(cmd, client, resource_group, service, name, deployment=None):
    if deployment.properties.source.type != "Source":
        raise CLIError("{} deployment has no build logs.".format(deployment.properties.source.type))
    return stream_logs(client.deployments, resource_group, service, name, deployment.name)


def app_tail_log(cmd, client, resource_group, service, name,
                 deployment=None, instance=None, follow=False, lines=50, since=None, limit=2048, format_json=None):
    app_tail_log_internal(cmd, client, resource_group, service, name, deployment, instance, follow, lines, since, limit,
                          format_json, get_app_log=log_stream_from_url)


def app_tail_log_internal(cmd, client, resource_group, service, name,
                          deployment=None, instance=None, follow=False, lines=50, since=None, limit=2048,
                          format_json=None, timeout=None, get_app_log=None):
    if not instance:
        if not deployment.properties.instances:
            raise CLIError("No instances found for deployment '{0}' in app '{1}'".format(
                deployment.name, name))
        instances = deployment.properties.instances
        if len(instances) > 1:
            logger.warning("Multiple app instances found:")
            for temp_instance in instances:
                logger.warning("{}".format(temp_instance.name))
            logger.warning("Please use '-i/--instance' parameter to specify the instance name")
            return None
        instance = instances[0].name

    resource = client.services.get(resource_group, service)
    if resource.sku.tier.upper() == 'STANDARDGEN2':
        profile = Profile(cli_ctx=cmd.cli_ctx)
        creds, _, tenant = profile.get_raw_token()
        token = creds[1]
        subscriptionId = get_subscription_id(cmd.cli_ctx)
        hostname = get_proxy_api_endpoint(cmd.cli_ctx, resource)
        streaming_url = "https://{}/proxy/logstream/subscriptions/{}/resourceGroups/{}/providers/Microsoft.AppPlatform/Spring/{}/apps/{}/deployments/{}/instances/{}".format(
            hostname, subscriptionId, resource_group, service, name, deployment.name, instance)
        params = {}
        params["tailLines"] = lines
        params["tenantId"] = tenant
        if follow:
            params["follow"] = True
        format_json = None
        auth = BearerAuth(token)
    else:
        log_stream = LogStream(client, resource_group, service)
        if not log_stream:
            raise CLIError("To use the log streaming feature, please enable the test endpoint by running 'az spring test-endpoint enable -n {0} -g {1}'".format(service, resource_group))
        streaming_url = "https://{0}/api/logstream/apps/{1}/instances/{2}".format(
            log_stream.base_url, name, instance)
        params = {}
        params["tailLines"] = lines
        params["limitBytes"] = limit
        if since:
            params["sinceSeconds"] = since
        if follow:
            params["follow"] = True
        auth = HTTPBasicAuth("primary", log_stream.primary_key)

    exceptions = []
    streaming_url += "?{}".format(parse.urlencode(params)) if params else ""
    t = Thread(target=get_app_log, args=(
        streaming_url, auth, format_json, exceptions))
    t.daemon = True
    t.start()

    if timeout:
        t.join(timeout=timeout)
    else:
        while t.is_alive():
            sleep(5)  # so that ctrl+c can stop the command

    if exceptions:
        raise exceptions[0]


def app_set_deployment(cmd, client, resource_group, service, name, deployment):
    return _set_active_in_preview_api(cmd, client, resource_group, service, name, deployment)


def app_unset_deployment(cmd, client, resource_group, service, name):
    return _set_active_in_preview_api(cmd, client, resource_group, service, name)


def _set_active_in_preview_api(cmd, client, resource_group, service, name, deployment=None):
    active_deployment_collection = models.ActiveDeploymentCollection(
        active_deployment_names=[x for x in [deployment] if x is not None]
    )
    return client.apps.begin_set_active_deployments(resource_group, service, name, active_deployment_collection)


def app_append_loaded_public_certificate(cmd, client, resource_group, service, name, certificate_name, load_trust_store):
    app_resource = client.apps.get(resource_group, service, name)
    certificate_resource = client.certificates.get(resource_group, service, certificate_name)
    certificate_resource_id = certificate_resource.id

    loaded_certificates = []
    if app_resource.properties.loaded_certificates:
        for loaded_certificate in app_resource.properties.loaded_certificates:
            loaded_certificates.append(loaded_certificate)

    for loaded_certificate in loaded_certificates:
        if loaded_certificate.resource_id == certificate_resource.id:
            raise ClientRequestError("This certificate has already been loaded.")

    loaded_certificates.append(models.
                               LoadedCertificate(resource_id=certificate_resource_id,
                                                 load_trust_store=load_trust_store))

    app_resource.properties.loaded_certificates = loaded_certificates
    app_resource.properties.secrets = None
    logger.warning("[1/1] updating app '{}'".format(name))

    poller = client.apps.begin_update(
        resource_group, service, name, app_resource)
    while poller.done() is False:
        sleep(APP_CREATE_OR_UPDATE_SLEEP_INTERVAL)

    app_updated = client.apps.get(resource_group, service, name)
    return app_updated


def _validate_instance_count(sku, instance_count=None):
    if instance_count is not None:
        sku = sku.upper()
        if sku == "ENTERPRISE":
            if instance_count > 1000:
                raise InvalidArgumentValueError(
                    "Enterprise SKU can have at most 1000 app instances in total, but got '{}'".format(instance_count))
        if sku == "STANDARD":
            if instance_count > 500:
                raise CLIError(
                    "Standard SKU can have at most 500 app instances in total, but got '{}'".format(instance_count))
        if sku == "BASIC":
            if instance_count > 25:
                raise CLIError(
                    "Basic SKU can have at most 25 app instances in total, but got '{}'".format(instance_count))


def deployment_list(cmd, client, resource_group, service, app):
    return client.deployments.list(resource_group, service, app)


def deployment_generate_heap_dump(cmd, client, resource_group, service, app, app_instance, file_path, deployment=None):
    diagnostic_parameters = models.DiagnosticParameters(app_instance=app_instance, file_path=file_path)
    logger.info("Heap dump is triggered.")
    return client.deployments.begin_generate_heap_dump(resource_group, service, app, deployment.name, diagnostic_parameters)


def deployment_generate_thread_dump(cmd, client, resource_group, service, app, app_instance, file_path,
                                    deployment=None):
    diagnostic_parameters = models.DiagnosticParameters(app_instance=app_instance, file_path=file_path)
    logger.info("Thread dump is triggered.")
    return client.deployments.begin_generate_thread_dump(resource_group, service, app, deployment.name, diagnostic_parameters)


def deployment_start_jfr(cmd, client, resource_group, service, app, app_instance, file_path, duration=None,
                         deployment=None):
    diagnostic_parameters = models.DiagnosticParameters(app_instance=app_instance, file_path=file_path, duration=duration)
    logger.info("JFR is triggered.")
    return client.deployments.begin_start_jfr(resource_group, service, app, deployment.name, diagnostic_parameters)


def deployment_get(cmd, client, resource_group, service, app, name):
    return client.deployments.get(resource_group, service, app, name)


def deployment_delete(cmd, client, resource_group, service, app, name, no_wait=False):
    deployment = client.deployments.get(resource_group, service, app, name)
    if deployment.properties.active:
        logger.warning(DELETE_PRODUCTION_DEPLOYMENT_WARNING)
    return sdk_no_wait(no_wait, client.deployments.begin_delete, resource_group, service, app, name)


def is_valid_git_uri(uri):
    return uri.startswith("https://") or uri.startswith("git@")


def validate_config_server_settings(client, resource_group, name, config_server_settings):
    error_msg = "Git URI should start with \"https://\" or \"git@\""
    git_property = config_server_settings.git_property
    if git_property:
        if not is_valid_git_uri(git_property.uri):
            raise CLIError(error_msg)
        if git_property.repositories:
            for repository in git_property.repositories:
                if not is_valid_git_uri(repository.uri):
                    raise CLIError(error_msg)

    try:
        result = sdk_no_wait(False, client.begin_validate, resource_group, name, config_server_settings).result()
    except Exception as err:  # pylint: disable=broad-except
        raise CLIError("{0}. You may raise a support ticket if needed by the following link: https://docs.microsoft.com/azure/spring-cloud/spring-cloud-faq?pivots=programming-language-java#how-can-i-provide-feedback-and-report-issues".format(err))

    if not result.is_valid:
        for item in result.details or []:
            if not item.name:
                logger.error("Default repository with URI \"%s\" meets error:", item.uri)
            else:
                logger.error("Repository named \"%s\" with URI \"%s\" meets error:", item.name, item.uri)
            logger.error("\n".join(item.messages))
        raise CLIError("Config Server settings contain error.")


def eureka_get(cmd, client, resource_group, name):
    return client.get(resource_group, name)


def eureka_enable(cmd, client, resource_group, name):
    eureka_server_properties = models.EurekaServerProperties(enabled_state="Enabled")
    eureka_server_resource = models.EurekaServerResource(properties=eureka_server_properties)
    return cached_put(cmd, client.begin_update_patch, eureka_server_resource, resource_group, name).result()


def eureka_disable(cmd, client, resource_group, name):
    eureka_server_properties = models.EurekaServerProperties(enabled_state="Disabled")
    eureka_server_resource = models.EurekaServerResource(properties=eureka_server_properties)
    return cached_put(cmd, client.begin_update_patch, eureka_server_resource, resource_group, name).result()


def config_enable(cmd, client, resource_group, name):
    config_server_resource = client.get(resource_group, name)
    if not config_server_resource.properties.enabled_state:
        raise CLIError("Only supported Standard consumption Tier.")

    config_server_properties = models.ConfigServerProperties(enabled_state="Enabled")
    config_server_resource = models.ConfigServerResource(properties=config_server_properties)
    return cached_put(cmd, client.begin_update_patch, config_server_resource, resource_group, name).result()


def config_disable(cmd, client, resource_group, name):
    config_server_resource = client.get(resource_group, name)
    if not config_server_resource.properties.enabled_state:
        raise CLIError("Only supported Standard consumption Tier.")

    config_server_properties = models.ConfigServerProperties(enabled_state="Disabled")
    config_server_resource = models.ConfigServerResource(properties=config_server_properties)
    return cached_put(cmd, client.begin_update_patch, config_server_resource, resource_group, name).result()


def config_set(cmd, client, resource_group, name, config_file, no_wait=False):
    config_server_resource = client.get(resource_group, name)
    if config_server_resource.properties.enabled_state and config_server_resource.properties.enabled_state == "Disabled":
        raise CLIError("Config server is disabled.")

    def standardization(dic):
        new_dic = {}
        for k, v in dic.items():
            ks = k.split("-")
            ks = [seg[0].upper() + seg[1:] for seg in ks]
            k = ''.join(ks)
            k = k[0].lower() + k[1:]
            new_dic[k] = v

        if 'pattern' in new_dic and isinstance(new_dic['pattern'], str):
            new_dic['pattern'] = new_dic['pattern'].split(',')
        if 'searchPaths' in new_dic and isinstance(new_dic['searchPaths'], str):
            new_dic['searchPaths'] = new_dic['searchPaths'].split(',')
        return new_dic

    with open(config_file, 'r') as stream:
        yaml_object = yaml.safe_load(stream)
    config_property = yaml_object['spring']['cloud']['config']['server']['git']

    if 'default-label' in config_property:
        config_property['label'] = config_property['default-label']
        del config_property['default-label']

    config_property = standardization(config_property)
    repositories = []
    if 'repos' in config_property:
        for k, v in config_property['repos'].items():
            if 'default-label' in v:
                v['label'] = v['default-label']
                del v['default-label']
            v['name'] = k
            v = standardization(v)
            repositories.append(v)
        del config_property['repos']

    config_property['repositories'] = repositories
    git_property = client._deserialize('ConfigServerGitProperty', config_property)
    config_server_settings = models.ConfigServerSettings(git_property=git_property)
    config_server_properties = models.ConfigServerProperties(enabled_state="Enabled", config_server=config_server_settings)

    logger.warning("[1/2] Validating config server settings")
    validate_config_server_settings(client, resource_group, name, config_server_settings)
    logger.warning("[2/2] Updating config server settings, (this operation can take a while to complete)")

    config_server_resource = models.ConfigServerResource(properties=config_server_properties)
    return sdk_no_wait(no_wait, client.begin_update_put, resource_group, name, config_server_resource)


def config_get(cmd, client, resource_group, name):
    config_server_resource = client.get(resource_group, name)

    if not config_server_resource.properties.enabled_state and not config_server_resource.properties.config_server:
        raise CLIError("Config server not set.")
    return config_server_resource


def config_delete(cmd, client, resource_group, name):
    config_server_resource = client.get(resource_group, name)
    config_server_properties = models.ConfigServerProperties(enabled_state=config_server_resource.properties.enabled_state)
    config_server_resource = models.ConfigServerResource(properties=config_server_properties)
    return client.begin_update_put(resource_group, name, config_server_resource)


def config_git_set(cmd, client, resource_group, name, uri,
                   label=None,
                   search_paths=None,
                   username=None,
                   password=None,
                   host_key=None,
                   host_key_algorithm=None,
                   private_key=None,
                   strict_host_key_checking=None):
    config_server_resource = client.get(resource_group, name)
    if config_server_resource.properties.enabled_state and config_server_resource.properties.enabled_state == "Disabled":
        raise CLIError("Config server is disabled.")

    git_property = models.ConfigServerGitProperty(uri=uri)

    if search_paths:
        search_paths = search_paths.split(",")

    git_property.label = label
    git_property.search_paths = search_paths
    git_property.username = username
    git_property.password = password
    git_property.host_key = host_key
    git_property.host_key_algorithm = host_key_algorithm
    git_property.private_key = private_key
    git_property.strict_host_key_checking = strict_host_key_checking

    config_server_settings = models.ConfigServerSettings(git_property=git_property)
    config_server_properties = models.ConfigServerProperties(enabled_state="Enabled", config_server=config_server_settings)

    logger.warning("[1/2] Validating config server settings")
    validate_config_server_settings(client, resource_group, name, config_server_settings)

    logger.warning("[2/2] Updating config server settings, (this operation can take a while to complete)")
    config_server_resource = models.ConfigServerResource(properties=config_server_properties)
    return cached_put(cmd, client.begin_update_put, config_server_resource, resource_group, name).result()


def config_repo_add(cmd, client, resource_group, name, uri, repo_name,
                    pattern=None,
                    label=None,
                    search_paths=None,
                    username=None,
                    password=None,
                    host_key=None,
                    host_key_algorithm=None,
                    private_key=None,
                    strict_host_key_checking=None):
    config_server_resource = client.get(resource_group, name)
    config_server = config_server_resource.properties.config_server
    git_property = models.ConfigServerGitProperty(uri=uri) if not config_server else config_server.git_property

    if search_paths:
        search_paths = search_paths.split(",")

    if pattern:
        pattern = pattern.split(",")

    if git_property.repositories:
        repos = [repo for repo in git_property.repositories if repo.name == repo_name]
        if repos:
            raise CLIError("Repo '{}' already exists.".format(repo_name))
    else:
        git_property.repositories = []

    repository = models.GitPatternRepository(
        uri=uri,
        name=repo_name,
        pattern=pattern,
        label=label,
        search_paths=search_paths,
        username=username,
        password=password,
        host_key=host_key,
        host_key_algorithm=host_key_algorithm,
        private_key=private_key,
        strict_host_key_checking=strict_host_key_checking)

    git_property.repositories.append(repository)
    config_server_settings = models.ConfigServerSettings(git_property=git_property)
    config_server_properties = models.ConfigServerProperties(
        config_server=config_server_settings)

    logger.warning("[1/2] Validating config server settings")
    validate_config_server_settings(client, resource_group, name, config_server_settings)

    logger.warning("[2/2] Adding config server settings repo, (this operation can take a while to complete)")
    config_server_resource = models.ConfigServerResource(properties=config_server_properties)
    return cached_put(cmd, client.begin_update_patch, config_server_resource, resource_group, name).result()


def config_repo_delete(cmd, client, resource_group, name, repo_name):
    config_server_resource = client.get(resource_group, name)
    config_server = config_server_resource.properties.config_server
    if not config_server or not config_server.git_property or not config_server.git_property.repositories:
        raise CLIError("Repo '{}' not found.".format(repo_name))

    git_property = config_server.git_property
    repository = [repo for repo in git_property.repositories if repo.name == repo_name]
    if not repository:
        raise CLIError("Repo '{}' not found.".format(repo_name))

    git_property.repositories.remove(repository[0])

    config_server_settings = models.ConfigServerSettings(git_property=git_property)
    config_server_properties = models.ConfigServerProperties(
        config_server=config_server_settings)

    logger.warning("[1/2] Validating config server settings")
    validate_config_server_settings(client, resource_group, name, config_server_settings)

    logger.warning("[2/2] Deleting config server settings repo, (this operation can take a while to complete)")
    config_server_resource = models.ConfigServerResource(properties=config_server_properties)
    return cached_put(cmd, client.begin_update_patch, config_server_resource, resource_group, name).result()


def config_repo_update(cmd, client, resource_group, name, repo_name,
                       uri=None,
                       pattern=None,
                       label=None,
                       search_paths=None,
                       username=None,
                       password=None,
                       host_key=None,
                       host_key_algorithm=None,
                       private_key=None,
                       strict_host_key_checking=None):
    config_server_resource = client.get(resource_group, name)
    config_server = config_server_resource.properties.config_server
    if not config_server or not config_server.git_property or not config_server.git_property.repositories:
        raise CLIError("Repo '{}' not found.".format(repo_name))
    git_property = config_server.git_property
    repository = [repo for repo in git_property.repositories if repo.name == repo_name]
    if not repository:
        raise CLIError("Repo '{}' not found.".format(repo_name))

    if search_paths:
        search_paths = search_paths.split(",")

    if pattern:
        pattern = pattern.split(",")

    old_repository = repository[0]
    git_property.repositories.remove(old_repository)

    repository = models.GitPatternRepository(name=old_repository.name, uri=uri or old_repository.uri)
    repository.pattern = pattern or old_repository.pattern
    repository.label = label or old_repository.label
    repository.search_paths = search_paths or old_repository.search_paths
    repository.username = username or old_repository.username
    repository.password = password or old_repository.password
    repository.host_key = host_key or old_repository.host_key
    repository.host_key_algorithm = host_key_algorithm or old_repository.host_key_algorithm
    repository.private_key = private_key or old_repository.private_key
    repository.strict_host_key_checking = strict_host_key_checking or old_repository.strict_host_key_checking

    git_property.repositories.append(repository)

    config_server_settings = models.ConfigServerSettings(git_property=git_property)
    config_server_properties = models.ConfigServerProperties(config_server=config_server_settings)

    logger.warning("[1/2] Validating config server settings")
    validate_config_server_settings(client, resource_group, name, config_server_settings)

    logger.warning("[2/2] Updating config server settings repo, (this operation can take a while to complete)")
    config_server_resource = models.ConfigServerResource(properties=config_server_properties)
    return cached_put(cmd, client.begin_update_patch, config_server_resource, resource_group, name).result()


def config_repo_list(cmd, client, resource_group, name):
    config_server_resource = client.get(resource_group, name)
    config_server = config_server_resource.properties.config_server

    if not config_server or not config_server.git_property or not config_server.git_property.repositories:
        raise CLIError("Repos not found.")

    return config_server.git_property.repositories


def binding_list(cmd, client, resource_group, service, app):
    return client.bindings.list(resource_group, service, app)


def binding_get(cmd, client, resource_group, service, app, name):
    return client.bindings.get(resource_group, service, app, name)


def binding_remove(cmd, client, resource_group, service, app, name):
    return client.bindings.begin_delete(resource_group, service, app, name)


def binding_cosmos_add(cmd, client, resource_group, service, app, name,
                       resource_id,
                       api_type,
                       database_name=None,
                       key_space=None,
                       collection_name=None):
    resource_id_dict = parse_resource_id(resource_id)
    resource_type = resource_id_dict['resource_type']
    resource_name = resource_id_dict['resource_name']
    binding_parameters = {}
    binding_parameters['apiType'] = api_type
    if database_name:
        binding_parameters['databaseName'] = database_name
    if key_space:
        binding_parameters['keySpace'] = key_space
    if collection_name:
        binding_parameters['collectionName'] = collection_name

    try:
        primary_key = _get_cosmosdb_primary_key(cmd.cli_ctx, resource_id)
    except:
        raise CLIError(
            "Couldn't get cosmosdb {}'s primary key".format(resource_name))

    properties = models.BindingResourceProperties(
        resource_name=resource_name,
        resource_type=resource_type,
        resource_id=resource_id,
        key=primary_key,
        binding_parameters=binding_parameters
    )
    binding_resource = models.BindingResource(properties=properties)
    return client.bindings.begin_create_or_update(resource_group, service, app, name, binding_resource)


def binding_cosmos_update(cmd, client, resource_group, service, app, name,
                          database_name=None,
                          key_space=None,
                          collection_name=None):
    binding = client.bindings.get(resource_group, service, app, name).properties
    resource_id = binding.resource_id
    resource_name = binding.resource_name
    binding_parameters = {}
    binding_parameters['databaseName'] = database_name
    binding_parameters['keySpace'] = key_space
    binding_parameters['collectionName'] = collection_name

    try:
        primary_key = _get_cosmosdb_primary_key(cmd.cli_ctx, resource_id)
    except:
        raise CLIError(
            "Couldn't get cosmosdb {}'s primary key".format(resource_name))

    properties = models.BindingResourceProperties(
        key=primary_key,
        binding_parameters=binding_parameters
    )
    binding_resource = models.BindingResource(properties=properties)
    return client.bindings.begin_update(resource_group, service, app, name, binding_resource)


def binding_mysql_add(cmd, client, resource_group, service, app, name,
                      resource_id,
                      key,
                      username,
                      database_name):
    resource_id_dict = parse_resource_id(resource_id)
    resource_type = resource_id_dict['resource_type']
    resource_name = resource_id_dict['resource_name']
    binding_parameters = {}
    binding_parameters['username'] = username
    binding_parameters['databaseName'] = database_name

    properties = models.BindingResourceProperties(
        resource_name=resource_name,
        resource_type=resource_type,
        resource_id=resource_id,
        key=key,
        binding_parameters=binding_parameters
    )
    binding_resource = models.BindingResource(properties=properties)
    return client.bindings.begin_create_or_update(resource_group, service, app, name, binding_resource)


def binding_mysql_update(cmd, client, resource_group, service, app, name,
                         key=None,
                         username=None,
                         database_name=None):
    binding_parameters = {}
    binding_parameters['username'] = username
    binding_parameters['databaseName'] = database_name

    properties = models.BindingResourceProperties(
        key=key,
        binding_parameters=binding_parameters
    )
    binding_resource = models.BindingResource(properties=properties)
    return client.bindings.begin_update(resource_group, service, app, name, binding_resource)


def binding_redis_add(cmd, client, resource_group, service, app, name,
                      resource_id,
                      disable_ssl=None):
    use_ssl = not disable_ssl
    resource_id_dict = parse_resource_id(resource_id)
    resource_type = resource_id_dict['resource_type']
    resource_name = resource_id_dict['resource_name']
    binding_parameters = {}
    binding_parameters['useSsl'] = use_ssl
    primary_key = None
    try:
        primary_key = _get_redis_primary_key(cmd.cli_ctx, resource_id)
    except:
        raise CLIError(
            "Couldn't get redis {}'s primary key".format(resource_name))

    properties = models.BindingResourceProperties(
        resource_name=resource_name,
        resource_type=resource_type,
        resource_id=resource_id,
        key=primary_key,
        binding_parameters=binding_parameters
    )
    binding_resource = models.BindingResource(properties=properties)
    return client.bindings.begin_create_or_update(resource_group, service, app, name, binding_resource)


def binding_redis_update(cmd, client, resource_group, service, app, name,
                         disable_ssl=None):
    binding = client.bindings.get(resource_group, service, app, name).properties
    resource_id = binding.resource_id
    resource_name = binding.resource_name
    binding_parameters = {}
    binding_parameters['useSsl'] = not disable_ssl

    primary_key = None
    try:
        primary_key = _get_redis_primary_key(cmd.cli_ctx, resource_id)
    except:
        raise CLIError(
            "Couldn't get redis {}'s primary key".format(resource_name))

    properties = models.BindingResourceProperties(
        key=primary_key,
        binding_parameters=binding_parameters
    )
    binding_resource = models.BindingResource(properties=properties)
    return client.bindings.begin_update(resource_group, service, app, name, binding_resource)


def _get_cosmosdb_primary_key(cli_ctx, resource_id):
    resource_id_dict = parse_resource_id(resource_id)
    cosmosdb_client = get_mgmt_service_client(cli_ctx, CosmosDBManagementClient)
    keys = cosmosdb_client.database_accounts.list_keys(resource_id_dict['resource_group'],
                                                       resource_id_dict['resource_name'])
    return keys.primary_master_key


def _get_redis_primary_key(cli_ctx, resource_id):
    resource_id_dict = parse_resource_id(resource_id)
    redis_client = get_mgmt_service_client(cli_ctx, RedisManagementClient)
    keys = redis_client.redis.list_keys(resource_id_dict['resource_group'], resource_id_dict['resource_name'])
    return keys.primary_key


def storage_callback(pipeline_response, deserialized, headers):
    return models.StorageResource.deserialize(json.loads(pipeline_response.http_response.text()))


def storage_add(client, resource_group, service, name, storage_type, account_name, account_key):
    properties = None
    if storage_type == 'StorageAccount':
        properties = models.StorageAccount(
            storage_type=storage_type,
            account_name=account_name,
            account_key=account_key)

    return client.storages.begin_create_or_update(
        resource_group_name=resource_group,
        service_name=service,
        storage_name=name,
        storage_resource=models.StorageResource(properties=properties),
        cls=storage_callback)


def storage_get(client, resource_group, service, name):
    return client.storages.get(resource_group, service, name)


def storage_list(client, resource_group, service):
    return client.storages.list(resource_group, service)


def storage_remove(client, resource_group, service, name):
    client.storages.get(resource_group, service, name)
    return client.storages.begin_delete(resource_group, service, name)


def storage_update(client, resource_group, service, name, storage_type, account_name, account_key):
    properties = None
    if storage_type == 'StorageAccount':
        properties = models.StorageAccount(
            storage_type=storage_type,
            account_name=account_name,
            account_key=account_key)

    return client.storages.begin_create_or_update(
        resource_group_name=resource_group,
        service_name=service,
        storage_name=name,
        storage_resource=models.StorageResource(properties=properties),
        cls=storage_callback)


def storage_list_persistent_storage(client, resource_group, service, name):
    apps = list(client.apps.list(resource_group, service))

    storage_resource = client.storages.get(resource_group, service, name)
    storage_id = storage_resource.id
    reference_apps = []

    for app in apps:
        for custom_persistent_disk in app.properties.custom_persistent_disks or []:
            if custom_persistent_disk.storage_id == storage_id:
                reference_apps.append(app)
                break
    return reference_apps


def certificate_add(cmd, client, resource_group, service, name, only_public_cert=None,
                    vault_uri=None, vault_certificate_name=None, public_certificate_file=None, enable_auto_sync=None):
    if vault_uri is None and public_certificate_file is None:
        raise InvalidArgumentValueError("One of --vault-uri and --public-certificate-file should be provided")
    if vault_uri is not None and public_certificate_file is not None:
        raise InvalidArgumentValueError("--vault-uri and --public-certificate-file could not be provided at the same time")
    if vault_uri is not None:
        if vault_certificate_name is None:
            raise InvalidArgumentValueError("--vault-certificate-name should be provided for Key Vault Certificate")

    if vault_uri is not None:
        if only_public_cert is None:
            only_public_cert = False
        properties = models.KeyVaultCertificateProperties(
            type='KeyVaultCertificate',
            vault_uri=vault_uri,
            key_vault_cert_name=vault_certificate_name,
            exclude_private_key=only_public_cert,
            auto_sync='Enabled' if enable_auto_sync is True else 'Disabled'
        )
    else:
        if os.path.exists(public_certificate_file):
            try:
                with open(public_certificate_file, 'rb') as input_file:
                    logger.debug("attempting to read file %s as binary", public_certificate_file)
                    content = base64.b64encode(input_file.read()).decode("utf-8")
            except Exception:
                raise FileOperationError('Failed to decode file {} - unknown decoding'.format(public_certificate_file))
        else:
            raise FileOperationError("public_certificate_file {} could not be found".format(public_certificate_file))
        properties = models.ContentCertificateProperties(
            type="ContentCertificate",
            content=content
        )
    certificate_resource = models.CertificateResource(properties=properties)

    return client.certificates.begin_create_or_update(resource_group, service, name, certificate_resource)


def certificate_update(cmd, client, resource_group, service, name, enable_auto_sync=None):
    certificate_resource = client.certificates.get(resource_group, service, name)

    if certificate_resource.properties.type == 'KeyVaultCertificate':
        if enable_auto_sync is not None:
            certificate_resource.properties.auto_sync = 'Enabled' if enable_auto_sync is True else 'Disabled'

    return client.certificates.begin_create_or_update(resource_group, service, name, certificate_resource)


def certificate_show(cmd, client, resource_group, service, name):
    return client.certificates.get(resource_group, service, name)


def certificate_list(cmd, client, resource_group, service, certificate_type=None):
    certificates = list(client.certificates.list(resource_group, service))
    certificates_to_list = []
    if certificate_type is None:
        certificates_to_list = certificates
    elif certificate_type == 'KeyVaultCertificate':
        for certificate in certificates:
            if certificate.properties.type == 'KeyVaultCertificate':
                certificates_to_list.append(certificate)
    elif certificate_type == 'ContentCertificate':
        for certificate in certificates:
            if certificate.properties.type == 'ContentCertificate':
                certificates_to_list.append(certificate)
    return certificates_to_list


def certificate_remove(cmd, client, resource_group, service, name):
    client.certificates.get(resource_group, service, name)
    return client.certificates.begin_delete(resource_group, service, name)


def certificate_list_reference_app(cmd, client, resource_group, service, name):
    apps = list(client.apps.list(resource_group, service))
    reference_apps = []
    certificate_resource = client.certificates.get(resource_group, service, name)
    certificate_resource_id = certificate_resource.id
    for app in apps:
        for load_certificate in app.properties.loaded_certificates or []:
            if load_certificate.resource_id == certificate_resource_id:
                reference_apps.append(app)
                break
    return reference_apps


def domain_bind(cmd, client, resource_group, service, app,
                domain_name,
                certificate=None,
                enable_ingress_to_app_tls=None):
    properties = models.CustomDomainProperties()

    resource = client.services.get(resource_group, service)
    if resource.sku.tier.upper() == 'STANDARDGEN2':
        properties = models.CustomDomainProperties(cert_name=certificate)
    else:
        if certificate is not None:
            certificate_response = client.certificates.get(resource_group, service, certificate)
            properties = models.CustomDomainProperties(
                thumbprint=certificate_response.properties.thumbprint,
                cert_name=certificate
            )
        if enable_ingress_to_app_tls is not None:
            _update_app_e2e_tls(cmd, client, resource_group, service, app, enable_ingress_to_app_tls)

    custom_domain_resource = models.CustomDomainResource(properties=properties)
    return client.custom_domains.begin_create_or_update(resource_group, service, app,
                                                        domain_name, custom_domain_resource)


def _update_app_e2e_tls(cmd, client, resource_group, service, app, enable_ingress_to_app_tls):
    resource = client.services.get(resource_group, service)
    location = resource.location

    properties = models.AppResourceProperties(enable_end_to_end_tls=enable_ingress_to_app_tls)
    app_resource = models.AppResource()
    app_resource.properties = properties
    app_resource.location = location

    logger.warning("Set ingress to app tls for app '{}'".format(app))
    poller = client.apps.begin_update(
        resource_group, service, app, app_resource)
    return poller.result()


def domain_show(cmd, client, resource_group, service, app, domain_name):
    return client.custom_domains.get(resource_group, service, app, domain_name)


def domain_list(cmd, client, resource_group, service, app):
    return client.custom_domains.list(resource_group, service, app)


def domain_update(cmd, client, resource_group, service, app,
                  domain_name,
                  certificate=None,
                  enable_ingress_to_app_tls=None):
    properties = models.CustomDomainProperties()
    if certificate is not None:
        certificate_response = client.certificates.get(resource_group, service, certificate)
        properties = models.CustomDomainProperties(
            thumbprint=certificate_response.properties.thumbprint,
            cert_name=certificate
        )
    if enable_ingress_to_app_tls is not None:
        _update_app_e2e_tls(cmd, client, resource_group, service, app, enable_ingress_to_app_tls)

    custom_domain_resource = models.CustomDomainResource(properties=properties)
    return client.custom_domains.begin_create_or_update(resource_group, service, app,
                                                        domain_name, custom_domain_resource)


def domain_unbind(cmd, client, resource_group, service, app, domain_name):
    client.custom_domains.get(resource_group, service, app, domain_name)
    return client.custom_domains.begin_delete(resource_group, service, app, domain_name)


def get_app_insights_connection_string(cli_ctx, resource_group, name):
    appinsights_client = get_mgmt_service_client(cli_ctx, ApplicationInsightsManagementClient)
    appinsights = appinsights_client.components.get(resource_group, name)
    if appinsights is None or appinsights.connection_string is None:
        raise ResourceNotFoundError("App Insights {} under resource group {} was not found."
                                    .format(name, resource_group))
    return appinsights.connection_string


def update_java_agent_config(cmd, resource_group, service_name, location,
                             app_insights_key, app_insights, sampling_rate):
    """
    :param sampling_rate: None safe, backend will use default value.
    """
    create_app_insights = False
    monitoring_setting_properties = None

    if app_insights_key or app_insights:
        monitoring_setting_properties = _get_monitoring_setting(cmd, resource_group, app_insights_key, app_insights)
    else:
        create_app_insights = True

    if create_app_insights is True:
        try:
            created_app_insights = try_create_application_insights(cmd, resource_group, service_name, location)
            if created_app_insights:
                monitoring_setting_properties = models.MonitoringSettingProperties(
                    trace_enabled=True, app_insights_instrumentation_key=created_app_insights.connection_string)
        except Exception:  # pylint: disable=broad-except
            logger.warning(
                'Error while trying to create and configure an Application Insights for the Azure Spring Apps. '
                'Please use the Azure Portal to create and configure the Application Insights, if needed.')
            return None
    if monitoring_setting_properties:
        monitoring_setting_properties.app_insights_sampling_rate = sampling_rate
    return monitoring_setting_properties


def _get_monitoring_setting(cmd, resource_group, app_insights_key, app_insights):
    monitoring_setting_properties = None
    if app_insights_key:
        monitoring_setting_properties = models.MonitoringSettingProperties(
            trace_enabled=True,
            app_insights_instrumentation_key=app_insights_key)
    elif app_insights:
        connection_string = _get_connection_string_from_app_insights(cmd, resource_group, app_insights)
        monitoring_setting_properties = models.MonitoringSettingProperties(
            trace_enabled=True,
            app_insights_instrumentation_key=connection_string)
    return monitoring_setting_properties


def _get_connection_string_from_app_insights(cmd, resource_group, app_insights):
    """Get connection string from:
    1) application insights name
    2) application insights resource id
    """
    if is_valid_resource_id(app_insights):
        resource_id_dict = parse_resource_id(app_insights)
        connection_string = get_app_insights_connection_string(
            cmd.cli_ctx, resource_id_dict['resource_group'], resource_id_dict['resource_name'])
    else:
        connection_string = get_app_insights_connection_string(cmd.cli_ctx, resource_group, app_insights)
    if not connection_string:
        raise InvalidArgumentValueError(
            "Cannot find Connection string from application insights:{}".format(app_insights))
    return connection_string


def try_create_application_insights(cmd, resource_group, name, location):
    workspace = try_create_log_analytics_workspace(cmd, resource_group, name, location)
    if workspace is None:
        logger.warning(APP_INSIGHTS_CREATION_FAILURE_WARNING)
        return None

    app_insights_client = get_mgmt_service_client(cmd.cli_ctx, ApplicationInsightsManagementClient,
                                                  api_version='2020-02-02-preview')
    ai_properties = {
        "location": location,
        "kind": "web",
        "properties": {
            "Application_Type": "web",
            "Flow_Type": "Bluefield",
            "Request_Source": "rest",
            "WorkspaceResourceId": workspace.id
        }
    }
    appinsights = app_insights_client.components.create_or_update(resource_group, name, ai_properties)
    if appinsights is None or appinsights.connection_string is None:
        logger.warning(APP_INSIGHTS_CREATION_FAILURE_WARNING)
        return None

    portal_url = get_portal_uri(cmd.cli_ctx)
    # We make this success message as a warning to no interfere with regular JSON output in stdout
    logger.warning('Application Insights \"%s\" was created for this Azure Spring Apps. '
                   'You can visit %s/#resource%s/overview to view your '
                   'Application Insights component', appinsights.name, portal_url, appinsights.id)

    return appinsights


def app_insights_update(cmd, client, resource_group, name,
                        app_insights_key=None, app_insights=None, sampling_rate=None,
                        disable=None, no_wait=False):
    """
    :param app_insights_key: Connection string or Instrumentation key
    :param sampling_rate: float from 0.0 to 100.0, both included
    """
    if disable:
        monitoring_setting_properties = models.MonitoringSettingProperties(trace_enabled=False)
    else:
        monitoring_setting_properties = client.monitoring_settings.get(resource_group, name).properties
        if not monitoring_setting_properties.app_insights_instrumentation_key \
                and not app_insights_key \
                and not app_insights:
            InvalidArgumentValueError("Can't update application insights without connecting to Application Insights. "
                                      "Please provide '--app-insights' or '--app-insights-key'.")
        if app_insights_key:
            connection_string = app_insights_key
        elif app_insights:
            if is_valid_resource_id(app_insights):
                resource_id_dict = parse_resource_id(app_insights)
                connection_string = get_app_insights_connection_string(
                    cmd.cli_ctx, resource_id_dict['resource_group'], resource_id_dict['resource_name'])
            else:
                connection_string = get_app_insights_connection_string(cmd.cli_ctx, resource_group, app_insights)
        else:
            connection_string = monitoring_setting_properties.app_insights_instrumentation_key
        if sampling_rate is not None:
            monitoring_setting_properties = models.MonitoringSettingProperties(
                trace_enabled=True,
                app_insights_instrumentation_key=connection_string,
                app_insights_sampling_rate=sampling_rate)
        elif monitoring_setting_properties.app_insights_sampling_rate is not None:
            monitoring_setting_properties = models.MonitoringSettingProperties(
                trace_enabled=True,
                app_insights_instrumentation_key=connection_string,
                app_insights_sampling_rate=monitoring_setting_properties.app_insights_sampling_rate)
    if monitoring_setting_properties is not None:
        monitoring_setting_resource = models.MonitoringSettingResource(properties=monitoring_setting_properties)
        sdk_no_wait(no_wait, client.monitoring_settings.begin_update_put,
                    resource_group_name=resource_group, service_name=name,
                    monitoring_setting_resource=monitoring_setting_resource)


def app_insights_show(cmd, client, resource_group, name, no_wait=False):
    monitoring_setting_properties = client.monitoring_settings.get(resource_group, name).properties
    if not monitoring_setting_properties:
        raise CLIError("Application Insights not set.")
    return monitoring_setting_properties


def try_create_log_analytics_workspace(cmd, resource_group, name, location):
    client = get_mgmt_service_client(cmd.cli_ctx, LogAnalyticsManagementClient)
    workspace = None

    try:
        workspace = client.workspaces.get(resource_group, name)
    except HttpResponseError as err:
        if err.status_code != 404:
            raise

    if workspace is not None:
        return workspace

    logger.debug("Log Analytics workspace not found. Creating it now...")
    properties = {
        "location": location,
        "properties": {
            "sku": {
                "name": "PerGB2018"
            },
            "retentionInDays": 30
        }
    }
    workspace = client.workspaces.begin_create_or_update(resource_group, name, properties).result()

    portal_url = get_portal_uri(cmd.cli_ctx)
    # We make this success message as a warning to no interfere with regular JSON output in stdout
    logger.warning('Log Analytics workspace \"%s\" was created for this Azure Spring Apps. '
                   'You can visit %s/#resource%s/overview to view your Log Analytics workspace',
                   workspace.name, portal_url, workspace.id)

    return workspace


def app_connect(cmd, client, resource_group, service, name,
                deployment=None, instance=None, shell_cmd='/bin/sh'):

    profile = Profile(cli_ctx=cmd.cli_ctx)
    creds, _, tenant = profile.get_raw_token()
    token = creds[1]

    resource = client.services.get(resource_group, service)
    if not instance:
        if not deployment.properties.instances:
            raise ResourceNotFoundError("No instances found for deployment '{0}' in app '{1}'".format(
                deployment.name, name))
        instances = deployment.properties.instances
        if len(instances) > 1:
            logger.warning("Multiple app instances found:")
            for temp_instance in instances:
                logger.warning("{}".format(temp_instance.name))
            logger.warning("Please use '-i/--instance' parameter to specify the instance name")
            return None
        instance = instances[0].name

    if resource.sku.tier.upper() == 'STANDARDGEN2':
        subscriptionId = get_subscription_id(cmd.cli_ctx)
        hostname = get_proxy_api_endpoint(cmd.cli_ctx, resource)
        connect_url = "wss://{}/proxy/appconnect/subscriptions/{}/resourceGroups/{}/providers/Microsoft.AppPlatform/Spring/{}/apps/{}/deployments/{}/instances/{}?tenantId={}&command={}".format(
            hostname, subscriptionId, resource_group, resource.name, name, deployment.name, instance, tenant, shell_cmd)
        logger.warning("Connecting to %s...", connect_url)
    else:
        hostname = resource.properties.fqdn
        connect_url = "wss://{0}/api/appconnect/apps/{1}/deployments/{2}/instances/{3}/connect?command={4}".format(hostname, name, deployment.name, instance, shell_cmd)
        logger.warning("Connecting to the app instance Microsoft.AppPlatform/Spring/%s/apps/%s/deployments/%s/instances/%s..." % (service, name, deployment.name, instance))

    conn = WebSocketConnection(connect_url, token)

    reader = Thread(target=recv_remote, args=(conn,))
    reader.daemon = True
    reader.start()

    try:
        import tty
        tty.setcbreak(sys.stdin.fileno())  # needed to prevent printing arrow key characters
    except ModuleNotFoundError:
        # tty works only on Unix
        pass

    writer = Thread(target=send_stdin, args=(conn,))
    writer.daemon = True
    writer.start()

    logger.warning("Use ctrl + D to exit.")
    while conn.is_connected:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            if conn.is_connected:
                logger.info("Caught KeyboardInterrupt. Sending ctrl+c to server")
                conn.send(EXEC_PROTOCOL_CTRL_C_MSG)

    try:
        import termios
        # Turn on the terminal echo after exiting.
        mode = termios.tcgetattr(sys.stdin.fileno())
        mode[3] = mode[3] | termios.ECHO
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSAFLUSH, mode)
    except ModuleNotFoundError:
        # termios works only on Unix
        pass
