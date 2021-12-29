# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument, logging-format-interpolation, protected-access, wrong-import-order, too-many-lines
import requests
import re
import os
import shlex

from azure.core.exceptions import HttpResponseError
from azure.mgmt.cosmosdb import CosmosDBManagementClient
from azure.mgmt.redis import RedisManagementClient
from requests.auth import HTTPBasicAuth
import yaml  # pylint: disable=import-error
from time import sleep
from ._stream_utils import stream_logs
from azure.mgmt.core.tools import (parse_resource_id, is_valid_resource_id)
from ._utils import (_get_upload_local_file, _get_persistent_disk_size,
                     get_portal_uri, get_azure_files_info,
                     wait_till_end)
from knack.util import CLIError
from .vendored_sdks.appplatform.v2020_07_01 import models
from .vendored_sdks.appplatform.v2020_11_01_preview import models as models_20201101preview
from .vendored_sdks.appplatform.v2022_01_01_preview import models as models_20220101preview
from .vendored_sdks.appplatform.v2020_07_01.models import _app_platform_management_client_enums as AppPlatformEnums
from .vendored_sdks.appplatform.v2020_11_01_preview import (
    AppPlatformManagementClient as AppPlatformManagementClient_20201101preview
)
from knack.log import get_logger
from .azure_storage_file import FileService
from azure.cli.core.azclierror import ClientRequestError, FileOperationError, InvalidArgumentValueError, RequiredArgumentMissingError
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.util import get_file_json, sdk_no_wait
from azure.cli.core.profiles import ResourceType, get_sdk
from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient
from azure.cli.core.commands import cached_put
from azure.core.exceptions import ResourceNotFoundError
from ._utils import _get_rg_location
from ._resource_quantity import validate_cpu, validate_memory
from six.moves.urllib import parse
from threading import Thread
from threading import Timer
import sys
import json
import base64
from collections import defaultdict
from ._log_stream import LogStream

logger = get_logger(__name__)
DEFAULT_DEPLOYMENT_NAME = "default"
DEPLOYMENT_CREATE_OR_UPDATE_SLEEP_INTERVAL = 5
APP_CREATE_OR_UPDATE_SLEEP_INTERVAL = 2

# pylint: disable=line-too-long
NO_PRODUCTION_DEPLOYMENT_ERROR = "No production deployment found, use --deployment to specify deployment or create deployment with: az spring-cloud app deployment create"
NO_PRODUCTION_DEPLOYMENT_SET_ERROR = "This app has no production deployment, use \"az spring-cloud app deployment create\" to create a deployment and \"az spring-cloud app set-deployment\" to set production deployment."
DELETE_PRODUCTION_DEPLOYMENT_WARNING = "You are going to delete production deployment, the app will be inaccessible after this operation."
LOG_RUNNING_PROMPT = "This command usually takes minutes to run. Add '--verbose' parameter if needed."


def spring_cloud_create(cmd, client, resource_group, name, location=None,
                        vnet=None, service_runtime_subnet=None, app_subnet=None, reserved_cidr_range=None,
                        service_runtime_network_resource_group=None, app_network_resource_group=None,
                        app_insights_key=None, app_insights=None, sampling_rate=None,
                        disable_app_insights=None, enable_java_agent=None,
                        sku=None, tags=None, zone_redundant=False, no_wait=False):
    """
    Note: This is the command for create Spring-Cloud Standard and Basic tier. Refer tier_routing_spring_cloud.py for
    the command definition. And _enteprise.py for Spring-Cloud Enterprise tier creation.

    If app_insights_key, app_insights and disable_app_insights are all None,
    will still create an application insights and enable application insights.
    :param enable_java_agent: (TODO) In deprecation process, ignore the value now. Will delete this.
    :param app_insights: application insights name or its resource id
    :param app_insights_key: Connection string or Instrumentation key
    """
    # TODO (jiec) Deco this method when we deco parameter "--enable-java-agent"
    _warn_enable_java_agent(enable_java_agent)

    poller = _create_service(cmd, client, resource_group, name,
                             location=location,
                             service_runtime_subnet=service_runtime_subnet,
                             app_subnet=app_subnet,
                             reserved_cidr_range=reserved_cidr_range,
                             service_runtime_network_resource_group=service_runtime_network_resource_group,
                             app_network_resource_group=app_network_resource_group,
                             zone_redundant=zone_redundant,
                             sku=sku,
                             tags=tags)
    _update_application_insights_asc_create(cmd, resource_group, name, location,
                                            app_insights_key, app_insights, sampling_rate,
                                            disable_app_insights, no_wait)
    return poller


def _create_service(cmd, client, resource_group, name, location=None,
                    service_runtime_subnet=None, app_subnet=None, reserved_cidr_range=None,
                    service_runtime_network_resource_group=None, app_network_resource_group=None,
                    zone_redundant=False,
                    sku=None, tags=None):
    if location is None:
        location = _get_rg_location(cmd.cli_ctx, resource_group)
    properties = models_20220101preview.ClusterResourceProperties()

    if service_runtime_subnet or app_subnet or reserved_cidr_range:
        properties.network_profile = models_20220101preview.NetworkProfile(
            service_runtime_subnet_id=service_runtime_subnet,
            app_subnet_id=app_subnet,
            service_cidr=reserved_cidr_range,
            app_network_resource_group=app_network_resource_group,
            service_runtime_network_resource_group=service_runtime_network_resource_group
        )

    properties.zone_redundant = zone_redundant
    resource = models_20220101preview.ServiceResource(location=location, sku=sku, properties=properties, tags=tags)

    poller = client.services.begin_create_or_update(
        resource_group, name, resource)
    logger.warning(" - Creating Service ..")
    wait_till_end(cmd, poller)
    return poller


def _warn_enable_java_agent(enable_java_agent):
    if enable_java_agent is not None:
        logger.warn("Java in process agent is now GA-ed and used by default when Application Insights enabled. "
                    "The parameter '--enable-java-agent' is no longer needed and will be removed in future release.")


def _update_application_insights_asc_create(cmd, resource_group, name, location,
                                            app_insights_key, app_insights, sampling_rate,
                                            disable_app_insights, no_wait):
    monitoring_setting_resource = models.MonitoringSettingResource()
    if disable_app_insights is not True:
        client_preview = get_mgmt_service_client(cmd.cli_ctx, AppPlatformManagementClient_20201101preview)
        logger.warning("Start configure Application Insights")
        monitoring_setting_properties = update_java_agent_config(
            cmd, resource_group, name, location, app_insights_key, app_insights, sampling_rate)
        if monitoring_setting_properties is not None:
            monitoring_setting_resource.properties = monitoring_setting_properties
            sdk_no_wait(no_wait, client_preview.monitoring_settings.begin_update_put,
                        resource_group_name=resource_group, service_name=name,
                        monitoring_setting_resource=monitoring_setting_resource)


