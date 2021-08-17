# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import shutil
import platform
from base64 import b64encode

import yaml
from requests.adapters import HTTPAdapter
from Crypto.IO import PEM
from Crypto.PublicKey import RSA
from Crypto.Util import asn1
from psutil import process_iter, NoSuchProcess, AccessDenied, ZombieProcess, net_connections
from knack.log import get_logger
from knack.prompting import NoTTYException, prompt_y_n
from azure.cli.core.util import send_raw_request
from azure.cli.core import telemetry
from azure.cli.core.azclierror import CLIInternalError, ValidationError, FileOperationError, ClientRequestError
from azure.cli.core.azclierror import ManualInterrupt
from azext_connectedk8s._helm_core_utils import HelmCoreUtils
import azext_connectedk8s._constants as consts
import azext_connectedk8s._kube_core_utils as kube_core_utils
from .vendored_sdks.models import ConnectedCluster, ConnectedClusterIdentity

logger = get_logger(__name__)

# pylint: disable=bare-except


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = consts.DEFAULT_REQUEST_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


def get_chart_path(registry_path, kube_config, kube_context):
    # Pulling helm chart from registry
    os.environ['HELM_EXPERIMENTAL_OCI'] = '1'

    helm_core_utils = HelmCoreUtils(kube_config, kube_context)
    helm_core_utils.pull_helm_chart(registry_path)

    # Exporting helm chart after cleanup
    chart_export_path = os.path.join(os.path.expanduser('~'), '.azure', 'AzureArcCharts')
    try:
        if os.path.isdir(chart_export_path):
            shutil.rmtree(chart_export_path)
    except:
        logger.warning("Unable to cleanup the azure-arc helm charts already present on the machine." +
                       " In case of failure, please cleanup the directory '%s' and try again.",
                       chart_export_path)
    helm_core_utils.export_helm_chart(registry_path, chart_export_path)

    # Returning helm chart path
    helm_chart_path = os.path.join(chart_export_path, 'azure-arc-k8sagents')
    chart_path = os.getenv('HELMCHART') if os.getenv('HELMCHART') else helm_chart_path
    return chart_path


def get_helm_registry(cmd, config_dp_endpoint, dp_endpoint_dogfood=None, release_train_dogfood=None):
    # Setting uri
    get_chart_location_url = "{}/{}/GetLatestHelmPackagePath?api-version=2019-11-01-preview" \
                             .format(config_dp_endpoint, 'azure-arc-k8sagents')
    release_train = os.getenv('RELEASETRAIN') if os.getenv('RELEASETRAIN') else 'stable'
    if dp_endpoint_dogfood:
        get_chart_location_url = "{}/azure-arc-k8sagents/GetLatestHelmPackagePath?api-version=2019-11-01-preview" \
                                 .format(dp_endpoint_dogfood)
        if release_train_dogfood:
            release_train = release_train_dogfood
    uri_parameters = ["releaseTrain={}".format(release_train)]
    resource = cmd.cli_ctx.cloud.endpoints.active_directory_resource_id

    # Sending request
    try:
        r = send_raw_request(cmd.cli_ctx, 'post', get_chart_location_url, uri_parameters=uri_parameters,
                             resource=resource)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.Get_HelmRegistery_Path_Fault_Type,
                                summary='Error while fetching helm chart registry path')
        raise CLIInternalError("Error while fetching helm chart registry path: " + str(e))
    if r.content:
        try:
            return r.json().get('repositoryPath')
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Get_HelmRegistery_Path_Fault_Type,
                                    summary='Error while fetching helm chart registry path')
            raise CLIInternalError("Error while fetching helm chart registry path from JSON response: " + str(e))
    else:
        telemetry.set_exception(exception='No content in response',
                                fault_type=consts.Get_HelmRegistery_Path_Fault_Type,
                                summary='No content in acr path response')
        raise CLIInternalError("No content was found in helm registry path response.")


def validate_infrastructure_type(infra):
    for s in consts.Infrastructure_Enum_Values[1:]:  # First value is "auto"
        if s.lower() == infra.lower():
            return s
    return "generic"


def get_values_file():
    values_file_provided = False
    values_file = os.getenv('HELMVALUESPATH')
    if (values_file is not None) and (os.path.isfile(values_file)):
        values_file_provided = True
        logger.warning("Values files detected. Reading additional helm parameters from same.")
        # trimming required for windows os
        if (values_file.startswith("'") or values_file.startswith('"')):
            values_file = values_file[1:]
        if (values_file.endswith("'") or values_file.endswith('"')):
            values_file = values_file[:-1]

    return values_file_provided, values_file


