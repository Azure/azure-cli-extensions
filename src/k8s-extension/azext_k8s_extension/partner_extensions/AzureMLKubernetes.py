# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument
# pylint: disable=line-too-long
# pylint: disable=too-many-locals

import copy
from hashlib import md5
from typing import Any, Dict, List, Tuple

from ..aaz.latest.relay.hyco import Create as HycoCreate, Show as HycoShow
from ..aaz.latest.relay.hyco.authorization_rule import Create as HycoAuthoCreate
from ..aaz.latest.relay.hyco.authorization_rule.keys import List as HycoAuthoKeysList
from ..aaz.latest.relay.namespace import Create as NamespaceCreate
from ..utils import get_cluster_rp_api_version

import azure.mgmt.resource.locks
import azure.mgmt.servicebus
import azure.mgmt.servicebus.models
import azure.mgmt.storage
import azure.mgmt.storage.models
import azure.mgmt.loganalytics
import azure.mgmt.loganalytics.models
from azure.cli.core.azclierror import AzureResponseError, InvalidArgumentValueError, MutuallyExclusiveArgumentError, ResourceNotFoundError
from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_subscription_id
from azure.mgmt.resource.locks.models import ManagementLockObject
from knack.log import get_logger
from msrestazure.azure_exceptions import CloudError
from msrest.exceptions import HttpOperationError
import azure.core.exceptions

from .._client_factory import cf_resources
from .DefaultExtension import DefaultExtension, user_confirmation_factory
from ..vendored_sdks.models import (
    Extension,
    Scope,
    ScopeCluster,
    PatchExtension
)

logger = get_logger(__name__)

resource_tag = {'created_by': 'Azure Arc-enabled ML'}


