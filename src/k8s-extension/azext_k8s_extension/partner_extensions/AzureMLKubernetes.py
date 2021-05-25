# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument
import copy
from hashlib import md5
from typing import Any, Dict, List, Tuple

import azure.mgmt.relay
import azure.mgmt.relay.models
import azure.mgmt.resource.locks
import azure.mgmt.servicebus
import azure.mgmt.servicebus.models
import azure.mgmt.storage
import azure.mgmt.storage.models
import azure.mgmt.loganalytics
import azure.mgmt.loganalytics.models
from ..vendored_sdks.models import (
    ExtensionInstance, ExtensionInstanceUpdate, Scope, ScopeCluster)
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_subscription_id
from azure.mgmt.resource.locks.models import ManagementLockObject
from knack.log import get_logger
from msrestazure.azure_exceptions import CloudError

from .._client_factory import cf_resources
from .PartnerExtensionModel import PartnerExtensionModel

logger = get_logger(__name__)

resource_tag = {'created_by': 'Azure Arc-enabled ML'}


class AzureMLKubernetes(PartnerExtensionModel):
    def __init__(self):
        # constants for configuration settings.
        self.DEFAULT_RELEASE_NAMESPACE = 'azureml'
        self.RELAY_CONNECTION_STRING_KEY = 'relayserver.relayConnectionString'
        self.RELAY_CONNECTION_STRING_DEPRECATED_KEY = 'RelayConnectionString'  # for 3rd party deployment, will be deprecated
        self.HC_RESOURCE_ID_KEY = 'relayserver.hybridConnectionResourceID'
        self.RELAY_HC_NAME_KEY = 'relayserver.hybridConnectionName'
        self.SERVICE_BUS_CONNECTION_STRING_KEY = 'servicebus.connectionString'
        self.SERVICE_BUS_RESOURCE_ID_KEY = 'servicebus.resourceID'
        self.SERVICE_BUS_TOPIC_SUB_MAPPING_KEY = 'servicebus.topicSubMapping'
        self.AZURE_LOG_ANALYTICS_ENABLED_KEY = 'azure_log_analytics.enabled'
        self.AZURE_LOG_ANALYTICS_CUSTOMER_ID_KEY = 'azure_log_analytics.customer_id'
        self.AZURE_LOG_ANALYTICS_CONNECTION_STRING = 'azure_log_analytics.connection_string'
        self.JOB_SCHEDULER_LOCATION_KEY = 'jobSchedulerLocation'
        self.CLUSTER_NAME_FRIENDLY_KEY = 'cluster_name_friendly'

        # component flag
        self.ENABLE_TRAINING = 'enableTraining'
        self.ENABLE_INFERENCE = 'enableInference'

        # constants for determine whether create underlying azure resource
        self.RELAY_SERVER_CONNECTION_STRING = 'relayServerConnectionString'  # create relay connection string if None
        self.SERVICE_BUS_CONNECTION_STRING = 'serviceBusConnectionString'  # create service bus if None
        self.LOG_ANALYTICS_WS_ENABLED = 'logAnalyticsWS'  # create log analytics workspace if true

        # constants for azure resources creation
        self.RELAY_HC_AUTH_NAME = 'azureml_rw'
        self.SERVICE_BUS_COMPUTE_STATE_TOPIC = 'computestate-updatedby-computeprovider'
        self.SERVICE_BUS_COMPUTE_STATE_SUB = 'compute-scheduler-computestate'
        self.SERVICE_BUS_JOB_STATE_TOPIC = 'jobstate-updatedby-computeprovider'
        self.SERVICE_BUS_JOB_STATE_SUB = 'compute-scheduler-jobstate'

        # reference mapping
        self.reference_mapping = {
            self.RELAY_SERVER_CONNECTION_STRING: [self.RELAY_CONNECTION_STRING_KEY, self.RELAY_CONNECTION_STRING_DEPRECATED_KEY],
            self.SERVICE_BUS_CONNECTION_STRING: [self.SERVICE_BUS_CONNECTION_STRING_KEY],
            'cluster_name': ['clusterId', 'prometheus.prometheusSpec.externalLabels.cluster_name'],
        }

    def Create(self, cmd, client, resource_group_name, cluster_name, name, cluster_type, extension_type,
               scope, auto_upgrade_minor_version, release_train, version, target_namespace,
               release_namespace, configuration_settings, configuration_protected_settings,
               configuration_settings_file, configuration_protected_settings_file):
        if scope == 'namespace':
            raise InvalidArgumentValueError("Invalid scope '{}'.  This extension can be installed "
                                            "only at 'cluster' scope.".format(scope))
        if not release_namespace:
            release_namespace = self.DEFAULT_RELEASE_NAMESPACE
        scope_cluster = ScopeCluster(release_namespace=release_namespace)
        ext_scope = Scope(cluster=scope_cluster, namespace=None)

        # validate the config
        self.__validate_config(configuration_settings, configuration_protected_settings)

        # get the arc's location
        subscription_id = get_subscription_id(cmd.cli_ctx)
        cluster_rp, parent_api_version = _get_cluster_rp_api_version(cluster_type)
        cluster_resource_id = '/subscriptions/{0}/resourceGroups/{1}/providers/{2}' \
            '/{3}/{4}'.format(subscription_id, resource_group_name, cluster_rp, cluster_type, cluster_name)
        cluster_location = ''
        resources = cf_resources(cmd.cli_ctx, subscription_id)
        try:
            resource = resources.get_by_id(
                cluster_resource_id, parent_api_version)
            cluster_location = resource.location.lower()
        except CloudError as ex:
            raise ex

        # generate values for the extension if none is set.
        configuration_settings['cluster_name'] = configuration_settings.get('cluster_name', cluster_resource_id)
        configuration_settings['domain'] = configuration_settings.get(
            'doamin', '{}.cloudapp.azure.com'.format(cluster_location))
        configuration_settings['location'] = configuration_settings.get('location', cluster_location)
        configuration_settings[self.JOB_SCHEDULER_LOCATION_KEY] = configuration_settings.get(
            self.JOB_SCHEDULER_LOCATION_KEY, cluster_location)
        configuration_settings[self.CLUSTER_NAME_FRIENDLY_KEY] = configuration_settings.get(
            self.CLUSTER_NAME_FRIENDLY_KEY, cluster_name)

        # create Azure resources need by the extension based on the config.
        self.__create_required_resource(
            cmd, configuration_settings, configuration_protected_settings, subscription_id, resource_group_name,
            cluster_name, cluster_location)

        # dereference
        configuration_settings = _dereference(self.reference_mapping, configuration_settings)
        configuration_protected_settings = _dereference(self.reference_mapping, configuration_protected_settings)

        # If release-train is not input, set it to 'stable'
        if release_train is None:
            release_train = 'stable'

        create_identity = True
        extension_instance = ExtensionInstance(
            extension_type=extension_type,
            auto_upgrade_minor_version=auto_upgrade_minor_version,
            release_train=release_train,
            version=version,
            scope=ext_scope,
            configuration_settings=configuration_settings,
            configuration_protected_settings=configuration_protected_settings,
            identity=None,
            location=""
        )
        return extension_instance, name, create_identity

    def Update(self, extension, auto_upgrade_minor_version, release_train, version):
        return ExtensionInstanceUpdate(
            auto_upgrade_minor_version=auto_upgrade_minor_version,
            release_train=release_train,
            version=version
        )

    def __validate_config(self, configuration_settings, configuration_protected_settings):
        # perform basic validation of the input config
        config_keys = configuration_settings.keys()
        config_protected_keys = configuration_protected_settings.keys()
        dup_keys = set(config_keys) & set(config_protected_keys)
        if len(dup_keys) > 0:
            for key in dup_keys:
                logger.warning(
                    'Duplicate keys found in both configuration settings and configuration protected setttings: %s', key)
            raise InvalidArgumentValueError("Duplicate keys found.")

        enable_training = _get_value_from_config_protected_config(
            self.ENABLE_TRAINING, configuration_settings, configuration_protected_settings)
        enable_training = str(enable_training).lower() == 'true'

        enable_inference = _get_value_from_config_protected_config(
            self.ENABLE_INFERENCE, configuration_settings, configuration_protected_settings)
        enable_inference = str(enable_inference).lower() == 'true'

        if enable_inference:
            logger.warning("The installed AzureML extension for AML inference is experimental and not covered by customer support. Please use with discretion.")
            self.__validate_scoring_fe_settings(configuration_settings, configuration_protected_settings)
        elif not (enable_training or enable_inference):
            raise InvalidArgumentValueError(
                "Please create Microsoft.AzureML.Kubernetes extension instance either "
                "for Machine Learning training or inference by specifying "
                f"'--configuration-settings {self.ENABLE_TRAINING}=true' or '--configuration-settings {self.ENABLE_INFERENCE}=true'")

        configuration_settings[self.ENABLE_TRAINING] = configuration_settings.get(self.ENABLE_TRAINING, enable_training)
        configuration_settings[self.ENABLE_INFERENCE] = configuration_settings.get(
            self.ENABLE_INFERENCE, enable_inference)
        configuration_protected_settings.pop(self.ENABLE_TRAINING, None)
        configuration_protected_settings.pop(self.ENABLE_INFERENCE, None)

    def __validate_scoring_fe_settings(self, configuration_settings, configuration_protected_settings):
        clusterPurpose = _get_value_from_config_protected_config(
            'clusterPurpose', configuration_settings, configuration_protected_settings)
        if clusterPurpose and clusterPurpose not in ["DevTest", "FastProd"]:
            raise InvalidArgumentValueError(
                "Accepted values for '--configuration-settings clusterPurpose' "
                "are 'DevTest' and 'FastProd'")

        feSslCert = _get_value_from_config_protected_config(
            'scoringFe.sslCert', configuration_settings, configuration_protected_settings)
        sslKey = _get_value_from_config_protected_config(
            'scoringFe.sslKey', configuration_settings, configuration_protected_settings)
        allowInsecureConnections = _get_value_from_config_protected_config(
            'allowInsecureConnections', configuration_settings, configuration_protected_settings)
        allowInsecureConnections = str(allowInsecureConnections).lower() == 'true'
        if (not feSslCert or not sslKey) and not allowInsecureConnections:
            raise InvalidArgumentValueError(
                "Provide ssl certificate and key. "
                "Otherwise explicitly allow insecure connection by specifying "
                "'--configuration-settings allowInsecureConnections=true'")

        feIsInternalLoadBalancer = _get_value_from_config_protected_config(
            'scoringFe.serviceType.internalLoadBalancer', configuration_settings, configuration_protected_settings)
        feIsInternalLoadBalancer = str(feIsInternalLoadBalancer).lower() == 'true'
        if feIsInternalLoadBalancer:
            logger.warning(
                'Internal load balancer only supported on AKS and AKS Engine Clusters.')

    def __create_required_resource(
            self, cmd, configuration_settings, configuration_protected_settings, subscription_id, resource_group_name,
            cluster_name, cluster_location):
        if str(configuration_settings.get(self.LOG_ANALYTICS_WS_ENABLED, False)).lower() == 'true'\
                and not configuration_settings.get(self.AZURE_LOG_ANALYTICS_CONNECTION_STRING)\
                and not configuration_protected_settings.get(self.AZURE_LOG_ANALYTICS_CONNECTION_STRING):
            logger.info('==== BEGIN LOG ANALYTICS WORKSPACE CREATION ====')
            ws_costumer_id, shared_key = _get_log_analytics_ws_connection_string(
                cmd, subscription_id, resource_group_name, cluster_name, cluster_location)
            logger.info('==== END LOG ANALYTICS WORKSPACE CREATION ====')
            configuration_settings[self.AZURE_LOG_ANALYTICS_ENABLED_KEY] = True
            configuration_settings[self.AZURE_LOG_ANALYTICS_CUSTOMER_ID_KEY] = ws_costumer_id
            configuration_protected_settings[self.AZURE_LOG_ANALYTICS_CONNECTION_STRING] = shared_key

        if not configuration_settings.get(
                self.RELAY_SERVER_CONNECTION_STRING) and not configuration_protected_settings.get(
                self.RELAY_SERVER_CONNECTION_STRING):
            logger.info('==== BEGIN RELAY CREATION ====')
            relay_connection_string, hc_resource_id, hc_name = _get_relay_connection_str(
                cmd, subscription_id, resource_group_name, cluster_name, cluster_location, self.RELAY_HC_AUTH_NAME)
            logger.info('==== END RELAY CREATION ====')
            configuration_protected_settings[self.RELAY_SERVER_CONNECTION_STRING] = relay_connection_string
            configuration_settings[self.HC_RESOURCE_ID_KEY] = hc_resource_id
            configuration_settings[self.RELAY_HC_NAME_KEY] = hc_name

        if not configuration_settings.get(
                self.SERVICE_BUS_CONNECTION_STRING) and not configuration_protected_settings.get(
                self.SERVICE_BUS_CONNECTION_STRING):
            logger.info('==== BEGIN SERVICE BUS CREATION ====')
            topic_sub_mapping = {
                self.SERVICE_BUS_COMPUTE_STATE_TOPIC: self.SERVICE_BUS_COMPUTE_STATE_SUB,
                self.SERVICE_BUS_JOB_STATE_TOPIC: self.SERVICE_BUS_JOB_STATE_SUB
            }
            service_bus_connection_string, service_buse_resource_id = _get_service_bus_connection_string(
                cmd, subscription_id, resource_group_name, cluster_name, cluster_location, topic_sub_mapping)
            logger.info('==== END SERVICE BUS CREATION ====')
            configuration_protected_settings[self.SERVICE_BUS_CONNECTION_STRING] = service_bus_connection_string
            configuration_settings[self.SERVICE_BUS_RESOURCE_ID_KEY] = service_buse_resource_id
            configuration_settings[f'{self.SERVICE_BUS_TOPIC_SUB_MAPPING_KEY}.{self.SERVICE_BUS_COMPUTE_STATE_TOPIC}'] = self.SERVICE_BUS_COMPUTE_STATE_SUB
            configuration_settings[f'{self.SERVICE_BUS_TOPIC_SUB_MAPPING_KEY}.{self.SERVICE_BUS_JOB_STATE_TOPIC}'] = self.SERVICE_BUS_JOB_STATE_SUB