def spring_cloud_update(cmd, client, resource_group, name, app_insights_key=None, app_insights=None,
                        disable_app_insights=None, sku=None, tags=None, no_wait=False):
    """
    TODO (jiec) app_insights_key, app_insights and disable_app_insights are marked as deprecated.
    Will be decommissioned in future releases.
    :param app_insights_key: Connection string or Instrumentation key
    """
    updated_resource = models_20220101preview.ServiceResource()
    update_service_tags = False
    update_service_sku = False

    # update service sku
    if sku is not None:
        updated_resource.sku = sku
        update_service_sku = True

    resource = client.services.get(resource_group, name)
    location = resource.location
    updated_resource_properties = models_20220101preview.ClusterResourceProperties()

    _update_application_insights_asc_update(cmd, resource_group, name, location,
                                            app_insights_key, app_insights, disable_app_insights, no_wait)

    # update service tags
    if tags is not None:
        updated_resource.tags = tags
        update_service_tags = True

    if update_service_tags is False and update_service_sku is False:
        return resource

    updated_resource.properties = updated_resource_properties
    return sdk_no_wait(no_wait, client.services.begin_update,
                       resource_group_name=resource_group, service_name=name, resource=updated_resource)


def _update_application_insights_asc_update(cmd, resource_group, name, location,
                                            app_insights_key, app_insights, disable_app_insights, no_wait):
    """If app_insights_key, app_insights and disable_app_insights are all None, do nothing here
    """
    update_app_insights = False
    app_insights_target_status = False

    client_preview = get_mgmt_service_client(cmd.cli_ctx, AppPlatformManagementClient_20201101preview)
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
            monitoring_setting_properties = models_20201101preview.MonitoringSettingProperties(trace_enabled=False)
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


def spring_cloud_delete(cmd, client, resource_group, name, no_wait=False):
    logger.warning("Stop using Azure Spring Cloud? We appreciate your feedback: https://aka.ms/springclouddeletesurvey")
    return sdk_no_wait(no_wait, client.services.begin_delete, resource_group_name=resource_group, service_name=name)


def spring_cloud_start(cmd, client, resource_group, name, no_wait=False):
    resource = client.services.get(resource_group, name)
    state = resource.properties.provisioning_state
    power_state = resource.properties.power_state
    if state != "Succeeded" or power_state != "Stopped":
        raise ClientRequestError("Service is in Provisioning State({}) and Power State({}), starting cannot be performed.".format(state, power_state))
    return sdk_no_wait(no_wait, client.services.begin_start, resource_group_name=resource_group, service_name=name)


def spring_cloud_stop(cmd, client, resource_group, name, no_wait=False):
    resource = client.services.get(resource_group, name)
    state = resource.properties.provisioning_state
    power_state = resource.properties.power_state
    if state != "Succeeded" or power_state != "Running":
        raise ClientRequestError("Service is in Provisioning State({}) and Power State({}), stopping cannot be performed.".format(state, power_state))
    return sdk_no_wait(no_wait, client.services.begin_stop, resource_group_name=resource_group, service_name=name)


def spring_cloud_list(cmd, client, resource_group=None):
    if resource_group is None:
        return client.services.list_by_subscription()
    return client.services.list(resource_group)


def spring_cloud_get(cmd, client, resource_group, name):
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
                                  share_name,
                                  mount_path,
                                  mount_options=None,
                                  read_only=None):
    storage_resource = client.storages.get(resource_group, service, storage_name)
    app = client.apps.get(resource_group, service, name)

    custom_persistent_disks = []
    if app.properties.custom_persistent_disks:
        for disk in app.properties.custom_persistent_disks:
            custom_persistent_disks.append(disk)

    custom_persistent_disk_properties = models_20220101preview.AzureFileVolume(
        type=persistent_storage_type,
        share_name=share_name,
        mount_path=mount_path,
        mount_options=mount_options,
        read_only=read_only)

    custom_persistent_disks.append(
        models_20220101preview.CustomPersistentDiskResource(
            storage_id=storage_resource.id,
            custom_persistent_disk_properties=custom_persistent_disk_properties))

    app.properties.custom_persistent_disks = custom_persistent_disks
    logger.warning("[1/1] updating app '{}'".format(name))

    poller = client.apps.begin_update(
        resource_group, service, name, app)
    while poller.done() is False:
        sleep(APP_CREATE_OR_UPDATE_SLEEP_INTERVAL)

    app_updated = client.apps.get(resource_group, service, name)
    return app_updated


