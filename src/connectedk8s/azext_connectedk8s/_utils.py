# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import subprocess
from subprocess import Popen, PIPE
import requests

from knack.util import CLIError
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core import telemetry
from azext_connectedk8s._client_factory import _resource_client_factory
import azext_connectedk8s._constants as consts


def validate_location(cmd, location):
    subscription_id = get_subscription_id(cmd.cli_ctx)
    rp_locations = []
    resourceClient = _resource_client_factory(cmd.cli_ctx, subscription_id=subscription_id)
    providerDetails = resourceClient.providers.get('Microsoft.Kubernetes')
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

    # Exporting helm chart
    chart_export_path = os.path.join(os.path.expanduser('~'), '.azure', 'AzureArcCharts')
    export_helm_chart(registry_path, chart_export_path, kube_config, kube_context)
    # Helm Install
    helm_chart_path = os.path.join(chart_export_path, 'azure-arc-k8sagents')
    chart_path = os.getenv('HELMCHART') if os.getenv('HELMCHART') else helm_chart_path
    return chart_path


def pull_helm_chart(registry_path, kube_config, kube_context):
    cmd_helm_chart_pull = ["helm", "chart", "pull", registry_path, "--kubeconfig", kube_config]
    if kube_context:
        cmd_helm_chart_pull.extend(["--kube-context", kube_context])
    response_helm_chart_pull = subprocess.Popen(cmd_helm_chart_pull, stdout=PIPE, stderr=PIPE)
    _, error_helm_chart_pull = response_helm_chart_pull.communicate()
    if response_helm_chart_pull.returncode != 0:
        telemetry.set_exception(exception=error_helm_chart_pull.decode("ascii"), fault_type=consts.Pull_HelmChart_Fault_Type,
                                summary='Unable to pull helm chart from the registry')
        raise CLIError("Unable to pull helm chart from the registry '{}': ".format(registry_path) + error_helm_chart_pull.decode("ascii"))


def export_helm_chart(registry_path, chart_export_path, kube_config, kube_context):
    chart_export_path = os.path.join(os.path.expanduser('~'), '.azure', 'AzureArcCharts')
    cmd_helm_chart_export = ["helm", "chart", "export", registry_path, "--destination", chart_export_path, "--kubeconfig", kube_config]
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
    cmd_helm_repo = ["helm", "repo", "add", repo_name, repo_url, "--kubeconfig", kube_config]
    if kube_context:
        cmd_helm_repo.extend(["--kube-context", kube_context])
    response_helm_repo = Popen(cmd_helm_repo, stdout=PIPE, stderr=PIPE)
    _, error_helm_repo = response_helm_repo.communicate()
    if response_helm_repo.returncode != 0:
        telemetry.set_exception(exception=error_helm_repo.decode("ascii"), fault_type=consts.Add_HelmRepo_Fault_Type,
                                summary='Failed to add helm repository')
        raise CLIError("Unable to add repository {} to helm: ".format(repo_url) + error_helm_repo.decode("ascii"))


def get_helm_registry(profile, location):
    cred, _, _ = profile.get_login_credentials(
        resource='https://management.core.windows.net/')
    token = cred._token_retriever()[2].get('accessToken')  # pylint: disable=protected-access

    get_chart_location_url = "https://{}.dp.kubernetesconfiguration.azure.com/{}/GetLatestHelmPackagePath?api-version=2019-11-01-preview".format(location, 'azure-arc-k8sagents')
    query_parameters = {}
    query_parameters['releaseTrain'] = os.getenv('RELEASETRAIN') if os.getenv('RELEASETRAIN') else 'stable'
    header_parameters = {}
    header_parameters['Authorization'] = "Bearer {}".format(str(token))
    try:
        response = requests.post(get_chart_location_url, params=query_parameters, headers=header_parameters)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.Get_HelmRegistery_Path_Fault_Type,
                                summary='Error while fetching helm chart registry path')
        raise CLIError("Error while fetching helm chart registry path: " + str(e))
    if response.status_code == 200:
        return response.json().get('repositoryPath')
    telemetry.set_exception(exception=str(response.json()), fault_type=consts.Get_HelmRegistery_Path_Fault_Type,
                            summary='Error while fetching helm chart registry path')
    raise CLIError("Error while fetching helm chart registry path: {}".format(str(response.json())))