def _get_valid_name(input_name: str, suffix_len: int, max_len: int) -> str:
    normalized_str = ''.join(filter(str.isalnum, input_name))
    assert len(normalized_str) > 0, "normalized name empty"

    if len(normalized_str) <= max_len:
        return normalized_str

    if suffix_len > max_len:
        logger.warning(
            "suffix length is bigger than max length. Set suffix length to max length.")
        suffix_len = max_len

    md5_suffix = md5(input_name.encode("utf8")).hexdigest()[:suffix_len]
    new_name = normalized_str[:max_len - suffix_len] + md5_suffix
    return new_name


def _lock_resource(cmd, lock_scope, lock_level='CanNotDelete'):
    lock_client: azure.mgmt.resource.locks.ManagementLockClient = get_mgmt_service_client(
        cmd.cli_ctx, azure.mgmt.resource.locks.ManagementLockClient)
    # put lock on relay resource
    lock_object = ManagementLockObject(level=lock_level, notes='locked by amlarc.')
    try:
        lock_client.management_locks.create_or_update_by_scope(
            scope=lock_scope, lock_name='amlarc-resource-lock', parameters=lock_object)
    except:
        # try to lock the resource if user has the owner privilege
        pass


def _get_relay_connection_str(
        cmd, subscription_id, resource_group_name, cluster_name, cluster_location, auth_rule_name) -> Tuple[
        str, str, str]:
    relay_client: azure.mgmt.relay.RelayManagementClient = get_mgmt_service_client(
        cmd.cli_ctx, azure.mgmt.relay.RelayManagementClient)

    cluster_id = '{}-{}-{}-relay'.format(cluster_name, subscription_id, resource_group_name)
    # create namespace
    relay_namespace_name = _get_valid_name(
        cluster_id, suffix_len=6, max_len=50)
    relay_namespace_params = azure.mgmt.relay.models.RelayNamespace(
        location=cluster_location, tags=resource_tag)

    async_poller = relay_client.namespaces.create_or_update(
        resource_group_name, relay_namespace_name, relay_namespace_params)
    while True:
        async_poller.result(15)
        if async_poller.done():
            break

    # create hybrid connection
    hybrid_connection_name = cluster_name
    hybrid_connection_object = relay_client.hybrid_connections.create_or_update(
        resource_group_name, relay_namespace_name, hybrid_connection_name, requires_client_authorization=True)

    # relay_namespace_ojbect = relay_client.namespaces.get(resource_group_name, relay_namespace_name)
    # relay_namespace_resource_id = relay_namespace_ojbect.id
    # _lock_resource(cmd, lock_scope=relay_namespace_resource_id)

    # create authorization rule
    auth_rule_rights = [azure.mgmt.relay.models.AccessRights.manage,
                        azure.mgmt.relay.models.AccessRights.send, azure.mgmt.relay.models.AccessRights.listen]
    relay_client.hybrid_connections.create_or_update_authorization_rule(
        resource_group_name, relay_namespace_name, hybrid_connection_name, auth_rule_name, rights=auth_rule_rights)

    # get connection string
    key: azure.mgmt.relay.models.AccessKeys = relay_client.hybrid_connections.list_keys(
        resource_group_name, relay_namespace_name, hybrid_connection_name, auth_rule_name)
    return f'{key.primary_connection_string}', hybrid_connection_object.id, hybrid_connection_name