# This function is deprecated, see app.py#app_create
def app_create(cmd, client, resource_group, service, name,
               assign_endpoint=None,
               cpu=None,
               memory=None,
               instance_count=None,
               disable_probe=None,
               runtime_version=None,
               jvm_options=None,
               env=None,
               enable_persistent_storage=None,
               assign_identity=None,
               persistent_storage=None,
               loaded_public_certificate_file=None):
    cpu = validate_cpu(cpu)
    memory = validate_memory(memory)
    apps = _get_all_apps(client, resource_group, service)
    if name in apps:
        raise CLIError("App '{}' already exists.".format(name))
    logger.warning("[1/4] Creating app with name '{}'".format(name))
    properties = models_20220101preview.AppResourceProperties()
    properties.temporary_disk = models_20220101preview.TemporaryDisk(
        size_in_gb=5, mount_path="/tmp")

    resource = client.services.get(resource_group, service)

    _validate_instance_count(resource.sku.tier, instance_count)

    if enable_persistent_storage:
        properties.persistent_disk = models_20220101preview.PersistentDisk(
            size_in_gb=_get_persistent_disk_size(resource.sku.tier), mount_path="/persistent")
    else:
        properties.persistent_disk = models_20220101preview.PersistentDisk(
            size_in_gb=0, mount_path="/persistent")

    if persistent_storage:
        data = get_file_json(persistent_storage, throw_on_empty=False)
        custom_persistent_disks = []

        if data:
            if not data.get('customPersistentDisks'):
                raise InvalidArgumentValueError("CustomPersistentDisks must be provided in the json file")
            for item in data['customPersistentDisks']:
                invalidProperties = not item.get('storageName') or \
                    not item.get('customPersistentDiskProperties').get('type') or \
                    not item.get('customPersistentDiskProperties').get('shareName') or \
                    not item.get('customPersistentDiskProperties').get('mountPath')
                if invalidProperties:
                    raise InvalidArgumentValueError("StorageName, Type, ShareName, MountPath mast be provided in the json file")
                storage_resource = client.storages.get(resource_group, service, item['storageName'])
                custom_persistent_disk_properties = models_20220101preview.AzureFileVolume(
                    type=item['customPersistentDiskProperties']['type'],
                    share_name=item['customPersistentDiskProperties']['shareName'],
                    mount_path=item['customPersistentDiskProperties']['mountPath'],
                    mount_options=item['customPersistentDiskProperties']['mountOptions'] if 'mountOptions' in item['customPersistentDiskProperties'] else None,
                    read_only=item['customPersistentDiskProperties']['readOnly'] if 'readOnly' in item['customPersistentDiskProperties'] else None)

                custom_persistent_disks.append(
                    models_20220101preview.CustomPersistentDiskResource(
                        storage_id=storage_resource.id,
                        custom_persistent_disk_properties=custom_persistent_disk_properties))
        properties.custom_persistent_disks = custom_persistent_disks

    if loaded_public_certificate_file is not None:
        data = get_file_json(loaded_public_certificate_file)
        if data:
            if not data.get('loadedCertificates'):
                raise FileOperationError("loadedCertificates must be provided in the json file")
            loaded_certificates = []
            for item in data['loadedCertificates']:
                invalidProperties = not item.get('certificateName') or not item.get('loadTrustStore')
                if invalidProperties:
                    raise FileOperationError("certificateName, loadTrustStore must be provided in the json file")
                certificate_resource = client.certificates.get(resource_group, service, item['certificateName'])
                loaded_certificates.append(models_20220101preview.
                                           LoadedCertificate(resource_id=certificate_resource.id,
                                                             load_trust_store=item['loadTrustStore']))
            properties.loaded_certificates = loaded_certificates

    app_resource = models_20220101preview.AppResource()
    app_resource.properties = properties
    app_resource.location = resource.location
    if assign_identity is True:
        app_resource.identity = models_20220101preview.ManagedIdentityProperties(type="systemassigned")

    poller = client.apps.begin_create_or_update(
        resource_group, service, name, app_resource)
    while poller.done() is False:
        sleep(APP_CREATE_OR_UPDATE_SLEEP_INTERVAL)

    # create default deployment
    logger.warning(
        "[2/4] Creating default deployment with name '{}'".format(DEFAULT_DEPLOYMENT_NAME))
    default_deployment_resource = _default_deployment_resource_builder(cpu, memory, env, jvm_options, runtime_version,
                                                                       instance_count, disable_probe, active=True)
    poller = client.deployments.begin_create_or_update(resource_group,
                                                       service,
                                                       name,
                                                       DEFAULT_DEPLOYMENT_NAME,
                                                       default_deployment_resource)

    logger.warning("[3/4] Setting default deployment to production")
    properties.public = assign_endpoint

    app_resource.location = resource.location

    app_poller = client.apps.begin_update(resource_group, service, name, app_resource)
    logger.warning(
        "[4/4] Updating app '{}' (this operation can take a while to complete)".format(name))
    while not poller.done() or not app_poller.done():
        sleep(DEPLOYMENT_CREATE_OR_UPDATE_SLEEP_INTERVAL)

    active_deployment = client.deployments.get(
        resource_group, service, name, DEFAULT_DEPLOYMENT_NAME)
    app = client.apps.get(resource_group, service, name)
    app.properties.active_deployment = active_deployment
    logger.warning("App create succeeded")
    return app


def _default_deployment_resource_builder(cpu, memory, env, jvm_options, runtime_version, instance_count, disable_probe=None, active=False):
    resource_requests = models_20220101preview.ResourceRequests(cpu=cpu, memory=memory)
    container_probe_settings = None
    if disable_probe is not None:
        container_probe_settings = models_20220101preview.ContainerProbeSettings(disable_probe=disable_probe)

    deployment_settings = models_20220101preview.DeploymentSettings(
        resource_requests=resource_requests,
        environment_variables=env,
        container_probe_settings=container_probe_settings)

    file_type = "NetCoreZip" if runtime_version == AppPlatformEnums.RuntimeVersion.NET_CORE31 else "Jar"
    user_source_info = _format_user_source(file_type, '<default>', runtime_version=runtime_version, jvm_options=jvm_options)
    properties = models_20220101preview.DeploymentResourceProperties(
        deployment_settings=deployment_settings,
        source=user_source_info,
        active=active)

    sku = models_20220101preview.Sku(name="S0", tier="STANDARD", capacity=instance_count)
    deployment_resource = models_20220101preview.DeploymentResource(properties=properties, sku=sku)
    return deployment_resource


def _format_user_source(file_type,
                        path,
                        artifact_selector=None,
                        jvm_options=None,
                        runtime_version=None,
                        main_entry=None,
                        version=None):
    if file_type == 'NetCoreZip':
        return models_20220101preview.NetCoreZipUploadedUserSourceInfo(
            relative_path=path,
            main_entry=main_entry,
            runtime_version=runtime_version,
            version=version
        )
    elif file_type == 'Jar':
        return models_20220101preview.JarUploadedUserSourceInfo(
            relative_path=path,
            runtime_version=runtime_version,
            jvm_options=jvm_options,
            version=version
        )
    elif file_type == 'Source':
        return models_20220101preview.SourceUploadedUserSourceInfo(
            relative_path=path,
            artifact_selector=artifact_selector,
            version=version
        )
    else:
        return None


