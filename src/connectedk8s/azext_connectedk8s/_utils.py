# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import shutil
import subprocess
from subprocess import Popen, PIPE
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json

from knack.util import CLIError
from knack.log import get_logger
from knack.prompting import NoTTYException, prompt_y_n
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import send_raw_request
from azure.cli.core import telemetry
from msrest.exceptions import AuthenticationError, HttpOperationError, TokenExpiredError, ValidationError
from msrestazure.azure_exceptions import CloudError
from kubernetes.client.rest import ApiException
from azext_connectedk8s._client_factory import _resource_client_factory
import azext_connectedk8s._constants as consts
from kubernetes import client as kube_client
from azure.cli.core.azclierror import CLIInternalError, ClientRequestError, ArgumentUsageError, ManualInterrupt, AzureResponseError, AzureInternalError, ValidationError

logger = get_logger(__name__)

# pylint: disable=line-too-long
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
                telemetry.set_exception(exception='Location not supported', fault_type=consts.Invalid_Location_Fault_Type,
                                        summary='Provided location is not supported for creating connected clusters')
                raise ArgumentUsageError("Connected cluster resource creation is supported only in the following locations: " +
                                         ', '.join(map(str, rp_locations)), recommendation="Use the --location flag to specify one of these locations.")
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
        raise CLIInternalError("Unable to pull helm chart from the registry '{}': ".format(registry_path) + error_helm_chart_pull.decode("ascii"))


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
        raise CLIInternalError("Unable to export helm chart from the registry '{}': ".format(registry_path) + error_helm_chart_export.decode("ascii"))


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
        raise CLIInternalError("Unable to add repository {} to helm: ".format(repo_url) + error_helm_repo.decode("ascii"))


def get_helm_registry(cmd, config_dp_endpoint, dp_endpoint_dogfood=None, release_train_dogfood=None):
    # Setting uri
    get_chart_location_url = "{}/{}/GetLatestHelmPackagePath?api-version=2019-11-01-preview".format(config_dp_endpoint, 'azure-arc-k8sagents')
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
        raise CLIInternalError("Error while fetching helm chart registry path: " + str(e))
    if r.content:
        try:
            return r.json().get('repositoryPath')
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Get_HelmRegistery_Path_Fault_Type,
                                    summary='Error while fetching helm chart registry path')
            raise CLIInternalError("Error while fetching helm chart registry path from JSON response: " + str(e))
    else:
        telemetry.set_exception(exception='No content in response', fault_type=consts.Get_HelmRegistery_Path_Fault_Type,
                                summary='No content in acr path response')
        raise CLIInternalError("No content was found in helm registry path response.")