# pylint: disable=too-many-instance-attributes
class AzureMLKubernetes(DefaultExtension):
    def __init__(self):
        # tsg link
        self.TSG_LINK = 'https://aka.ms/arcmltsg'

        # constants for configuration settings.
        self.DEFAULT_RELEASE_NAMESPACE = 'azureml'
        self.RELAY_CONNECTION_STRING_KEY = 'relayserver.relayConnectionString'
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
        self.NGINX_INGRESS_ENABLED_KEY = 'nginxIngress.enabled'

        # component flag
        self.ENABLE_TRAINING = 'enableTraining'
        self.ENABLE_INFERENCE = 'enableInference'

        # constants for determine whether create underlying azure resource
        self.RELAY_SERVER_CONNECTION_STRING = 'relayServerConnectionString'  # create relay connection string if None
        self.SERVICE_BUS_CONNECTION_STRING = 'serviceBusConnectionString'  # create service bus if None
        self.LOG_ANALYTICS_WS_ENABLED = 'logAnalyticsWS'  # create log analytics workspace if true
        # default to false when creating the extension
        self.SERVICE_BUS_ENABLED = 'servicebus.enabled'
        # default to false if cluster is AKS when creating the extension
        self.RELAY_SERVER_ENABLED = 'relayserver.enabled'

        # constants for azure resources creation
        self.RELAY_HC_AUTH_NAME = 'azureml_rw'
        self.SERVICE_BUS_COMPUTE_STATE_TOPIC = 'computestate-updatedby-computeprovider'
        self.SERVICE_BUS_COMPUTE_STATE_SUB = 'compute-scheduler-computestate'
        self.SERVICE_BUS_JOB_STATE_TOPIC = 'jobstate-updatedby-computeprovider'
        self.SERVICE_BUS_JOB_STATE_SUB = 'compute-scheduler-jobstate'

        # constants for enabling SSL in inference
        self.sslKeyPemFile = 'sslKeyPemFile'
        self.sslCertPemFile = 'sslCertPemFile'
        self.allowInsecureConnections = 'allowInsecureConnections'
        self.SSL_SECRET = 'sslSecret'
        self.SSL_Cname = 'sslCname'

        self.inferenceRouterServiceType = 'inferenceRouterServiceType'
        self.internalLoadBalancerProvider = 'internalLoadBalancerProvider'
        self.inferenceRouterHA = 'inferenceRouterHA'
        self.clusterPurpose = 'clusterPurpose'

        # constants for existing AKS to AMLARC migration
        self.IS_AKS_MIGRATION = 'isAKSMigration'

        # constants for others in Spec
        self.installNvidiaDevicePlugin = 'installNvidiaDevicePlugin'

        # reference mapping
        self.reference_mapping = {
            self.RELAY_SERVER_CONNECTION_STRING: [self.RELAY_CONNECTION_STRING_KEY],
            self.SERVICE_BUS_CONNECTION_STRING: [self.SERVICE_BUS_CONNECTION_STRING_KEY],
            'cluster_name': ['clusterId', 'prometheus.prometheusSpec.externalLabels.cluster_name'],
        }

        self.OPEN_SHIFT = 'openshift'

    def Create(self, cmd, client, resource_group_name, cluster_name, name, cluster_type, cluster_rp,
               extension_type, scope, auto_upgrade_minor_version, release_train, version, target_namespace,
               release_namespace, configuration_settings, configuration_protected_settings,
               configuration_settings_file, configuration_protected_settings_file, plan_name,
               plan_publisher, plan_product):

        logger.warning("Troubleshooting: {}".format(self.TSG_LINK))

        if scope == 'namespace':
            raise InvalidArgumentValueError("Invalid scope '{}'.  This extension can't be installed "
                                            "only at 'cluster' scope. "
                                            "Check {} for more information.".format(scope, self.TSG_LINK))
        # set release name explicitly to azureml
        release_namespace = self.DEFAULT_RELEASE_NAMESPACE
        scope_cluster = ScopeCluster(release_namespace=release_namespace)
        ext_scope = Scope(cluster=scope_cluster, namespace=None)

        # validate the config
        self.__validate_config(configuration_settings, configuration_protected_settings, release_namespace)

        # get the arc's location
        subscription_id = get_subscription_id(cmd.cli_ctx)
        cluster_rp, parent_api_version = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_rp)
        cluster_resource_id = '/subscriptions/{0}/resourceGroups/{1}/providers/{2}' \
            '/{3}/{4}'.format(subscription_id, resource_group_name, cluster_rp, cluster_type, cluster_name)
        cluster_location = ''
        resources = cf_resources(cmd.cli_ctx, subscription_id)
        try:
            resource = resources.get_by_id(
                cluster_resource_id, parent_api_version)
            cluster_location = resource.location.lower()
            try:
                isSmallScale = False
                if cluster_type.lower() == 'connectedclusters':
                    if resource.properties['totalNodeCount'] < 3:
                        isSmallScale = True
                if cluster_type.lower() == 'managedclusters':
                    nodeCount = 0
                    for agent in resource.properties['agentPoolProfiles']:
                        nodeCount += agent['count']
                    if nodeCount < 3:
                        isSmallScale = True

                if isSmallScale:
                    clusterPurpose = _get_value_from_config_protected_config(
                        self.clusterPurpose, configuration_settings, configuration_protected_settings)
                    if clusterPurpose is None:
                        configuration_settings[self.clusterPurpose] = 'DevTest'

                    inferenceRouterHA = _get_value_from_config_protected_config(
                        self.inferenceRouterHA, configuration_settings, configuration_protected_settings)
                    if inferenceRouterHA is None:
                        configuration_settings[self.inferenceRouterHA] = 'false'

                if resource.properties.get('distribution', '').lower() == self.OPEN_SHIFT:
                    configuration_settings[self.OPEN_SHIFT] = 'true'
            except:
                pass
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
        # do not enable service bus by default
        configuration_settings[self.SERVICE_BUS_ENABLED] = configuration_settings.get(self.SERVICE_BUS_ENABLED, 'false')

        # do not enable relay for managed cluster(AKS) by default, do not enable nginx for ARC by default
        if cluster_type == "managedClusters":
            configuration_settings[self.RELAY_SERVER_ENABLED] = configuration_settings.get(self.RELAY_SERVER_ENABLED,
                                                                                           'false')
            configuration_settings[self.NGINX_INGRESS_ENABLED_KEY] = configuration_settings.get(
                self.NGINX_INGRESS_ENABLED_KEY, 'true')
        else:
            configuration_settings[self.RELAY_SERVER_ENABLED] = configuration_settings.get(self.RELAY_SERVER_ENABLED,
                                                                                           'true')
            configuration_settings[self.NGINX_INGRESS_ENABLED_KEY] = configuration_settings.get(
                self.NGINX_INGRESS_ENABLED_KEY, 'false')

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
        extension = Extension(
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
        return extension, name, create_identity

    def Delete(self, cmd, client, resource_group_name, cluster_name, name, cluster_type, cluster_rp, yes):
        logger.warning("Troubleshooting: {}".format(self.TSG_LINK))
        user_confirmation_factory(cmd, yes)

    def Update(self, cmd, resource_group_name, cluster_name, auto_upgrade_minor_version, release_train, version, configuration_settings,
               configuration_protected_settings, original_extension, yes=False):

        logger.warning("Troubleshooting: {}".format(self.TSG_LINK))

        input_configuration_settings = copy.deepcopy(configuration_settings)
        input_configuration_protected_settings = copy.deepcopy(configuration_protected_settings)
        # configuration_settings and configuration_protected_settings can be none, so need to set them to empty dict
        if configuration_settings is None:
            configuration_settings = {}
        if configuration_protected_settings is None:
            configuration_protected_settings = {}
        self.__normalize_config(configuration_settings, configuration_protected_settings)

        # Prompt message to ask customer to confirm again
        if len(configuration_settings) > 0:
            impactScenario = ""
            messageBody = ""
            disableTraining = False
            disableInference = False
            disableNvidiaDevicePlugin = False
            hasAllowInsecureConnections = False
            hasInferenceRouterServiceType = False
            hasInternalLoadBalancerProvider = False
            hasSslCname = False
            hasNodeSelector = False
            enableLogAnalyticsWS = False

            enableTraining = _get_value_from_config_protected_config(self.ENABLE_TRAINING, configuration_settings, configuration_protected_settings)
            if enableTraining is not None:
                disableTraining = str(enableTraining).lower() == 'false'
                if disableTraining:
                    messageBody = messageBody + "enableTraining from True to False,\n"

            enableInference = _get_value_from_config_protected_config(self.ENABLE_INFERENCE, configuration_settings, configuration_protected_settings)
            if enableInference is not None:
                disableInference = str(enableInference).lower() == 'false'
                if disableInference:
                    messageBody = messageBody + "enableInference from True to False,\n"

            installNvidiaDevicePlugin = _get_value_from_config_protected_config(self.installNvidiaDevicePlugin, configuration_settings, configuration_protected_settings)
            if installNvidiaDevicePlugin is not None:
                disableNvidiaDevicePlugin = str(installNvidiaDevicePlugin).lower() == 'false'
                if disableNvidiaDevicePlugin:
                    messageBody = messageBody + "installNvidiaDevicePlugin from True to False if Nvidia GPU is used,\n"

            allowInsecureConnections = _get_value_from_config_protected_config(self.allowInsecureConnections, configuration_settings, configuration_protected_settings)
            if allowInsecureConnections is not None:
                hasAllowInsecureConnections = True
                messageBody = messageBody + "allowInsecureConnections\n"

            inferenceRouterServiceType = _get_value_from_config_protected_config(self.inferenceRouterServiceType, configuration_settings, configuration_protected_settings)
            if inferenceRouterServiceType is not None:
                hasInferenceRouterServiceType = True
                messageBody = messageBody + "inferenceRouterServiceType\n"

            internalLoadBalancerProvider = _get_value_from_config_protected_config(self.internalLoadBalancerProvider, configuration_settings, configuration_protected_settings)
            if internalLoadBalancerProvider is not None:
                hasInternalLoadBalancerProvider = True
                messageBody = messageBody + "internalLoadBalancerProvider\n"

            sslCname = _get_value_from_config_protected_config(self.SSL_Cname, configuration_settings, configuration_protected_settings)
            if sslCname is not None:
                hasSslCname = True
                messageBody = messageBody + "sslCname\n"

            hasNodeSelector = _check_nodeselector_existed(configuration_settings, configuration_protected_settings)
            if hasNodeSelector:
                messageBody = messageBody + "nodeSelector. Update operation can't remove an existed node selector, but can update or add new ones.\n"

            logAnalyticsWS = _get_value_from_config_protected_config(self.LOG_ANALYTICS_WS_ENABLED, configuration_settings, configuration_protected_settings)
            if logAnalyticsWS is not None:
                enableLogAnalyticsWS = str(logAnalyticsWS).lower() == 'true'
                if enableLogAnalyticsWS:
                    messageBody = messageBody + "To update logAnalyticsWS from False to True, please provide all original configurationProtectedSettings. Otherwise, those settings would be considered obsolete and deleted.\n"

            if disableTraining or disableNvidiaDevicePlugin or hasNodeSelector:
                impactScenario = "jobs"

            if disableInference or disableNvidiaDevicePlugin or hasAllowInsecureConnections or hasInferenceRouterServiceType or hasInternalLoadBalancerProvider or hasNodeSelector or hasSslCname:
                if impactScenario == "":
                    impactScenario = "online endpoints and deployments"
                else:
                    impactScenario = impactScenario + ", online endpoints and deployments"

            if impactScenario != "":
                message = ("\nThe following configuration update will IMPACT your active Machine Learning " + impactScenario +
                           ". It will be the safe update if the cluster doesn't have active Machine Learning " + impactScenario + ".\n\n" + messageBody + "\nProceed?")
                user_confirmation_factory(cmd, yes, message=message)
            else:
                if enableLogAnalyticsWS:
                    message = "\n" + messageBody + "\nProceed?"
                    user_confirmation_factory(cmd, yes, message=message)

        if len(configuration_protected_settings) > 0:
            subscription_id = get_subscription_id(cmd.cli_ctx)

            if self.AZURE_LOG_ANALYTICS_CONNECTION_STRING not in configuration_protected_settings:
                try:
                    _, shared_key = _get_log_analytics_ws_connection_string(
                        cmd, subscription_id, resource_group_name, cluster_name, '', True)
                    configuration_protected_settings[self.AZURE_LOG_ANALYTICS_CONNECTION_STRING] = shared_key
                    logger.info("Get log analytics connection string succeeded.")
                except azure.core.exceptions.HttpResponseError:
                    logger.info("Failed to get log analytics connection string.")

            original_extension_config_settings = original_extension.configuration_settings
            if original_extension_config_settings is None:
                original_extension_config_settings = {}
            if original_extension_config_settings.get(self.RELAY_SERVER_ENABLED).lower() != 'false' \
                    and self.RELAY_SERVER_CONNECTION_STRING not in configuration_protected_settings:
                try:
                    relay_connection_string, _, _ = _get_relay_connection_str(
                        cmd, subscription_id, resource_group_name, cluster_name, '', self.RELAY_HC_AUTH_NAME, True)
                    configuration_protected_settings[self.RELAY_SERVER_CONNECTION_STRING] = relay_connection_string
                    logger.info("Get relay connection string succeeded.")
                except azure.core.exceptions.HttpResponseError as ex:
                    if ex.response.status_code == 404:
                        raise ResourceNotFoundError("Relay server not found. "
                                                    "Check {} for more information.".format(self.TSG_LINK)) from ex
                    raise AzureResponseError("Failed to get relay connection string."
                                             "Check {} for more information.".format(self.TSG_LINK)) from ex

            if original_extension_config_settings.get(self.SERVICE_BUS_ENABLED).lower() != 'false' \
                    and self.SERVICE_BUS_CONNECTION_STRING not in configuration_protected_settings:
                try:
                    service_bus_connection_string, _ = _get_service_bus_connection_string(
                        cmd, subscription_id, resource_group_name, cluster_name, '', {}, True)
                    configuration_protected_settings[self.SERVICE_BUS_CONNECTION_STRING] = service_bus_connection_string
                    logger.info("Get service bus connection string succeeded.")
                except azure.core.exceptions.HttpResponseError as ex:
                    if ex.response.status_code == 404:
                        raise ResourceNotFoundError("Service bus not found."
                                                    "Check {} for more information.".format(self.TSG_LINK)) from ex
                    raise AzureResponseError("Failed to get service bus connection string."
                                             "Check {} for more information.".format(self.TSG_LINK)) from ex

            configuration_protected_settings = _dereference(self.reference_mapping, configuration_protected_settings)

        fe_ssl_secret = _get_value_from_config_protected_config(
            self.SSL_SECRET, configuration_settings, configuration_protected_settings)
        fe_ssl_cert_file = configuration_protected_settings.get(self.sslCertPemFile)
        fe_ssl_key_file = configuration_protected_settings.get(self.sslKeyPemFile)
        # always take ssl key/cert first, then secret if key/cert file is not provided
        if fe_ssl_cert_file and fe_ssl_key_file:
            logger.info(f"Both {self.sslKeyPemFile} and {self.sslCertPemFile} are set, updating ssl key.")
            self.__set_inference_ssl_from_file(configuration_protected_settings, fe_ssl_cert_file, fe_ssl_key_file)
        elif fe_ssl_secret:
            logger.info(f"{self.SSL_SECRET} is set, updating ssl secret.")
            self.__set_inference_ssl_from_secret(configuration_settings, fe_ssl_secret)

        # if no entries are existed in configuration_protected_settings, configuration_settings, return whatever passed
        #  in the Update function(empty dict or None).
        if len(configuration_settings) == 0:
            configuration_settings = input_configuration_settings
        if len(configuration_protected_settings) == 0:
            configuration_protected_settings = input_configuration_protected_settings

        return PatchExtension(auto_upgrade_minor_version=auto_upgrade_minor_version,
                              release_train=release_train,
                              version=version,
                              configuration_settings=configuration_settings,
                              configuration_protected_settings=configuration_protected_settings)

    def __normalize_config(self, configuration_settings, configuration_protected_settings):
        inferenceRouterServiceType = _get_value_from_config_protected_config(
            self.inferenceRouterServiceType, configuration_settings, configuration_protected_settings)
        if inferenceRouterServiceType:
            if not _is_valid_service_type(inferenceRouterServiceType):
                raise InvalidArgumentValueError(
                    "inferenceRouterServiceType only supports NodePort or LoadBalancer or ClusterIP."
                    "Check {} for more information.".format(self.TSG_LINK))

            feIsNodePort = str(inferenceRouterServiceType).lower() == 'nodeport'
            configuration_settings['scoringFe.serviceType.nodePort'] = feIsNodePort

        internalLoadBalancerProvider = _get_value_from_config_protected_config(
            self.internalLoadBalancerProvider, configuration_settings, configuration_protected_settings)
        if internalLoadBalancerProvider:
            feIsInternalLoadBalancer = str(internalLoadBalancerProvider).lower() == 'azure'
            configuration_settings['scoringFe.serviceType.internalLoadBalancer'] = feIsInternalLoadBalancer
            logger.warning(
                'Internal load balancer only supported on AKS and AKS Engine Clusters.')

    def __validate_config(self, configuration_settings, configuration_protected_settings, release_namespace):
        # perform basic validation of the input config
        config_keys = configuration_settings.keys()
        config_protected_keys = configuration_protected_settings.keys()
        dup_keys = set(config_keys) & set(config_protected_keys)
        if dup_keys:
            for key in dup_keys:
                logger.warning(
                    'Duplicate keys found in both configuration settings and configuration protected setttings: %s', key)
            raise InvalidArgumentValueError("Duplicate keys found."
                                            "Check {} for more information.".format(self.TSG_LINK))

        enable_training = _get_value_from_config_protected_config(
            self.ENABLE_TRAINING, configuration_settings, configuration_protected_settings)
        enable_training = str(enable_training).lower() == 'true'

        enable_inference = _get_value_from_config_protected_config(
            self.ENABLE_INFERENCE, configuration_settings, configuration_protected_settings)
        enable_inference = str(enable_inference).lower() == 'true'

        if enable_inference:
            self.__validate_scoring_fe_settings(configuration_settings, configuration_protected_settings, release_namespace)
            self.__set_up_inference_ssl(configuration_settings, configuration_protected_settings)
        elif not (enable_training or enable_inference):
            raise InvalidArgumentValueError(
                "To create Microsoft.AzureML.Kubernetes extension, either "
                "enable Machine Learning training or inference by specifying "
                f"'--configuration-settings {self.ENABLE_TRAINING}=true' or '--configuration-settings {self.ENABLE_INFERENCE}=true'."
                "Please check {} for more information.".format(self.TSG_LINK))

        configuration_settings[self.ENABLE_TRAINING] = configuration_settings.get(self.ENABLE_TRAINING, enable_training)
        configuration_settings[self.ENABLE_INFERENCE] = configuration_settings.get(
            self.ENABLE_INFERENCE, enable_inference)
        configuration_protected_settings.pop(self.ENABLE_TRAINING, None)
        configuration_protected_settings.pop(self.ENABLE_INFERENCE, None)

    def __validate_scoring_fe_settings(self, configuration_settings, configuration_protected_settings, release_namespace):
        isAKSMigration = _get_value_from_config_protected_config(
            self.IS_AKS_MIGRATION, configuration_settings, configuration_protected_settings)
        isAKSMigration = str(isAKSMigration).lower() == 'true'
        if isAKSMigration:
            configuration_settings['scoringFe.namespace'] = "default"
            configuration_settings[self.IS_AKS_MIGRATION] = "true"
        sslSecret = _get_value_from_config_protected_config(
            self.SSL_SECRET, configuration_settings, configuration_protected_settings)
        feSslCertFile = configuration_protected_settings.get(self.sslCertPemFile)
        feSslKeyFile = configuration_protected_settings.get(self.sslKeyPemFile)
        allowInsecureConnections = _get_value_from_config_protected_config(
            self.allowInsecureConnections, configuration_settings, configuration_protected_settings)
        allowInsecureConnections = str(allowInsecureConnections).lower() == 'true'
        sslEnabled = (feSslCertFile and feSslKeyFile) or sslSecret
        if not sslEnabled and not allowInsecureConnections:
            raise InvalidArgumentValueError(
                "To enable HTTPs endpoint, "
                "either provide sslCertPemFile and sslKeyPemFile to --configuration-protected-settings, "
                f"or provide sslSecret(kubernetes secret name) in --configuration-settings containing both ssl cert and ssl key under {release_namespace} namespace. "
                "Otherwise, to enable HTTP endpoint, explicitly set allowInsecureConnections=true.")

        if sslEnabled:
            sslCname = _get_value_from_config_protected_config(
                self.SSL_Cname, configuration_settings, configuration_protected_settings)
            if not sslCname:
                raise InvalidArgumentValueError(
                    "To enable HTTPs endpoint, "
                    "please specify sslCname parameter in --configuration-settings. Check {} for more information.".format(self.TSG_LINK))

        inferenceRouterServiceType = _get_value_from_config_protected_config(
            self.inferenceRouterServiceType, configuration_settings, configuration_protected_settings)
        if not _is_valid_service_type(inferenceRouterServiceType):
            raise InvalidArgumentValueError(
                "To use inference, "
                "please specify inferenceRouterServiceType=ClusterIP or inferenceRouterServiceType=NodePort or inferenceRouterServiceType=LoadBalancer in --configuration-settings and also set internalLoadBalancerProvider=azure if your aks only supports internal load balancer."
                "Check {} for more information.".format(self.TSG_LINK))

        feIsNodePort = str(inferenceRouterServiceType).lower() == 'nodeport'
        internalLoadBalancerProvider = _get_value_from_config_protected_config(
            self.internalLoadBalancerProvider, configuration_settings, configuration_protected_settings)
        feIsInternalLoadBalancer = str(internalLoadBalancerProvider).lower() == 'azure'

        if feIsNodePort and feIsInternalLoadBalancer:
            raise MutuallyExclusiveArgumentError(
                "When using nodePort as inferenceRouterServiceType, no need to specify internalLoadBalancerProvider."
                "Check {} for more information.".format(self.TSG_LINK))
        if feIsNodePort:
            configuration_settings['scoringFe.serviceType.nodePort'] = feIsNodePort
        elif feIsInternalLoadBalancer:
            configuration_settings['scoringFe.serviceType.internalLoadBalancer'] = feIsInternalLoadBalancer
            logger.warning(
                'Internal load balancer only supported on AKS and AKS Engine Clusters.')

    def __set_inference_ssl_from_secret(self, configuration_settings, fe_ssl_secret):
        configuration_settings['scoringFe.sslSecret'] = fe_ssl_secret

    def __set_inference_ssl_from_file(self, configuration_protected_settings, fe_ssl_cert_file, fe_ssl_key_file):
        import base64
        with open(fe_ssl_cert_file) as f:
            cert_data = f.read()
            cert_data_bytes = cert_data.encode("ascii")
            ssl_cert = base64.b64encode(cert_data_bytes).decode()
            configuration_protected_settings['scoringFe.sslCert'] = ssl_cert
        with open(fe_ssl_key_file) as f:
            key_data = f.read()
            key_data_bytes = key_data.encode("ascii")
            ssl_key = base64.b64encode(key_data_bytes).decode()
            configuration_protected_settings['scoringFe.sslKey'] = ssl_key

    def __set_up_inference_ssl(self, configuration_settings, configuration_protected_settings):
        allowInsecureConnections = _get_value_from_config_protected_config(
            self.allowInsecureConnections, configuration_settings, configuration_protected_settings)
        allowInsecureConnections = str(allowInsecureConnections).lower() == 'true'
        if not allowInsecureConnections:
            fe_ssl_secret = _get_value_from_config_protected_config(
                self.SSL_SECRET, configuration_settings, configuration_protected_settings)
            fe_ssl_cert_file = configuration_protected_settings.get(self.sslCertPemFile)
            fe_ssl_key_file = configuration_protected_settings.get(self.sslKeyPemFile)

            # always take ssl key/cert first, then secret if key/cert file is not provided
            if fe_ssl_cert_file and fe_ssl_key_file:
                self.__set_inference_ssl_from_file(configuration_protected_settings, fe_ssl_cert_file, fe_ssl_key_file)
            else:
                self.__set_inference_ssl_from_secret(configuration_settings, fe_ssl_secret)
        else:
            logger.warning(
                'SSL is not enabled. Allowing insecure connections to the deployed services.')

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

        if str(configuration_settings.get(self.RELAY_SERVER_ENABLED)).lower() != 'false' and \
                not configuration_settings.get(self.RELAY_SERVER_CONNECTION_STRING) and \
                not configuration_protected_settings.get(self.RELAY_SERVER_CONNECTION_STRING):
            logger.info('==== BEGIN RELAY CREATION ====')
            relay_connection_string, hc_resource_id, hc_name = _get_relay_connection_str(
                cmd, subscription_id, resource_group_name, cluster_name, cluster_location, self.RELAY_HC_AUTH_NAME)
            logger.info('==== END RELAY CREATION ====')
            configuration_protected_settings[self.RELAY_SERVER_CONNECTION_STRING] = relay_connection_string
            configuration_settings[self.HC_RESOURCE_ID_KEY] = hc_resource_id
            configuration_settings[self.RELAY_HC_NAME_KEY] = hc_name

        if str(configuration_settings.get(self.SERVICE_BUS_ENABLED)).lower() != 'false' and \
                not configuration_settings.get(self.SERVICE_BUS_CONNECTION_STRING) and \
                not configuration_protected_settings.get(self.SERVICE_BUS_CONNECTION_STRING):
            logger.info('==== BEGIN SERVICE BUS CREATION ====')
            topic_sub_mapping = {
                self.SERVICE_BUS_COMPUTE_STATE_TOPIC: self.SERVICE_BUS_COMPUTE_STATE_SUB,
                self.SERVICE_BUS_JOB_STATE_TOPIC: self.SERVICE_BUS_JOB_STATE_SUB
            }
            service_bus_connection_string, service_bus_resource_id = _get_service_bus_connection_string(
                cmd, subscription_id, resource_group_name, cluster_name, cluster_location, topic_sub_mapping)
            logger.info('==== END SERVICE BUS CREATION ====')
            configuration_protected_settings[self.SERVICE_BUS_CONNECTION_STRING] = service_bus_connection_string
            configuration_settings[self.SERVICE_BUS_RESOURCE_ID_KEY] = service_bus_resource_id
            configuration_settings[f'{self.SERVICE_BUS_TOPIC_SUB_MAPPING_KEY}.{self.SERVICE_BUS_COMPUTE_STATE_TOPIC}'] = self.SERVICE_BUS_COMPUTE_STATE_SUB
            configuration_settings[f'{self.SERVICE_BUS_TOPIC_SUB_MAPPING_KEY}.{self.SERVICE_BUS_JOB_STATE_TOPIC}'] = self.SERVICE_BUS_JOB_STATE_SUB


def _get_valid_name(input_name: str, suffix_len: int, max_len: int) -> str:
    normalized_str = ''.join(filter(str.isalnum, input_name))
    assert normalized_str, "normalized name empty"

    if len(normalized_str) <= max_len:
        return normalized_str

    if suffix_len > max_len:
        logger.warning(
            "suffix length is bigger than max length. Set suffix length to max length.")
        suffix_len = max_len

    md5_suffix = md5(input_name.encode("utf8")).hexdigest()[:suffix_len]
    new_name = normalized_str[:max_len - suffix_len] + md5_suffix
    return new_name


# pylint: disable=broad-except
def _lock_resource(cmd, lock_scope, lock_level='CanNotDelete'):
    lock_client: azure.mgmt.resource.locks.ManagementLockClient = get_mgmt_service_client(
        cmd.cli_ctx, azure.mgmt.resource.locks.ManagementLockClient)
    # put lock on relay resource
    lock_object = ManagementLockObject(level=lock_level, notes='locked by amlarc.')
    try:
        lock_client.management_locks.create_or_update_by_scope(
            scope=lock_scope, lock_name='amlarc-resource-lock', parameters=lock_object)
    except Exception:
        # try to lock the resource if user has the owner privilege
        pass


def _get_relay_connection_str(
        cmd, subscription_id, resource_group_name, cluster_name, cluster_location, auth_rule_name, get_key_only=False) -> Tuple[str, str, str]:

    cluster_id = '{}-{}-{}-relay'.format(cluster_name, subscription_id, resource_group_name)
    relay_namespace_name = _get_valid_name(
        cluster_id, suffix_len=6, max_len=50)
    hybrid_connection_name = cluster_name
    hc_resource_id = ''

    # only create relay if not found
    try:
        # get connection string
        hybrid_connection_object = HycoShow(cli_ctx=cmd.cli_ctx)(command_args={"resource_group": resource_group_name,
                                                                               "namespace_name": relay_namespace_name,
                                                                               "name": hybrid_connection_name})
        hc_resource_id = hybrid_connection_object['id']
        key = HycoAuthoKeysList(cli_ctx=cmd.cli_ctx)(command_args={"resource_group": resource_group_name,
                                                                   "namespace_name": relay_namespace_name,
                                                                   "hybrid_connection_name": hybrid_connection_name,
                                                                   "name": auth_rule_name})
    except azure.core.exceptions.HttpResponseError as e:
        if e.response.status_code != 404 or get_key_only:
            raise e
        # create namespace
        async_poller = NamespaceCreate(cli_ctx=cmd.cli_ctx)(command_args={"resource_group": resource_group_name,
                                                                          "name": relay_namespace_name,
                                                                          "location": cluster_location,
                                                                          "tags": resource_tag})
        while True:
            async_poller.result(15)
            if async_poller.done():
                break

        # create hybrid connection
        hybrid_connection_object = HycoCreate(cli_ctx=cmd.cli_ctx)(command_args={"resource_group": resource_group_name,
                                                                                 "namespace_name": relay_namespace_name,
                                                                                 "name": hybrid_connection_name,
                                                                                 "requires_client_authorization": True})
        hc_resource_id = hybrid_connection_object['id']

        # create authorization rule
        auth_rule_rights = ["Manage", "Send", "Listen"]
        HycoAuthoCreate(cli_ctx=cmd.cli_ctx)(command_args={"resource_group": resource_group_name,
                                                           "namespace_name": relay_namespace_name,
                                                           "hybrid_connection_name": hybrid_connection_name,
                                                           "name": auth_rule_name,
                                                           "rights": auth_rule_rights})

        # get connection string
        key = HycoAuthoKeysList(cli_ctx=cmd.cli_ctx)(command_args={"resource_group": resource_group_name,
                                                                   "namespace_name": relay_namespace_name,
                                                                   "hybrid_connection_name": hybrid_connection_name,
                                                                   "name": auth_rule_name})
    return f'{key["primaryConnectionString"]}', hc_resource_id, hybrid_connection_name


def _get_service_bus_connection_string(cmd, subscription_id, resource_group_name, cluster_name, cluster_location,
                                       topic_sub_mapping: Dict[str, str], get_key_only=False) -> Tuple[str, str]:
    service_bus_client: azure.mgmt.servicebus.ServiceBusManagementClient = get_mgmt_service_client(
        cmd.cli_ctx, azure.mgmt.servicebus.ServiceBusManagementClient)
    cluster_id = '{}-{}-{}-service-bus'.format(cluster_name,
                                               subscription_id, resource_group_name)
    service_bus_namespace_name = _get_valid_name(
        cluster_id, suffix_len=6, max_len=50)
    try:
        service_bus_object = service_bus_client.namespaces.get(resource_group_name, service_bus_namespace_name)
        service_bus_resource_id = service_bus_object.id

        # get connection string
        auth_rules = service_bus_client.namespaces.list_authorization_rules(
            resource_group_name, service_bus_namespace_name)
        for rule in auth_rules:
            key: azure.mgmt.servicebus.models.AccessKeys = service_bus_client.namespaces.list_keys(
                resource_group_name, service_bus_namespace_name, rule.name)
            return key.primary_connection_string, service_bus_resource_id
    except azure.core.exceptions.HttpResponseError as e:
        if e.response.status_code != 404 or get_key_only:
            raise e
        # create namespace
        service_bus_sku = azure.mgmt.servicebus.models.SBSku(
            name=azure.mgmt.servicebus.models.SkuName.standard.name)
        service_bus_namespace = azure.mgmt.servicebus.models.SBNamespace(
            location=cluster_location,
            sku=service_bus_sku,
            tags=resource_tag)
        async_poller = service_bus_client.namespaces.begin_create_or_update(
            resource_group_name, service_bus_namespace_name, service_bus_namespace)
        while True:
            service_bus_object = async_poller.result(15)
            if async_poller.done():
                service_bus_resource_id = service_bus_object.id
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

        # get connection string
        auth_rules = service_bus_client.namespaces.list_authorization_rules(
            resource_group_name, service_bus_namespace_name)
        for rule in auth_rules:
            key: azure.mgmt.servicebus.models.AccessKeys = service_bus_client.namespaces.list_keys(
                resource_group_name, service_bus_namespace_name, rule.name)
            return key.primary_connection_string, service_bus_resource_id


def _get_log_analytics_ws_connection_string(
        cmd, subscription_id, resource_group_name, cluster_name, cluster_location, get_key_only=False) -> Tuple[str, str]:
    log_analytics_ws_client: azure.mgmt.loganalytics.LogAnalyticsManagementClient = get_mgmt_service_client(
        cmd.cli_ctx, azure.mgmt.loganalytics.LogAnalyticsManagementClient)

    # create workspace
    cluster_id = '{}-{}-{}'.format(cluster_name, subscription_id, resource_group_name)
    log_analytics_ws_name = _get_valid_name(cluster_id, suffix_len=6, max_len=63)
    customer_id = ''
    try:
        # get workspace shared keys
        log_analytics_ws_object = log_analytics_ws_client.workspaces.get(resource_group_name, log_analytics_ws_name)
        customer_id = log_analytics_ws_object.customer_id
        shared_key = log_analytics_ws_client.shared_keys.get_shared_keys(
            resource_group_name, log_analytics_ws_name).primary_shared_key
    except azure.core.exceptions.HttpResponseError as e:
        if e.response.status_code != 404 or get_key_only:
            raise e
        log_analytics_ws = azure.mgmt.loganalytics.models.Workspace(location=cluster_location, tags=resource_tag)
        async_poller = log_analytics_ws_client.workspaces.begin_create_or_update(
            resource_group_name, log_analytics_ws_name, log_analytics_ws)
        while True:
            log_analytics_ws_object = async_poller.result(15)
            if async_poller.done():
                customer_id = log_analytics_ws_object.customer_id
                break
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
    if config is not None and key in config:
        return config[key]
    if protected_config is not None:
        return protected_config.get(key)
    return None


def _check_nodeselector_existed(configuration_settings, configuration_protected_settings):
    config_keys = configuration_settings.keys()
    config_protected_keys = configuration_protected_settings.keys()
    all_keys = set(config_keys) | set(config_protected_keys)
    if all_keys:
        for key in all_keys:
            if "nodeSelector" in key:
                return True
    return False


def _is_valid_service_type(service_type):
    if service_type:
        return service_type.lower() == 'nodeport' or service_type.lower() == 'loadbalancer' or service_type.lower() == 'clusterip'
    else:
        return False