# This function is deprecated, see app.py#app_update
def app_update(cmd, client, resource_group, service, name,
               assign_endpoint=None,
               deployment=None,
               runtime_version=None,
               jvm_options=None,
               main_entry=None,
               env=None,
               disable_probe=None,
               enable_persistent_storage=None,
               https_only=None,
               enable_end_to_end_tls=None,
               persistent_storage=None,
               loaded_public_certificate_file=None):
    resource = client.services.get(resource_group, service)
    location = resource.location

    properties = models_20220101preview.AppResourceProperties(public=assign_endpoint, https_only=https_only,
                                                              enable_end_to_end_tls=enable_end_to_end_tls)
    if enable_persistent_storage is True:
        properties.persistent_disk = models_20220101preview.PersistentDisk(
            size_in_gb=_get_persistent_disk_size(resource.sku.tier), mount_path="/persistent")
    if enable_persistent_storage is False:
        properties.persistent_disk = models_20220101preview.PersistentDisk(size_in_gb=0)

    if persistent_storage:
        data = get_file_json(persistent_storage, throw_on_empty=False)
        custom_persistent_disks = []

        if data:
            if not data.get('customPersistentDisks'):
                raise InvalidArgumentValueError("CustomPersistentDisks must be provided in the json file")
            for item in data['customPersistentDisks']:
                invalidProperties = not item.get('storageName') or \
                    not item.get('customPersistentDiskProperties').get('type') or \
                    not item.get('customPersistentDiskProperties').get('shareName') or \
                    not item.get('customPersistentDiskProperties').get('mountPath')
                if invalidProperties:
                    raise InvalidArgumentValueError("StorageName, Type, ShareName, MountPath mast be provided in the json file")
                storage_resource = client.storages.get(resource_group, service, item['storageName'])
                custom_persistent_disk_properties = models_20220101preview.AzureFileVolume(
                    type=item['customPersistentDiskProperties']['type'],
                    share_name=item['customPersistentDiskProperties']['shareName'],
                    mount_path=item['customPersistentDiskProperties']['mountPath'],
                    mount_options=item['customPersistentDiskProperties']['mountOptions'] if 'mountOptions' in item['customPersistentDiskProperties'] else None,
                    read_only=item['customPersistentDiskProperties']['readOnly'] if 'readOnly' in item['customPersistentDiskProperties'] else None)

                custom_persistent_disks.append(
                    models_20220101preview.CustomPersistentDiskResource(
                        storage_id=storage_resource.id,
                        custom_persistent_disk_properties=custom_persistent_disk_properties))
        properties.custom_persistent_disks = custom_persistent_disks
    if loaded_public_certificate_file is not None:
        data = get_file_json(loaded_public_certificate_file)
        if data:
            if not data.get('loadedCertificates'):
                raise CLIError("loadedCertificates must be provided in the json file")
            loaded_certificates = []
            for item in data['loadedCertificates']:
                invalidProperties = not item.get('certificateName') or not item.get('loadTrustStore')
                if invalidProperties:
                    raise CLIError("certificateName, loadTrustStore must be provided in the json file")
                certificate_resource = client.certificates.get(resource_group, service, item['certificateName'])
                loaded_certificates.append(models_20220101preview.
                                           LoadedCertificate(resource_id=certificate_resource.id,
                                                             load_trust_store=item['loadTrustStore']))
            properties.loaded_certificates = loaded_certificates

    app_resource = models_20220101preview.AppResource()
    app_resource.properties = properties
    app_resource.location = location

    logger.warning("[1/2] updating app '{}'".format(name))
    poller = client.apps.begin_update(
        resource_group, service, name, app_resource)
    while poller.done() is False:
        sleep(APP_CREATE_OR_UPDATE_SLEEP_INTERVAL)

    app_updated = client.apps.get(resource_group, service, name)

    logger.warning("[2/2] Updating deployment '{}'".format(deployment.name))
    container_probe_settings = None
    if disable_probe is not None:
        container_probe_settings = models_20220101preview.ContainerProbeSettings(disable_probe=disable_probe)

    source_type = deployment.properties.source.type
    if source_type in ['Jar', 'NetCoreZip'] and (jvm_options or main_entry or runtime_version):
        source = _format_user_source(deployment.properties.source.type,
                                     deployment.properties.source.relative_path,
                                     jvm_options=jvm_options,
                                     runtime_version=runtime_version,
                                     main_entry=main_entry)

    deployment_settings = models_20220101preview.DeploymentSettings(
        environment_variables=env,
        container_probe_settings=container_probe_settings)
    properties = models_20220101preview.DeploymentResourceProperties(
        source=source,
        deployment_settings=deployment_settings)
    deployment_resource = models_20220101preview.DeploymentResource(properties=properties)
    poller = client.deployments.begin_update(
        resource_group, service, name, deployment.name, deployment_resource)
    while poller.done() is False:
        sleep(DEPLOYMENT_CREATE_OR_UPDATE_SLEEP_INTERVAL)

    deployment = client.deployments.get(
        resource_group, service, name, deployment.name)
    app_updated.properties.active_deployment = deployment
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


# This function is deprecated, see app.py#app_deploy
def app_deploy(cmd, client, resource_group, service, name,
               version=None,
               deployment=None,
               disable_validation=None,
               artifact_path=None,
               source_path=None,
               target_module=None,
               runtime_version=None,
               jvm_options=None,
               main_entry=None,
               env=None,
               disable_probe=None,
               container_image=None,
               container_registry=None,
               registry_username=None,
               registry_password=None,
               container_command=None,
               container_args=None,
               no_wait=False):
    logger.warning(LOG_RUNNING_PROMPT)

    old_deployment = client.deployments.get(resource_group, service, name, deployment.name)

    file_type, file_path = _get_upload_local_file(runtime_version, artifact_path, source_path, container_image)
    if file_type == 'Container':
        if old_deployment.properties.source and old_deployment.properties.source.type == 'Container':
            return _app_deploy_container(client, resource_group, service, name, deployment.name,
                                         None,
                                         None,
                                         None,
                                         env,
                                         disable_probe,
                                         container_image,
                                         container_registry,
                                         registry_username,
                                         registry_password,
                                         container_command,
                                         container_args,
                                         no_wait,
                                         True)
        else:
            return _app_deploy_container(client, resource_group, service, name, deployment.name,
                                         old_deployment.properties.deployment_settings.resource_requests.cpu,
                                         old_deployment.properties.deployment_settings.resource_requests.memory,
                                         old_deployment.sku.capacity,
                                         env,
                                         disable_probe,
                                         container_image,
                                         container_registry,
                                         registry_username,
                                         registry_password,
                                         container_command,
                                         container_args,
                                         no_wait,
                                         False)
    else:
        return _app_deploy(client,
                           resource_group,
                           service,
                           name,
                           deployment,
                           version,
                           file_path,
                           runtime_version,
                           jvm_options,
                           None,
                           None,
                           None,
                           env,
                           disable_probe,
                           main_entry,
                           target_module,
                           no_wait,
                           file_type,
                           True)


def app_scale(cmd, client, resource_group, service, name,
              deployment=None,
              cpu=None,
              memory=None,
              instance_count=None,
              no_wait=False):
    cpu = validate_cpu(cpu)
    memory = validate_memory(memory)

    resource = client.services.get(resource_group, service)
    _validate_instance_count(resource.sku.tier, instance_count)

    resource_requests = models_20220101preview.ResourceRequests(cpu=cpu, memory=memory)

    deployment_settings = models_20220101preview.DeploymentSettings(resource_requests=resource_requests)
    properties = models_20220101preview.DeploymentResourceProperties(
        deployment_settings=deployment_settings)
    sku = models_20220101preview.Sku(name="S0", tier="STANDARD", capacity=instance_count)
    deployment_resource = models_20220101preview.DeploymentResource(properties=properties, sku=sku)
    return sdk_no_wait(no_wait, client.deployments.begin_update,
                       resource_group, service, name, deployment.name, deployment_resource)