def arm_exception_handler(ex, fault_type, summary, return_if_not_found=False):
    if isinstance(ex, AuthenticationError):
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        raise AzureResponseError("Authentication error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, TokenExpiredError):
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        raise AzureResponseError("Token expiration error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, HttpOperationError):
        status_code = ex.response.status_code
        if status_code == 404 and return_if_not_found:
            return
        if status_code // 100 == 4:
            telemetry.set_user_fault()
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        if status_code // 100 == 5:
            raise AzureInternalError("Http operation error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))
        raise AzureResponseError("Http operation error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, ValidationError):
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        raise AzureResponseError("Validation error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, CloudError):
        status_code = ex.status_code
        if status_code == 404 and return_if_not_found:
            return
        if status_code // 100 == 4:
            telemetry.set_user_fault()
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        if status_code // 100 == 5:
            raise AzureInternalError("Cloud error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))
        raise AzureResponseError("Cloud error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
    raise ClientRequestError("Error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))


def kubernetes_exception_handler(ex, fault_type, summary, error_message='Error occured while connecting to the kubernetes cluster: ',
                                 message_for_unauthorized_request='The user does not have required privileges on the kubernetes cluster to deploy Azure Arc enabled Kubernetes agents. Please ensure you have cluster admin privileges on the cluster to onboard.',
                                 message_for_not_found='The requested kubernetes resource was not found.', raise_error=True):
    telemetry.set_user_fault()
    if isinstance(ex, ApiException):
        status_code = ex.status
        if status_code == 403:
            logger.warning(message_for_unauthorized_request)
        elif status_code == 404:
            logger.warning(message_for_not_found)
        else:
            logger.debug("Kubernetes Exception: " + str(ex))
        if raise_error:
            telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
            raise ValidationError(error_message + "\nError Response: " + str(ex.body))
    else:
        if raise_error:
            telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
            raise ValidationError(error_message + "\nError: " + str(ex))
        else:
            logger.debug("Kubernetes Exception: " + str(ex))


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


def ensure_namespace_cleanup(configuration):
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    timeout = time.time() + 180
    while True:
        if time.time() > timeout:
            telemetry.set_user_fault()
            logger.warning("Namespace 'azure-arc' still in terminating state. Please ensure that you delete the 'azure-arc' namespace before onboarding the cluster again.")
            return
        try:
            api_response = api_instance.list_namespace(field_selector='metadata.name=azure-arc')
            if not api_response.items:
                return
            time.sleep(5)
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Error while retrieving namespace information: " + str(e))
            kubernetes_exception_handler(e, consts.Get_Kubernetes_Namespace_Fault_Type, 'Unable to fetch kubernetes namespace',
                                         raise_error=False)


def delete_arc_agents(release_namespace, kube_config, kube_context, configuration):
    cmd_helm_delete = ["helm", "delete", "azure-arc", "--namespace", release_namespace]
    if kube_config:
        cmd_helm_delete.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_delete.extend(["--kube-context", kube_context])
    response_helm_delete = Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
    _, error_helm_delete = response_helm_delete.communicate()
    if response_helm_delete.returncode != 0:
        if 'forbidden' in error_helm_delete.decode("ascii") or 'Error: warning: Hook pre-delete' in error_helm_delete.decode("ascii") or 'Error: timed out waiting for the condition' in error_helm_delete.decode("ascii"):
            telemetry.set_user_fault()
        telemetry.set_exception(exception=error_helm_delete.decode("ascii"), fault_type=consts.Delete_HelmRelease_Fault_Type,
                                summary='Unable to delete helm release')
        raise CLIInternalError("Error occured while cleaning up arc agents. " +
                               "Helm release deletion failed: " + error_helm_delete.decode("ascii") +
                               " Please run 'helm delete azure-arc' to ensure that the release is deleted.")
    ensure_namespace_cleanup(configuration)


def helm_install_release(chart_path, subscription_id, kubernetes_distro, kubernetes_infra, resource_group_name, cluster_name,
                         location, onboarding_tenant_id, http_proxy, https_proxy, no_proxy, proxy_cert, private_key_pem,
                         kube_config, kube_context, no_wait, values_file_provided, values_file, cloud_name, disable_auto_upgrade, enable_custom_locations, custom_locations_oid):
    cmd_helm_install = ["helm", "upgrade", "--install", "azure-arc", chart_path,
                        "--set", "global.subscriptionId={}".format(subscription_id),
                        "--set", "global.kubernetesDistro={}".format(kubernetes_distro),
                        "--set", "global.kubernetesInfra={}".format(kubernetes_infra),
                        "--set", "global.resourceGroupName={}".format(resource_group_name),
                        "--set", "global.resourceName={}".format(cluster_name),
                        "--set", "global.location={}".format(location),
                        "--set", "global.tenantId={}".format(onboarding_tenant_id),
                        "--set", "global.onboardingPrivateKey={}".format(private_key_pem),
                        "--set", "systemDefaultValues.spnOnboarding=false",
                        "--set", "global.azureEnvironment={}".format(cloud_name),
                        "--set", "systemDefaultValues.clusterconnect-agent.enabled=true",
                        "--output", "json"]
    # Add custom-locations related params
    if enable_custom_locations:
        cmd_helm_install.extend(["--set", "systemDefaultValues.customLocations.enabled=true"])
        cmd_helm_install.extend(["--set", "systemDefaultValues.customLocations.oid={}".format(custom_locations_oid)])
    # To set some other helm parameters through file
    if values_file_provided:
        cmd_helm_install.extend(["-f", values_file])
    if disable_auto_upgrade:
        cmd_helm_install.extend(["--set", "systemDefaultValues.azureArcAgents.autoUpdate={}".format("false")])
    if https_proxy:
        cmd_helm_install.extend(["--set", "global.httpsProxy={}".format(https_proxy)])
    if http_proxy:
        cmd_helm_install.extend(["--set", "global.httpProxy={}".format(http_proxy)])
    if no_proxy:
        cmd_helm_install.extend(["--set", "global.noProxy={}".format(no_proxy)])
    if proxy_cert:
        cmd_helm_install.extend(["--set-file", "global.proxyCert={}".format(proxy_cert)])
    if https_proxy or http_proxy or no_proxy:
        cmd_helm_install.extend(["--set", "global.isProxyEnabled={}".format(True)])
    if kube_config:
        cmd_helm_install.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_install.extend(["--kube-context", kube_context])
    if not no_wait:
        cmd_helm_install.extend(["--wait"])
    response_helm_install = Popen(cmd_helm_install, stdout=PIPE, stderr=PIPE)
    _, error_helm_install = response_helm_install.communicate()
    if response_helm_install.returncode != 0:
        if ('forbidden' in error_helm_install.decode("ascii") or 'timed out waiting for the condition' in error_helm_install.decode("ascii")):
            telemetry.set_user_fault()
        telemetry.set_exception(exception=error_helm_install.decode("ascii"), fault_type=consts.Install_HelmRelease_Fault_Type,
                                summary='Unable to install helm release')
        logger.warning("Please check if the azure-arc namespace was deployed and run 'kubectl get pods -n azure-arc' to check if all the pods are in running state. A possible cause for pods stuck in pending state could be insufficient resources on the kubernetes cluster to onboard to arc.")
        raise CLIInternalError("Unable to install helm release: " + error_helm_install.decode("ascii"))


def flatten(dd, separator='.', prefix=''):
    try:
        if isinstance(dd, dict):
            return {prefix + separator + k if prefix else k: v for kk, vv in dd.items() for k, v in flatten(vv, separator, kk).items()}
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


def try_list_node_fix():
    try:
        from kubernetes.client.models.v1_container_image import V1ContainerImage

        def names(self, names):
            self._names = names

        V1ContainerImage.names = V1ContainerImage.names.setter(names)
    except Exception as ex:
        logger.debug("Error while trying to monkey patch the fix for list_node(): {}".format(str(ex)))