def flatten(dd, separator='.', prefix=''):
    try:
        if isinstance(dd, dict):
            return {prefix + separator + k if prefix else k: v for kk, vv in dd.items() \
                    for k, v in flatten(vv, separator, kk).items()}
        else:
            return {prefix: dd}
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.Error_Flattening_User_Supplied_Value_Dict,
                                summary='Error while flattening the user supplied helm values dict')
        raise CLIInternalError("Error while flattening the user supplied helm values dict")


def check_features_to_update(features_to_update):
    update_cluster_connect, update_azure_rbac, update_cl = False, False, False
    for feature in features_to_update:
        if feature == "cluster-connect":
            update_cluster_connect = True
        elif feature == "azure-rbac":
            update_azure_rbac = True
        elif feature == "custom-locations":
            update_cl = True
    return update_cluster_connect, update_azure_rbac, update_cl


def user_confirmation(message, yes=False):
    if yes:
        return
    try:
        if not prompt_y_n(message):
            raise ManualInterrupt('Operation cancelled.')
    except NoTTYException:
        raise CLIInternalError('Unable to prompt for confirmation as no tty available. Use --yes.')


def is_guid(guid):
    import uuid
    try:
        uuid.UUID(guid)
        return True
    except ValueError:
        return False


def check_process(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    for proc in process_iter():
        try:
            if proc.name().startswith(processName):
                return True
        except (NoSuchProcess, AccessDenied, ZombieProcess):
            pass
    return False


def check_if_port_is_open(port):
    try:
        connections = net_connections(kind='inet')
        for tup in connections:
            if int(tup[3][1]) == int(port):
                return True
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.Port_Check_Fault_Type,
                                summary='Failed to check if port is in use.')
        if platform.system() != 'Darwin':
            logger.info("Failed to check if port is in use. " + str(e))
        return False
    return False


def send_cloud_telemetry(cmd):
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.AzureCloud': cmd.cli_ctx.cloud.name})
    cloud_name = cmd.cli_ctx.cloud.name.upper()
    # Setting cloud name to format that is understood by golang SDK.
    if cloud_name == consts.PublicCloud_OriginalName:
        cloud_name = consts.Azure_PublicCloudName
    elif cloud_name == consts.USGovCloud_OriginalName:
        cloud_name = consts.Azure_USGovCloudName
    return cloud_name


def get_config_dp_endpoint(cmd, location):
    cloud_based_domain = cmd.cli_ctx.cloud.endpoints.active_directory.split('.')[2]
    config_dp_endpoint = "https://{}.dp.kubernetesconfiguration.azure.{}".format(location, cloud_based_domain)
    return config_dp_endpoint


def get_public_key(key_pair):
    pubKey = key_pair.publickey()
    seq = asn1.DerSequence([pubKey.n, pubKey.e])
    enc = seq.encode()
    return b64encode(enc).decode('utf-8')


def get_private_key(key_pair):
    privKey_DER = key_pair.exportKey(format='DER')
    return PEM.encode(privKey_DER, "RSA PRIVATE KEY")


def generate_request_payload(location, public_key, tags, kubernetes_distro, kubernetes_infra):
    # Create connected cluster resource object
    identity = ConnectedClusterIdentity(
        type="SystemAssigned"
    )
    if tags is None:
        tags = {}
    cc = ConnectedCluster(
        location=location,
        identity=identity,
        agent_public_key_certificate=public_key,
        tags=tags,
        distribution=kubernetes_distro,
        infrastructure=kubernetes_infra
    )
    return cc


def validate_env_file_dogfood(values_file, values_file_provided):
    if not values_file_provided:
        telemetry.set_exception(exception='Helm environment file not provided',
                                fault_type=consts.Helm_Environment_File_Fault_Type,
                                summary='Helm environment file missing')
        raise ValidationError("Helm environment file is required when using Dogfood environment" +
                              " for onboarding the cluster.", recommendation="Please set the" +
                              " environment variable 'HELMVALUESPATH' to point to the file.")

    with open(values_file, 'r') as f:
        try:
            env_dict = yaml.safe_load(f)
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Helm_Environment_File_Fault_Type,
                                    summary='Problem loading the helm environment file')
            raise FileOperationError("Problem loading the helm environment file: " + str(e))
        try:
            assert env_dict.get('global').get('azureEnvironment') == 'AZUREDOGFOOD'
            assert env_dict.get('systemDefaultValues').get('azureArcAgents').get('config_dp_endpoint_override')
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Helm_Environment_File_Fault_Type,
                                    summary='Problem loading the helm environment variables')
            raise FileOperationError("The required helm environment variables for dogfood onboarding are" +
                                     " either not present in the file or incorrectly set.",
                                     recommendation="Please check the values 'global.azureEnvironment' " +
                                     "and 'systemDefaultValues.azureArcAgents.config_dp_endpoint_override'" +
                                     " in the file.")

    # Return the dp endpoint and release train
    dp_endpoint = env_dict.get('systemDefaultValues').get('azureArcAgents').get('config_dp_endpoint_override')
    release_train = env_dict.get('systemDefaultValues').get('azureArcAgents').get('releaseTrain')
    return dp_endpoint, release_train

