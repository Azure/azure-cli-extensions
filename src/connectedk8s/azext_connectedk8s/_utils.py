# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import shutil
import subprocess
from subprocess import Popen, PIPE

from knack.util import CLIError
from knack.log import get_logger
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import send_raw_request
from azure.cli.core import telemetry
from msrest.exceptions import AuthenticationError, HttpOperationError, TokenExpiredError, ValidationError
from msrestazure.azure_exceptions import CloudError
from kubernetes.client.rest import ApiException
from azext_connectedk8s._client_factory import _resource_client_factory
import azext_connectedk8s._constants as consts


logger = get_logger(__name__)

# pylint: disable=line-too-long
# pylint: disable=bare-except


def validate_location(cmd, location):
    subscription_id = get_subscription_id(cmd.cli_ctx)
    rp_locations = []
    resourceClient = _resource_client_factory(cmd.cli_ctx, subscription_id=subscription_id)
    try:
        providerDetails = resourceClient.providers.get('Microsoft.Kubernetes')
    except Exception as e:  # pylint: disable=broad-except
        arm_exception_handler(e, consts.Get_ResourceProvider_Fault_Type, 'Failed to fetch resource provider details')
    for resourceTypes in providerDetails.resource_types:
        if resourceTypes.resource_type == 'connectedClusters':
            rp_locations = [location.replace(" ", "").lower() for location in resourceTypes.locations]
            if location.lower() not in rp_locations:
                telemetry.set_user_fault()
                telemetry.set_exception(exception='Location not supported', fault_type=consts.Invalid_Location_Fault_Type,
                                        summary='Provided location is not supported for creating connected clusters')
                raise CLIError("Connected cluster resource creation is supported only in the following locations: " +
                               ', '.join(map(str, rp_locations)) +
                               ". Use the --location flag to specify one of these locations.")
            break


def get_chart_path(registry_path, kube_config, kube_context):
    # Pulling helm chart from registry
    os.environ['HELM_EXPERIMENTAL_OCI'] = '1'
    pull_helm_chart(registry_path, kube_config, kube_context)

    # Exporting helm chart after cleanup
    chart_export_path = os.path.join(os.path.expanduser('~'), '.azure', 'AzureArcCharts')
    try:
        if os.path.isdir(chart_export_path):
            shutil.rmtree(chart_export_path)
    except:
        logger.warning("Unable to cleanup the azure-arc helm charts already present on the machine. In case of failure, please cleanup the directory '%s' and try again.", chart_export_path)
    export_helm_chart(registry_path, chart_export_path, kube_config, kube_context)

    # Returning helm chart path
    helm_chart_path = os.path.join(chart_export_path, 'azure-arc-k8sagents')
    chart_path = os.getenv('HELMCHART') if os.getenv('HELMCHART') else helm_chart_path
    return chart_path


def pull_helm_chart(registry_path, kube_config, kube_context):
    cmd_helm_chart_pull = ["helm", "chart", "pull", registry_path]
    if kube_config:
        cmd_helm_chart_pull.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_chart_pull.extend(["--kube-context", kube_context])
    response_helm_chart_pull = subprocess.Popen(cmd_helm_chart_pull, stdout=PIPE, stderr=PIPE)
    _, error_helm_chart_pull = response_helm_chart_pull.communicate()
    if response_helm_chart_pull.returncode != 0:
        telemetry.set_exception(exception=error_helm_chart_pull.decode("ascii"), fault_type=consts.Pull_HelmChart_Fault_Type,
                                summary='Unable to pull helm chart from the registry')
        raise CLIError("Unable to pull helm chart from the registry '{}': ".format(registry_path) + error_helm_chart_pull.decode("ascii"))


def export_helm_chart(registry_path, chart_export_path, kube_config, kube_context):
    cmd_helm_chart_export = ["helm", "chart", "export", registry_path, "--destination", chart_export_path]
    if kube_config:
        cmd_helm_chart_export.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_chart_export.extend(["--kube-context", kube_context])
    response_helm_chart_export = subprocess.Popen(cmd_helm_chart_export, stdout=PIPE, stderr=PIPE)
    _, error_helm_chart_export = response_helm_chart_export.communicate()
    if response_helm_chart_export.returncode != 0:
        telemetry.set_exception(exception=error_helm_chart_export.decode("ascii"), fault_type=consts.Export_HelmChart_Fault_Type,
                                summary='Unable to export helm chart from the registry')
        raise CLIError("Unable to export helm chart from the registry '{}': ".format(registry_path) + error_helm_chart_export.decode("ascii"))


