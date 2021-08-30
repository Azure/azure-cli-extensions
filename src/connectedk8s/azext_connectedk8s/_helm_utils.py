# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import shutil

import yaml
from knack.log import get_logger
from azure.cli.core.util import send_raw_request
from azure.cli.core import telemetry
from azure.cli.core.azclierror import CLIInternalError, ValidationError, FileOperationError, ClientRequestError
from azext_connectedk8s._helm_core_utils import HelmCoreUtils
import azext_connectedk8s._constants as consts

logger = get_logger(__name__)


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


def check_faulty_helm_version(helm_core_utils):
    # Check helm version
    helm_version = helm_core_utils.check_helm_version()
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.HelmVersion': helm_version})

    # Check for faulty pre-release helm versions
    if "3.3.0-rc" in helm_version:
        raise ClientRequestError("The current helm version is not supported for azure-arc onboarding.",
                                 recommendation="Please upgrade helm to a stable version and try again.")


def validate_helm_environment_file(cmd, values_file, values_file_provided):
    # Validate the helm environment file for Dogfood.
    dp_endpoint_dogfood = None
    release_train_dogfood = None
    azure_cloud = None
    if cmd.cli_ctx.cloud.endpoints.resource_manager == consts.Dogfood_RMEndpoint:
        azure_cloud = consts.Azure_DogfoodCloudName
        dp_endpoint_dogfood, release_train_dogfood = validate_env_file_dogfood(values_file, values_file_provided)

    return azure_cloud, dp_endpoint_dogfood, release_train_dogfood


def get_config_dp_endpoint(cmd, location):
    cloud_based_domain = cmd.cli_ctx.cloud.endpoints.active_directory.split('.')[2]
    config_dp_endpoint = "https://{}.dp.kubernetesconfiguration.azure.{}".format(location, cloud_based_domain)
    return config_dp_endpoint


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