def initial_log_warning():
    logger.warning("Ensure that you have the latest helm version installed before proceeding.")
    logger.warning("This operation might take a while...\n")


def add_telemetry_extenstion_event(connected_cluster, configuration):
    # Get kubernetes cluster info for telemetry
    kubernetes_version = kube_core_utils.get_server_version(configuration)
    if hasattr(connected_cluster, 'distribution') and (connected_cluster.distribution is not None):
        kubernetes_distro = connected_cluster.distribution
    else:
        kubernetes_distro = kube_core_utils.get_kubernetes_distro(configuration)

    if hasattr(connected_cluster, 'infrastructure') and (connected_cluster.infrastructure is not None):
        kubernetes_infra = connected_cluster.infrastructure
    else:
        kubernetes_infra = kube_core_utils.get_kubernetes_infra(configuration)

    add_telemetry_extenstion_event_raw(kubernetes_version, kubernetes_distro, kubernetes_infra)


def add_telemetry_extenstion_event_raw(kubernetes_version, kubernetes_distro, kubernetes_infra):
    kubernetes_properties = {
        'Context.Default.AzureCLI.KubernetesVersion': kubernetes_version,
        'Context.Default.AzureCLI.KubernetesDistro': kubernetes_distro,
        'Context.Default.AzureCLI.KubernetesInfra': kubernetes_infra
    }
    telemetry.add_extension_event('connectedk8s', kubernetes_properties)


def check_faulty_helm_version(helm_core_utils):
    # Check helm version
    helm_version = helm_core_utils.check_helm_version()
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.HelmVersion': helm_version})

    # Check for faulty pre-release helm versions
    if "3.3.0-rc" in helm_version:
        raise ClientRequestError("The current helm version is not supported for azure-arc onboarding.",
                                 recommendation="Please upgrade helm to a stable version and try again.")


def validate_helm_environment(cmd, values_file, values_file_provided):
    # Validate the helm environment file for Dogfood.
    dp_endpoint_dogfood = None
    release_train_dogfood = None
    azure_cloud = None
    if cmd.cli_ctx.cloud.endpoints.resource_manager == consts.Dogfood_RMEndpoint:
        azure_cloud = consts.Azure_DogfoodCloudName
        dp_endpoint_dogfood, release_train_dogfood = validate_env_file_dogfood(values_file, values_file_provided)

    return azure_cloud, dp_endpoint_dogfood, release_train_dogfood


def get_helm_registry_path(cmd, location, helm_core_utils, arc_agent_version, dp_endpoint_dogfood,
                           release_train_dogfood):
    # Adding helm repo
    if os.getenv('HELMREPONAME') and os.getenv('HELMREPOURL'):
        helm_core_utils.add_helm_repo(os.getenv('HELMREPONAME'), os.getenv('HELMREPOURL'))

    # Setting the config dataplane endpoint
    config_dp_endpoint = get_config_dp_endpoint(cmd, location)

    # Retrieving Helm chart OCI Artifact location
    registry_path = os.getenv('HELMREGISTRY') if os.getenv('HELMREGISTRY') \
        else get_helm_registry(cmd, config_dp_endpoint, dp_endpoint_dogfood, release_train_dogfood)

    reg_path_array = registry_path.split(':')
    agent_version = reg_path_array[1]

    # Set agent version in registry path
    if arc_agent_version is not None:
        agent_version = arc_agent_version
        registry_path = reg_path_array[0] + ":" + agent_version

    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.AgentVersion': agent_version})

    return registry_path


def generate_public_private_key():
    # Generate public-private key pair
    try:
        key_pair = RSA.generate(4096)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.KeyPair_Generate_Fault_Type,
                                summary='Failed to generate public-private key pair')
        raise CLIInternalError("Failed to generate public-private key pair. " + str(e))
    try:
        public_key = get_public_key(key_pair)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.PublicKey_Export_Fault_Type,
                                summary='Failed to export public key')
        raise CLIInternalError("Failed to export public key." + str(e))
    try:
        private_key_pem = get_private_key(key_pair)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.PrivateKey_Export_Fault_Type,
                                summary='Failed to export private key')
        raise CLIInternalError("Failed to export private key." + str(e))

    return public_key, private_key_pem