def _get_service_bus_connection_string(cmd, subscription_id, resource_group_name, cluster_name, cluster_location,
                                       topic_sub_mapping: Dict[str, str]) -> Tuple[str, str]:
    service_bus_client: azure.mgmt.servicebus.ServiceBusManagementClient = get_mgmt_service_client(
        cmd.cli_ctx, azure.mgmt.servicebus.ServiceBusManagementClient)
    cluster_id = '{}-{}-{}-service-bus'.format(cluster_name,
                                               subscription_id, resource_group_name)
    service_bus_namespace_name = _get_valid_name(
        cluster_id, suffix_len=6, max_len=50)

    # create namespace
    service_bus_sku = azure.mgmt.servicebus.models.SBSku(
        name=azure.mgmt.servicebus.models.SkuName.standard.name)
    service_bus_namespace = azure.mgmt.servicebus.models.SBNamespace(
        location=cluster_location,
        sku=service_bus_sku,
        tags=resource_tag)
    async_poller = service_bus_client.namespaces.create_or_update(
        resource_group_name, service_bus_namespace_name, service_bus_namespace)
    while True:
        async_poller.result(15)
        if async_poller.done():
            break

    for topic_name, service_bus_subscription_name in topic_sub_mapping.items():
        # create topic
        topic = azure.mgmt.servicebus.models.SBTopic(max_size_in_megabytes=5120, default_message_time_to_live='P60D')
        service_bus_client.topics.create_or_update(
            resource_group_name, service_bus_namespace_name, topic_name, topic)

        # create subscription
        sub = azure.mgmt.servicebus.models.SBSubscription(
            max_delivery_count=1, default_message_time_to_live='P14D', lock_duration='PT30S')
        service_bus_client.subscriptions.create_or_update(
            resource_group_name, service_bus_namespace_name, topic_name, service_bus_subscription_name, sub)

    service_bus_object = service_bus_client.namespaces.get(resource_group_name, service_bus_namespace_name)
    service_bus_resource_id = service_bus_object.id
    # _lock_resource(cmd, service_bus_resource_id)

    # get connection string
    auth_rules = service_bus_client.namespaces.list_authorization_rules(
        resource_group_name, service_bus_namespace_name)
    for rule in auth_rules:
        key: azure.mgmt.servicebus.models.AccessKeys = service_bus_client.namespaces.list_keys(
            resource_group_name, service_bus_namespace_name, rule.name)
        return key.primary_connection_string, service_bus_resource_id