def app_get_build_log(cmd, client, resource_group, service, name, deployment):
    if deployment.properties.source.type != "Source":
        raise CLIError("{} deployment has no build logs.".format(deployment.properties.source.type))
    return stream_logs(client.deployments, resource_group, service, name, deployment.name)


def app_tail_log(cmd, client, resource_group, service, name,
                 deployment=None, instance=None, follow=False, lines=50, since=None, limit=2048, format_json=None):
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

    log_stream = LogStream(client, resource_group, service)
    if not log_stream:
        raise CLIError("To use the log streaming feature, please enable the test endpoint by running 'az spring-cloud test-endpoint enable -n {0} -g {1}'".format(service, resource_group))

    streaming_url = "https://{0}/api/logstream/apps/{1}/instances/{2}".format(
        log_stream.base_url, name, instance)
    params = {}
    params["tailLines"] = lines
    params["limitBytes"] = limit
    if since:
        params["sinceSeconds"] = since
    if follow:
        params["follow"] = True

    exceptions = []
    streaming_url += "?{}".format(parse.urlencode(params)) if params else ""
    t = Thread(target=_get_app_log, args=(
        streaming_url, "primary", log_stream.primary_key, format_json, exceptions))
    t.daemon = True
    t.start()

    while t.is_alive():
        sleep(5)  # so that ctrl+c can stop the command

    if exceptions:
        raise exceptions[0]


def app_identity_assign(cmd, client, resource_group, service, name, role=None, scope=None):
    app_resource = models_20220101preview.AppResource()
    identity = models_20220101preview.ManagedIdentityProperties(type="systemassigned")
    properties = models_20220101preview.AppResourceProperties()
    resource = client.services.get(resource_group, service)
    location = resource.location

    app_resource.identity = identity
    app_resource.properties = properties
    app_resource.location = location
    client.apps.begin_update(resource_group, service, name, app_resource)
    app = client.apps.get(resource_group, service, name)
    if role:
        principal_id = app.identity.principal_id

        from azure.cli.core.commands import arm as _arm
        identity_role_id = _arm.resolve_role_id(cmd.cli_ctx, role, scope)
        assignments_client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_AUTHORIZATION).role_assignments
        RoleAssignmentCreateParameters = get_sdk(cmd.cli_ctx, ResourceType.MGMT_AUTHORIZATION,
                                                 'RoleAssignmentCreateParameters', mod='models',
                                                 operation_group='role_assignments')
        parameters = RoleAssignmentCreateParameters(role_definition_id=identity_role_id, principal_id=principal_id)
        logger.info("Creating an assignment with a role '%s' on the scope of '%s'", identity_role_id, scope)
        retry_times = 36
        assignment_name = _arm._gen_guid()
        for i in range(0, retry_times):
            try:
                assignments_client.create(scope=scope, role_assignment_name=assignment_name,
                                          parameters=parameters)
                break
            except HttpResponseError as ex:
                if 'role assignment already exists' in ex.message:
                    logger.info('Role assignment already exists')
                    break
                elif i < retry_times and ' does not exist in the directory ' in ex.message:
                    sleep(APP_CREATE_OR_UPDATE_SLEEP_INTERVAL)
                    logger.warning('Retrying role assignment creation: %s/%s', i + 1,
                                   retry_times)
                    continue
                else:
                    raise
    return app


def app_identity_remove(cmd, client, resource_group, service, name):
    app_resource = models_20220101preview.AppResource()
    identity = models_20220101preview.ManagedIdentityProperties(type="none")
    properties = models_20220101preview.AppResourceProperties()
    resource = client.services.get(resource_group, service)
    location = resource.location

    app_resource.identity = identity
    app_resource.properties = properties
    app_resource.location = location
    return client.apps.begin_update(resource_group, service, name, app_resource)


def app_identity_show(cmd, client, resource_group, service, name):
    app = client.apps.get(resource_group, service, name)
    return app.identity


def app_set_deployment(cmd, client, resource_group, service, name, deployment):
    active_deployment_collection = models_20220101preview.ActiveDeploymentCollection(
        active_deployment_names=[deployment]
    )
    return client.apps.begin_set_active_deployments(resource_group, service, name, active_deployment_collection)