def add_helm_repo(kube_config, kube_context):
    repo_name = os.getenv('HELMREPONAME')
    repo_url = os.getenv('HELMREPOURL')
    cmd_helm_repo = ["helm", "repo", "add", repo_name, repo_url]
    if kube_config:
        cmd_helm_repo.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_repo.extend(["--kube-context", kube_context])
    response_helm_repo = Popen(cmd_helm_repo, stdout=PIPE, stderr=PIPE)
    _, error_helm_repo = response_helm_repo.communicate()
    if response_helm_repo.returncode != 0:
        telemetry.set_exception(exception=error_helm_repo.decode("ascii"), fault_type=consts.Add_HelmRepo_Fault_Type,
                                summary='Failed to add helm repository')
        raise CLIError("Unable to add repository {} to helm: ".format(repo_url) + error_helm_repo.decode("ascii"))


def get_helm_registry(cmd, location, dp_endpoint_dogfood=None, release_train_dogfood=None):
    # Setting uri
    get_chart_location_url = "https://{}.dp.kubernetesconfiguration.azure.com/{}/GetLatestHelmPackagePath?api-version=2019-11-01-preview".format(location, 'azure-arc-k8sagents')
    release_train = os.getenv('RELEASETRAIN') if os.getenv('RELEASETRAIN') else 'stable'
    if dp_endpoint_dogfood:
        get_chart_location_url = "{}/azure-arc-k8sagents/GetLatestHelmPackagePath?api-version=2019-11-01-preview".format(dp_endpoint_dogfood)
        if release_train_dogfood:
            release_train = release_train_dogfood
    uri_parameters = ["releaseTrain={}".format(release_train)]
    resource = cmd.cli_ctx.cloud.endpoints.active_directory_resource_id

    # Sending request
    try:
        r = send_raw_request(cmd.cli_ctx, 'post', get_chart_location_url, uri_parameters=uri_parameters, resource=resource)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.Get_HelmRegistery_Path_Fault_Type,
                                summary='Error while fetching helm chart registry path')
        raise CLIError("Error while fetching helm chart registry path: " + str(e))
    if r.content:
        try:
            return r.json().get('repositoryPath')
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Get_HelmRegistery_Path_Fault_Type,
                                    summary='Error while fetching helm chart registry path')
            raise CLIError("Error while fetching helm chart registry path from JSON response: " + str(e))
    else:
        telemetry.set_exception(exception='No content in response', fault_type=consts.Get_HelmRegistery_Path_Fault_Type,
                                summary='No content in acr path response')
        raise CLIError("No content was found in helm registry path response.")


def arm_exception_handler(ex, fault_type, summary, return_if_not_found=False):
    if isinstance(ex, AuthenticationError):
        telemetry.set_user_fault()
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        raise CLIError("Authentication error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, TokenExpiredError):
        telemetry.set_user_fault()
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        raise CLIError("Token expiration error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, HttpOperationError):
        status_code = ex.response.status_code
        if status_code == 404 and return_if_not_found:
            return
        if status_code // 100 == 4:
            telemetry.set_user_fault()
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        raise CLIError("Http operation error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, ValidationError):
        telemetry.set_user_fault()
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        raise CLIError("Validation error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, CloudError):
        status_code = ex.status_code
        if status_code == 404 and return_if_not_found:
            return
        if status_code // 100 == 4:
            telemetry.set_user_fault()
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        raise CLIError("Cloud error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
    raise CLIError("Error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))


def kubernetes_exception_handler(ex, fault_type, summary, error_message='Error occured while connecting to the kubernetes cluster: ',
                                 message_for_unauthorized_request='The user does not have required privileges on the kubernetes cluster to deploy Azure Arc enabled Kubernetes agents. Please ensure you have cluster admin privileges on the cluster to onboard.',
                                 message_for_not_found='The requested kubernetes resource was not found.', raise_error=True):
    telemetry.set_user_fault()
    if isinstance(ex, ApiException):
        status_code = ex.status
        if status_code == 403:
            logger.warning(message_for_unauthorized_request)
        if status_code == 404:
            logger.warning(message_for_not_found)
        if raise_error:
            telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
            raise CLIError(error_message + "\nError Response: " + str(ex.body))
    else:
        if raise_error:
            telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
            raise CLIError(error_message + "\nError: " + str(ex))