def _get_log_analytics_ws_connection_string(
        cmd, subscription_id, resource_group_name, cluster_name, cluster_location) -> Tuple[
        str, str]:
    log_analytics_ws_client: azure.mgmt.loganalytics.LogAnalyticsManagementClient = get_mgmt_service_client(
        cmd.cli_ctx, azure.mgmt.loganalytics.LogAnalyticsManagementClient)

    # create workspace
    cluster_id = '{}-{}-{}'.format(cluster_name, subscription_id, resource_group_name)
    log_analytics_ws_name = _get_valid_name(cluster_id, suffix_len=6, max_len=63)
    log_analytics_ws = azure.mgmt.loganalytics.models.Workspace(location=cluster_location, tags=resource_tag)
    async_poller = log_analytics_ws_client.workspaces.begin_create_or_update(
        resource_group_name, log_analytics_ws_name, log_analytics_ws)
    customer_id = ''
    # log_analytics_ws_resource_id = ''
    while True:
        log_analytics_ws_object = async_poller.result(15)
        if async_poller.done():
            customer_id = log_analytics_ws_object.customer_id
            # log_analytics_ws_resource_id = log_analytics_ws_object.id
            break

    # _lock_resource(cmd, log_analytics_ws_resource_id)

    # get workspace shared keys
    shared_key = log_analytics_ws_client.shared_keys.get_shared_keys(
        resource_group_name, log_analytics_ws_name).primary_shared_key
    return customer_id, shared_key