def app_unset_deployment(cmd, client, resource_group, service, name):
    active_deployment_collection = models_20220101preview.ActiveDeploymentCollection(
        active_deployment_names=[]
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

    loaded_certificates.append(models_20220101preview.
                               LoadedCertificate(resource_id=certificate_resource_id,
                                                 load_trust_store=load_trust_store))

    app_resource.properties.loaded_certificates = loaded_certificates
    logger.warning("[1/1] updating app '{}'".format(name))

    poller = client.apps.begin_update(
        resource_group, service, name, app_resource)
    while poller.done() is False:
        sleep(APP_CREATE_OR_UPDATE_SLEEP_INTERVAL)

    app_updated = client.apps.get(resource_group, service, name)
    return app_updated


# This function is deprecated, see app.py#deployment_create
def deployment_create(cmd, client, resource_group, service, app, name,
                      skip_clone_settings=False,
                      version=None,
                      artifact_path=None,
                      source_path=None,
                      disable_validation=None,
                      target_module=None,
                      runtime_version=None,
                      jvm_options=None,
                      main_entry=None,
                      cpu=None,
                      memory=None,
                      instance_count=None,
                      env=None,
                      disable_probe=None,
                      container_image=None,
                      container_registry=None,
                      registry_username=None,
                      registry_password=None,
                      container_command=None,
                      container_args=None,
                      no_wait=False):
    cpu = validate_cpu(cpu)
    memory = validate_memory(memory)
    logger.warning(LOG_RUNNING_PROMPT)
    deployments = _get_all_deployments(client, resource_group, service, app)
    if any(iter(x for x in deployments if x.name == name)):
        raise CLIError("Deployment " + name + " already exists")

    resource = client.services.get(resource_group, service)
    _validate_instance_count(resource.sku.tier, instance_count)

    if not skip_clone_settings:
        active_deployment = next(iter(x for x in deployments if x.properties.active), None)
        if not active_deployment:
            logger.warning("No production deployment found, use --skip-clone-settings to skip copying settings from "
                           "production deployment.")
        else:
            cpu = cpu or active_deployment.properties.deployment_settings.resource_requests.cpu
            memory = memory or active_deployment.properties.deployment_settings.resource_requests.memory
            instance_count = instance_count or active_deployment.sku.capacity
            jvm_options = jvm_options or (active_deployment.properties.source.jvm_options if hasattr(active_deployment.properties.source, 'jvm_options') else None)
            env = env or active_deployment.properties.deployment_settings.environment_variables
            if active_deployment.properties.deployment_settings.container_probe_settings is not None:
                disable_probe = disable_probe or active_deployment.properties.deployment_settings.container_probe_settings.disable_probe
    else:
        cpu = cpu or "1"
        memory = memory or "1Gi"
        instance_count = instance_count or 1

    file_type, file_path = _get_upload_local_file(runtime_version, artifact_path, source_path, container_image)
    if file_type == 'Container':
        return _app_deploy_container(client, resource_group, service, app, name,
                                     cpu,
                                     memory,
                                     instance_count,
                                     env,
                                     disable_probe,
                                     container_image,
                                     container_registry,
                                     registry_username,
                                     registry_password,
                                     container_command,
                                     container_args,
                                     no_wait)
    else:
        return _app_deploy(client, resource_group, service, app, name, version, file_path,
                           runtime_version,
                           jvm_options,
                           cpu,
                           memory,
                           instance_count,
                           env,
                           disable_probe,
                           main_entry,
                           target_module,
                           no_wait,
                           file_type)


def _validate_instance_count(sku, instance_count=None):
    if instance_count is not None:
        sku = sku.upper()
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
    diagnostic_parameters = models_20220101preview.DiagnosticParameters(app_instance=app_instance, file_path=file_path)
    logger.info("Heap dump is triggered.")
    return client.deployments.begin_generate_heap_dump(resource_group, service, app, deployment.name, diagnostic_parameters)


def deployment_generate_thread_dump(cmd, client, resource_group, service, app, app_instance, file_path,
                                    deployment=None):
    diagnostic_parameters = models_20220101preview.DiagnosticParameters(app_instance=app_instance, file_path=file_path)
    logger.info("Thread dump is triggered.")
    return client.deployments.begin_generate_thread_dump(resource_group, service, app, deployment.name, diagnostic_parameters)


def deployment_start_jfr(cmd, client, resource_group, service, app, app_instance, file_path, duration=None,
                         deployment=None):
    diagnostic_parameters = models_20220101preview.DiagnosticParameters(app_instance=app_instance, file_path=file_path,
                                                                        duration=duration)
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


def config_set(cmd, client, resource_group, name, config_file, no_wait=False):
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
    config_server_properties = models.ConfigServerProperties(config_server=config_server_settings)

    logger.warning("[1/2] Validating config server settings")
    validate_config_server_settings(client, resource_group, name, config_server_settings)
    logger.warning("[2/2] Updating config server settings, (this operation can take a while to complete)")

    config_server_resource = models.ConfigServerResource(properties=config_server_properties)
    return sdk_no_wait(no_wait, client.begin_update_put, resource_group, name, config_server_resource)


def config_get(cmd, client, resource_group, name):
    config_server_resource = client.get(resource_group, name)

    if not config_server_resource.properties.config_server:
        raise CLIError("Config server not set.")
    return config_server_resource


def config_delete(cmd, client, resource_group, name):
    config_server_properties = models.ConfigServerProperties()
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
    config_server_properties = models.ConfigServerProperties(config_server=config_server_settings)

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


def _get_all_deployments(client, resource_group, service, app):
    deployments_resource = client.deployments.list(
        resource_group, service, app)
    return [x for x in deployments_resource]


def _get_all_apps(client, resource_group, service):
    apps = []
    apps_resource = client.apps.list(resource_group, service)
    apps = list(apps_resource)
    apps = (app.name for app in apps)
    return apps


# pylint: disable=too-many-locals, no-member
def _app_deploy(client, resource_group, service, app, name, version, path, runtime_version, jvm_options, cpu, memory,
                instance_count,
                env,
                disable_probe=None,
                main_entry=None,
                target_module=None,
                no_wait=False,
                file_type=None,
                update=False):
    if file_type is None:
        # update means command is az spring-cloud app deploy xxx
        if update:
            raise RequiredArgumentMissingError(
                "One of the following arguments are required: '--artifact-path' or '--source-path'")
        # if command is az spring-cloud app deployment create xxx, create default deployment
        else:
            logger.warning(
                "Creating default deployment without artifact/source folder. Please specify the --artifact-path/--source-path argument explicitly if needed.")
            default_deployment_resource = _default_deployment_resource_builder(cpu, memory, env, jvm_options,
                                                                               runtime_version, instance_count, disable_probe)
            return sdk_no_wait(no_wait, client.deployments.begin_create_or_update,
                               resource_group, service, app, name, default_deployment_resource)
    upload_url = None
    relative_path = None
    logger.warning("file_type is {}".format(file_type))
    logger.warning("[1/3] Requesting for upload URL")
    try:
        response = client.apps.get_resource_upload_url(resource_group, service, app)
        upload_url = response.upload_url
        relative_path = response.relative_path
    except (AttributeError, HttpResponseError) as e:
        raise CLIError(
            "Failed to get a SAS URL to upload context. Error: {}".format(e.message))

    resource_requests = None
    if cpu is not None or memory is not None:
        resource_requests = models_20220101preview.ResourceRequests(cpu=cpu, memory=memory)

    container_probe_settings = None
    if disable_probe is not None:
        container_probe_settings = models_20220101preview.ContainerProbeSettings(disable_probe=disable_probe)

    deployment_settings = models_20220101preview.DeploymentSettings(
        resource_requests=resource_requests,
        environment_variables=env,
        container_probe_settings=container_probe_settings)
    sku = models_20220101preview.Sku(name="S0", tier="STANDARD", capacity=instance_count)
    user_source_info = _format_user_source(file_type,
                                           relative_path,
                                           artifact_selector=target_module,
                                           jvm_options=jvm_options,
                                           runtime_version=runtime_version,
                                           main_entry=main_entry,
                                           version=version)
    properties = models_20220101preview.DeploymentResourceProperties(
        deployment_settings=deployment_settings,
        source=user_source_info)
    # upload file
    if not upload_url:
        raise CLIError("Failed to get a SAS URL to upload context.")
    account_name, endpoint_suffix, share_name, relative_name, sas_token = get_azure_files_info(upload_url)
    logger.warning("[2/3] Uploading package to blob")
    file_service = FileService(account_name, sas_token=sas_token, endpoint_suffix=endpoint_suffix)
    file_service.create_file_from_path(share_name, None, relative_name, path)

    if file_type == "Source" and not no_wait:
        def get_log_url():
            try:
                log_file_url_response = client.deployments.get_log_file_url(
                    resource_group_name=resource_group,
                    service_name=service,
                    app_name=app,
                    deployment_name=name)
                if not log_file_url_response:
                    return None
                return log_file_url_response.url
            except HttpResponseError:
                return None

        def get_logs_loop():
            log_url = None
            while not log_url or log_url == old_log_url:
                log_url = get_log_url()
                sleep(10)

            logger.warning("Trying to fetch build logs")
            stream_logs(client.deployments, resource_group, service,
                        app, name, logger_level_func=print)

        old_log_url = get_log_url()

        timer = Timer(3, get_logs_loop)
        timer.daemon = True
        timer.start()

    # create deployment
    logger.warning(
        "[3/3] Updating deployment in app '{}' (this operation can take a while to complete)".format(app))
    deployment_resource = models.DeploymentResource(properties=properties, sku=sku)
    if update:
        return sdk_no_wait(no_wait, client.deployments.begin_update,
                           resource_group, service, app, name, deployment_resource)

    return sdk_no_wait(no_wait, client.deployments.begin_create_or_update,
                       resource_group, service, app, name, deployment_resource)


# pylint: disable=too-many-locals, no-member
def _app_deploy_container(client, resource_group, service, app, name, cpu, memory,
                          instance_count,
                          env,
                          disable_probe,
                          container_image,
                          container_registry,
                          registry_username,
                          registry_password,
                          container_command,
                          container_args,
                          no_wait=False,
                          update=False):
    resource_requests = None
    if cpu is not None or memory is not None:
        resource_requests = models_20220101preview.ResourceRequests(cpu=cpu, memory=memory)
    if container_command is not None:
        container_command = shlex.split(container_command)
    if container_args is not None:
        container_args = shlex.split(container_args)

    container_probe_settings = None
    if disable_probe is not None:
        container_probe_settings = models_20220101preview.ContainerProbeSettings(disable_probe=disable_probe)

    deployment_settings = models_20220101preview.DeploymentSettings(
        resource_requests=resource_requests,
        environment_variables=env,
        container_probe_settings=container_probe_settings)
    sku = models_20220101preview.Sku(name="S0", tier="STANDARD", capacity=instance_count)
    image_registry_credential = models_20220101preview.ImageRegistryCredential(
        username=registry_username,
        password=registry_password    # [SuppressMessage("Microsoft.Security", "CS001:SecretInline", Justification="false positive")]
    ) if registry_username is not None and registry_password is not None else None
    custom_container = models_20220101preview.CustomContainer(
        server=container_registry,
        container_image=container_image,
        command=container_command,
        args=container_args,
        image_registry_credential=image_registry_credential,
    )
    user_source_info = models_20220101preview.CustomContainerUserSourceInfo(
        custom_container=custom_container)
    properties = models_20220101preview.DeploymentResourceProperties(
        deployment_settings=deployment_settings,
        source=user_source_info)

    # create deployment
    logger.warning(
        "Updating deployment in app '{}' (this operation can take a while to complete)".format(app))
    deployment_resource = models_20220101preview.DeploymentResource(properties=properties, sku=sku)
    if update:
        return sdk_no_wait(no_wait, client.deployments.begin_update,
                           resource_group, service, app, name, deployment_resource)

    return sdk_no_wait(no_wait, client.deployments.begin_create_or_update,
                       resource_group, service, app, name, deployment_resource)


# pylint: disable=bare-except, too-many-statements
def _get_app_log(url, user_name, password, format_json, exceptions):
    logger_seg_regex = re.compile(r'([^\.])[^\.]+\.')

    def build_log_shortener(length):
        if length <= 0:
            raise InvalidArgumentValueError('Logger length in `logger{length}` should be positive')

        def shortener(record):
            '''
            Try shorten the logger property to the specified length before feeding it to the formatter.
            '''
            logger_name = record.get('logger', None)
            if logger_name is None:
                return record

            # first, try to shorten the package name to one letter, e.g.,
            #     org.springframework.cloud.netflix.eureka.config.DiscoveryClientOptionalArgsConfiguration
            # to: o.s.c.n.e.c.DiscoveryClientOptionalArgsConfiguration
            while len(logger_name) > length:
                logger_name, count = logger_seg_regex.subn(r'\1.', logger_name, 1)
                if count < 1:
                    break

            # then, cut off the leading packages if necessary
            logger_name = logger_name[-length:]
            record['logger'] = logger_name
            return record

        return shortener

    def build_formatter():
        '''
        Build the log line formatter based on the format_json argument.
        '''
        nonlocal format_json

        def identity(o):
            return o

        if format_json is None or len(format_json) == 0:
            return identity

        logger_regex = re.compile(r'\blogger\{(\d+)\}')
        match = logger_regex.search(format_json)
        pre_processor = identity
        if match:
            length = int(match[1])
            pre_processor = build_log_shortener(length)
            format_json = logger_regex.sub('logger', format_json, 1)

        first_exception = True

        def format_line(line):
            nonlocal first_exception
            try:
                log_record = json.loads(line)
                # Add n=\n so that in Windows CMD it's easy to specify customized format with line ending
                # e.g., "{timestamp} {message}{n}"
                # (Windows CMD does not escape \n in string literal.)
                return format_json.format_map(pre_processor(defaultdict(str, n="\n", **log_record)))
            except:
                if first_exception:
                    # enable this format error logging only with --verbose
                    logger.info("Failed to format log line '{}'".format(line), exc_info=sys.exc_info())
                    first_exception = False
                return line

        return format_line

    def iter_lines(response, limit=2 ** 20):
        '''
        Returns a line iterator from the response content. If no line ending was found and the buffered content size is
        larger than the limit, the buffer will be yielded directly.
        '''
        buffer = []
        total = 0
        for content in response.iter_content(chunk_size=None):
            if not content:
                if len(buffer) > 0:
                    yield b''.join(buffer)
                break

            start = 0
            while start < len(content):
                line_end = content.find(b'\n', start)
                should_print = False
                if line_end < 0:
                    next = (content if start == 0 else content[start:])
                    buffer.append(next)
                    total += len(next)
                    start = len(content)
                    should_print = total >= limit
                else:
                    buffer.append(content[start:line_end + 1])
                    start = line_end + 1
                    should_print = True

                if should_print:
                    yield b''.join(buffer)
                    buffer.clear()
                    total = 0

    with requests.get(url, stream=True, auth=HTTPBasicAuth(user_name, password)) as response:
        try:
            if response.status_code != 200:
                raise CLIError("Failed to connect to the server with status code '{}' and reason '{}'".format(
                    response.status_code, response.reason))
            std_encoding = sys.stdout.encoding

            formatter = build_formatter()

            for line in iter_lines(response):
                decoded = (line.decode(encoding='utf-8', errors='replace')
                           .encode(std_encoding, errors='replace')
                           .decode(std_encoding, errors='replace'))
                print(formatter(decoded), end='')

        except CLIError as e:
            exceptions.append(e)


def storage_callback(pipeline_response, deserialized, headers):
    return models_20220101preview.StorageResource.deserialize(json.loads(pipeline_response.http_response.text()))


def storage_add(client, resource_group, service, name, storage_type, account_name, account_key):
    properties = None
    if storage_type == 'StorageAccount':
        properties = models_20220101preview.StorageAccount(
            storage_type=storage_type,
            account_name=account_name,
            account_key=account_key)

    return client.storages.begin_create_or_update(
        resource_group_name=resource_group,
        service_name=service,
        storage_name=name,
        storage_resource=models_20220101preview.StorageResource(properties=properties),
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
        properties = models_20220101preview.StorageAccount(
            storage_type=storage_type,
            account_name=account_name,
            account_key=account_key)

    return client.storages.begin_create_or_update(
        resource_group_name=resource_group,
        service_name=service,
        storage_name=name,
        storage_resource=models_20220101preview.StorageResource(properties=properties),
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
                    vault_uri=None, vault_certificate_name=None, public_certificate_file=None):
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
        properties = models_20220101preview.KeyVaultCertificateProperties(
            type="KeyVaultCertificate",
            vault_uri=vault_uri,
            key_vault_cert_name=vault_certificate_name,
            exclude_private_key=only_public_cert
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
        properties = models_20220101preview.ContentCertificateProperties(
            type="ContentCertificate",
            content=content
        )
    certificate_resource = models_20220101preview.CertificateResource(properties=properties)

    def callback(pipeline_response, deserialized, headers):
        return models_20220101preview.CertificateResource.deserialize(json.loads(pipeline_response.http_response.text()))

    return client.certificates.begin_create_or_update(
        resource_group_name=resource_group,
        service_name=service,
        certificate_name=name,
        certificate_resource=certificate_resource,
        cls=callback
    )


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
                enable_end_to_end_tls=None):
    properties = models.CustomDomainProperties()
    if certificate is not None:
        certificate_response = client.certificates.get(resource_group, service, certificate)
        properties = models.CustomDomainProperties(
            thumbprint=certificate_response.properties.thumbprint,
            cert_name=certificate
        )
    if enable_end_to_end_tls is not None:
        _update_app_e2e_tls(cmd, client, resource_group, service, app, enable_end_to_end_tls)

    custom_domain_resource = models.CustomDomainResource(properties=properties)
    return client.custom_domains.begin_create_or_update(resource_group, service, app,
                                                        domain_name, custom_domain_resource)


def _update_app_e2e_tls(cmd, client, resource_group, service, app, enable_end_to_end_tls):
    resource = client.services.get(resource_group, service)
    location = resource.location

    properties = models_20220101preview.AppResourceProperties(enable_end_to_end_tls=enable_end_to_end_tls)
    app_resource = models_20220101preview.AppResource()
    app_resource.properties = properties
    app_resource.location = location

    logger.warning("Set end to end tls for app '{}'".format(app))
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
                  enable_end_to_end_tls=None):
    properties = models.CustomDomainProperties()
    if certificate is not None:
        certificate_response = client.certificates.get(resource_group, service, certificate)
        properties = models.CustomDomainProperties(
            thumbprint=certificate_response.properties.thumbprint,
            cert_name=certificate
        )
    if enable_end_to_end_tls is not None:
        _update_app_e2e_tls(cmd, client, resource_group, service, app, enable_end_to_end_tls)

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
                monitoring_setting_properties = models_20201101preview.MonitoringSettingProperties(
                    trace_enabled=True, app_insights_instrumentation_key=created_app_insights.connection_string)
        except Exception:  # pylint: disable=broad-except
            logger.warning(
                'Error while trying to create and configure an Application Insights for the Azure Spring Cloud. '
                'Please use the Azure Portal to create and configure the Application Insights, if needed.')
            return None
    if monitoring_setting_properties:
        monitoring_setting_properties.app_insights_sampling_rate = sampling_rate
    return monitoring_setting_properties


def _get_monitoring_setting(cmd, resource_group, app_insights_key, app_insights):
    monitoring_setting_properties = None
    if app_insights_key:
        monitoring_setting_properties = models_20201101preview.MonitoringSettingProperties(
            trace_enabled=True,
            app_insights_instrumentation_key=app_insights_key)
    elif app_insights:
        connection_string = _get_connection_string_from_app_insights(cmd, resource_group, app_insights)
        monitoring_setting_properties = models_20201101preview.MonitoringSettingProperties(
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
    creation_failed_warn = 'Unable to create the Application Insights for the Azure Spring Cloud. ' \
                           'Please use the Azure Portal to manually create and configure the Application Insights, ' \
                           'if needed.'

    ai_resource_group_name = resource_group
    ai_name = name
    ai_location = location

    app_insights_client = get_mgmt_service_client(cmd.cli_ctx, ApplicationInsightsManagementClient)
    ai_properties = {
        "name": ai_name,
        "location": ai_location,
        "kind": "web",
        "properties": {
            "Application_Type": "web"
        }
    }
    appinsights = app_insights_client.components.create_or_update(ai_resource_group_name, ai_name, ai_properties)
    if appinsights is None or appinsights.connection_string is None:
        logger.warning(creation_failed_warn)
        return None

    portal_url = get_portal_uri(cmd.cli_ctx)
    # We make this success message as a warning to no interfere with regular JSON output in stdout
    logger.warning('Application Insights \"%s\" was created for this Azure Spring Cloud. '
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
        monitoring_setting_properties = models_20201101preview.MonitoringSettingProperties(trace_enabled=False)
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
            monitoring_setting_properties = models_20201101preview.MonitoringSettingProperties(
                trace_enabled=True,
                app_insights_instrumentation_key=connection_string,
                app_insights_sampling_rate=sampling_rate)
        elif monitoring_setting_properties.app_insights_sampling_rate is not None:
            monitoring_setting_properties = models_20201101preview.MonitoringSettingProperties(
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