def _dereference(ref_mapping_dict: Dict[str, List], output_dict: Dict[str, Any]):
    output_dict = copy.deepcopy(output_dict)
    for ref_key, ref_list in ref_mapping_dict.items():
        if ref_key not in output_dict:
            continue
        ref_value = output_dict[ref_key]
        for key in ref_list:
            # if user has set the value, skip.
            output_dict[key] = output_dict.get(key, ref_value)
    return output_dict


def _get_value_from_config_protected_config(key, config, protected_config):
    if key in config:
        return config[key]
    return protected_config.get(key)


def _get_cluster_rp_api_version(cluster_type) -> Tuple[str, str]:
    rp = ''
    parent_api_version = ''
    if cluster_type.lower() == 'connectedclusters':
        rp = 'Microsoft.Kubernetes'
        parent_api_version = '2020-01-01-preview'
    elif cluster_type.lower() == 'appliances':
        rp = 'Microsoft.ResourceConnector'
        parent_api_version = '2020-09-15-privatepreview'
    elif cluster_type.lower() == '':
        rp = 'Microsoft.ContainerService'
        parent_api_version = '2017-07-01'
    else:
        raise InvalidArgumentValueError("Error! Cluster type '{}' is not supported".format(cluster_type))
    return rp, parent_api_version
