# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import shutil
import subprocess
from subprocess import Popen, PIPE
import time
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
from datetime import datetime, timedelta
import colorama
import base64
import platform
from six.moves.urllib.request import urlopen  # pylint: disable=import-error
from tabulate import tabulate  # pylint: disable=import-error
import tempfile


from knack.log import get_logger
from knack.prompting import NoTTYException, prompt_y_n
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import send_raw_request
from azure.cli.core import telemetry
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from msrest.exceptions import AuthenticationError, HttpOperationError, TokenExpiredError
from msrest.exceptions import ValidationError as MSRestValidationError
from kubernetes.client.rest import ApiException
from azext_connectedk8s._client_factory import _resource_client_factory, _resource_providers_client
import azext_connectedk8s._constants as consts
from kubernetes import client as kube_client
from azure.cli.core.azclierror import CLIInternalError, ClientRequestError, ArgumentUsageError, ManualInterrupt, AzureResponseError, AzureInternalError, ValidationError
from azext_connectedk8s._client_factory import get_subscription_client, _resource_providers_client, cf_storage

logger = get_logger(__name__)

# pylint: disable=line-too-long
# pylint: disable=bare-except


def setup_logger(logger_name, log_file, level=logging.DEBUG):
    loggr = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)

    loggr.setLevel(level)
    loggr.addHandler(fileHandler)


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

    if isinstance(ex, MSRestValidationError):
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        raise AzureResponseError("Validation error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, HttpResponseError):
        status_code = ex.status_code
        if status_code == 404 and return_if_not_found:
            return
        if status_code // 100 == 4:
            telemetry.set_user_fault()
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        if status_code // 100 == 5:
            raise AzureInternalError("Http response error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))
        raise AzureResponseError("Http response error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, ResourceNotFoundError) and return_if_not_found:
        return

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
    return None


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
                         kube_config, kube_context, no_wait, values_file_provided, values_file, cloud_name, disable_auto_upgrade, enable_custom_locations, custom_locations_oid, onboarding_timeout="600"):
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
        # Change --timeout format for helm client to understand
        onboarding_timeout = onboarding_timeout + "s"
        cmd_helm_install.extend(["--wait", "--timeout", "{}".format(onboarding_timeout)])
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


def get_latest_extension_version(custom_logger, extension_name='connectedk8s', max_retries=3, timeout=2):
    git_url = "https://raw.githubusercontent.com/Azure/azure-cli-extensions/master/src/index.json"
    # or use "https://aka.ms/azure-cli-extension-index-v1"
    try:
        with requests.Session() as s:
            s.mount(git_url, requests.adapters.HTTPAdapter(max_retries=max_retries))
            response = s.get(git_url, timeout=timeout)
            response_json = response.json()
            version_list = []
            for ver in response_json["extensions"][extension_name]:
                version_list.append(ver["metadata"]["version"])
            version_list.sort()
            return version_list[-1]
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as ex:
        custom_logger.error('Internet connectivity problem detected. Error: {}'.format(str(ex)))
    except Exception as ex:
        custom_logger.error("Failed to get the latest connectedk8s version from '%s'. %s", git_url, str(ex))
    return None


def get_existing_extension_version(extension_name='connectedk8s'):
    from azure.cli.core.extension import get_extensions
    extensions = get_extensions()
    if extensions:
        for ext in extensions:
            if ext.name == extension_name:
                return ext.version or 'Unknown'

    return 'NotFound'


def check_connectivity(url='https://azure.microsoft.com', max_retries=5, timeout=1):
    import timeit
    start = timeit.default_timer()
    success = None
    try:
        with requests.Session() as s:
            s.mount(url, requests.adapters.HTTPAdapter(max_retries=max_retries))
            s.head(url, timeout=timeout)
            success = True
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as ex:
        logger.error('Internet connectivity problem detected. Error: {}'.format(str(ex)))
        success = False
    except Exception as ex:  # pylint: disable=broad-except
        logger.error("Failed to check Internet connectivity. Error: %s", str(ex))
        success = False
    stop = timeit.default_timer()
    logger.debug('Connectivity check: %s sec', stop - start)
    return success


def validate_azure_management_reachability(subscription_id):
    try:
        get_subscription_client().get(subscription_id)
    except Exception as ex:
        logger.warning("Not able to reach azure management endpoints. Exception: " + str(ex))


# Returns a list of kubernetes pod objects in a given namespace. Object description at: https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1PodList.md
def get_pod_list(api_instance, namespace, label_selector="", field_selector=""):
    try:
        return api_instance.list_namespaced_pod(namespace, label_selector=label_selector, field_selector=field_selector)
    except Exception as e:
        logger.debug("Error occurred when retrieving pod information: " + str(e))


def try_list_node_fix():
    try:
        from kubernetes.client.models.v1_container_image import V1ContainerImage

        def names(self, names):
            self._names = names

        V1ContainerImage.names = V1ContainerImage.names.setter(names)
    except Exception as ex:
        logger.debug("Error while trying to monkey patch the fix for list_node(): {}".format(str(ex)))


def get_kubernetes_secret(api_instance, namespace, secret_name, custom_logger=None):
    try:
        return api_instance.read_namespaced_secret(secret_name, namespace)
    except Exception as e:
        handle_logging_error(custom_logger, "Error occurred when retrieving secret '{}': ".format(secret_name) + str(e))


def handle_logging_error(custom_logger, error_string):
    if custom_logger:
        custom_logger.error(error_string)
    else:
        logger.debug(error_string)


def check_provider_registrations(cli_ctx):
    try:
        rp_client = _resource_providers_client(cli_ctx)
        cc_registration_state = rp_client.get(consts.Connected_Cluster_Provider_Namespace).registration_state
        if cc_registration_state != "Registered":
            telemetry.set_exception(exception="{} provider is not registered".format(consts.Connected_Cluster_Provider_Namespace), fault_type=consts.CC_Provider_Namespace_Not_Registered_Fault_Type,
                                    summary="{} provider is not registered".format(consts.Connected_Cluster_Provider_Namespace))
            raise ValidationError("{} provider is not registered. Please register it using 'az provider register -n 'Microsoft.Kubernetes' before running the connect command.".format(consts.Connected_Cluster_Provider_Namespace))
        kc_registration_state = rp_client.get(consts.Kubernetes_Configuration_Provider_Namespace).registration_state
        if kc_registration_state != "Registered":
            telemetry.set_user_fault()
            logger.warning("{} provider is not registered".format(consts.Kubernetes_Configuration_Provider_Namespace))
    except ValidationError as e:
        raise e
    except Exception as ex:
        logger.warning("Couldn't check the required provider's registration status. Error: {}".format(str(ex)))


def can_create_clusterrolebindings(configuration):
    try:
        api_instance = kube_client.AuthorizationV1Api(kube_client.ApiClient(configuration))
        access_review = kube_client.V1SelfSubjectAccessReview(spec={
            "resourceAttributes": {
                "verb": "create",
                "resource": "clusterrolebindings",
                "group": "rbac.authorization.k8s.io"
            }
        })
        response = api_instance.create_self_subject_access_review(access_review)
        return response.status.allowed
    except Exception as ex:
        logger.warning("Couldn't check for the permission to create clusterrolebindings on this k8s cluster. Error: {}".format(str(ex)))
        return "Unknown"


def check_delete_job(configuration, namespace):
    try:
        api_instance = kube_client.BatchV1Api(kube_client.ApiClient(configuration))
        api_response = api_instance.list_namespaced_job(namespace)
        for item in list(api_response.items):
            annotations = item.metadata.annotations
            if annotations.get("helm.sh/hook") == "pre-delete":
                job_status = item.status
                if job_status.succeeded == 0 or job_status.active > 0:
                    logger.warning("Delete Job status conditions: {}".format(job_status.conditions))
                break
    except Exception as e:
        logger.debug("Error occurred while retrieving status of the delete job: {}".format(str(e)))


def try_upload_log_file(storage_account_name, storage_token, container_name, log_file_path):
    try:  # Storage Upload
        import uuid
        from azure.storage.blob import BlobServiceClient
        storage_account_url = f"https://{storage_account_name}.blob.core.windows.net/"
        blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=storage_token)

        try:
            blob_service_client.create_container(container_name)
        except Exception as ex:
            raise Exception("Storage account container creation error: {}".format(str(ex)))

        blob_client = blob_service_client.get_blob_client(container=container_name, blob="connectedk8s_troubleshoot.log")
        with open(log_file_path, "rb") as data:  # Upload log file as blob
            blob_client.upload_blob(data)
    except Exception as e:
        logger.warning("Error while uploading the log file to storage account: {}".format(str(e)))


def setup_validate_storage_account(cli_ctx, storage_account, sas_token, rg_name):
    if storage_account is None:
        return None, None, None
    try:
        from msrestazure.tools import is_valid_resource_id, parse_resource_id, resource_id
        from azure.storage.blob import generate_account_sas
        if not is_valid_resource_id(storage_account):
            storage_account_id = resource_id(
                subscription=get_subscription_id(cli_ctx),
                resource_group=rg_name,
                namespace='Microsoft.Storage', type='storageAccounts',
                name=storage_account
            )
        else:
            storage_account_id = storage_account

        if is_valid_resource_id(storage_account_id):
            try:
                parsed_storage_account = parse_resource_id(storage_account_id)
            except Exception as ex:
                logger.warning("Couldn't validate the storage account details. Error: {}".format(str(ex)))
                return None, None, None
        else:
            logger.warning("Invalid storage account id - {}".format(storage_account_id))
            return None, None, None

        storage_account_name = parsed_storage_account['name']

        readonly_sas_token = None
        if sas_token is None:
            storage_client = cf_storage(
                cli_ctx, parsed_storage_account['subscription'])
            storage_account_keys = storage_client.storage_accounts.list_keys(parsed_storage_account['resource_group'], storage_account_name)
            sas_token = generate_account_sas(account_name=storage_account_name, account_key=storage_account_keys.keys[0].value, resource_types='sco', permission='rwdlacup', expiry=datetime.utcnow() + timedelta(days=1))
            readonly_sas_token = generate_account_sas(account_name=storage_account_name, account_key=storage_account_keys.keys[0].value, resource_types='sco', permission='rl', expiry=datetime.utcnow() + timedelta(days=1))
        return storage_account_name, sas_token, readonly_sas_token
    except Exception as ex:
        logger.warning("Error while validating the credentials for the storage account: {}".format(str(ex)))
        return None, None, None


def format_hyperlink(the_link):
    return f'\033[1m{colorama.Style.BRIGHT}{colorama.Fore.BLUE}{the_link}{colorama.Style.RESET_ALL}'


def format_bright(msg):
    return f'\033[1m{colorama.Style.BRIGHT}{msg}{colorama.Style.RESET_ALL}'


def display_diagnostics_report(kubectl_prior):   # pylint: disable=too-many-statements
    if not which('kubectl'):
        raise ValidationError('Can not find kubectl executable in PATH')
    subprocess_cmd = kubectl_prior + ["get", "node", "--no-headers"]
    nodes = subprocess.check_output(
        subprocess_cmd,
        universal_newlines=True)
    logger.debug(nodes)
    node_lines = nodes.splitlines()
    ready_nodes = {}
    for node_line in node_lines:
        columns = node_line.split()
        logger.debug(node_line)
        if columns[1] != "Ready":
            logger.warning("Node %s is not Ready. Current state is: %s.", columns[0], columns[1])
        else:
            ready_nodes[columns[0]] = False

    logger.debug('There are %s ready nodes in the cluster', str(len(ready_nodes)))

    if not ready_nodes:
        logger.warning('No nodes are ready in the current cluster. Diagnostics info might not be available.')

    network_config_array = []
    network_status_array = []
    apds_created = False

    max_retry = 10
    for retry in range(0, max_retry):
        if not apds_created:
            subprocess_cmd = kubectl_prior + ["get", "apd", "-n", "aks-periscope", "--no-headers"]
            try:
                apd = subprocess.check_output(subprocess_cmd, universal_newlines=True)
            except subprocess.CalledProcessError as ex:
                logger.debug(f"Exception while running {subprocess_cmd}: {ex.returncode}, {ex.output}. Retrying...")
                continue

            apd_lines = apd.splitlines()
            if apd_lines and 'No resources found' in apd_lines[0]:
                apd_lines.pop(0)

            print("Got {} diagnostic results for {} ready nodes{}\r".format(len(apd_lines),
                                                                            len(ready_nodes),
                                                                            '.' * retry), end='')
            if len(apd_lines) < len(ready_nodes):
                time.sleep(3)
            else:
                apds_created = True
                print()
        else:
            for node_name in ready_nodes:
                if ready_nodes[node_name]:
                    continue
                apdName = "aks-periscope-diagnostic-" + node_name
                try:
                    subprocess_cmd = kubectl_prior + ["get", "apd", apdName, "-n", "aks-periscope", "-o=jsonpath={.spec.networkconfig}"]
                    network_config = subprocess.check_output(
                        subprocess_cmd,
                        universal_newlines=True)
                    logger.debug('Dns status for node %s is %s', node_name, network_config)
                    subprocess_cmd = kubectl_prior + ["get", "apd", apdName, "-n", "aks-periscope", "-o=jsonpath={.spec.networkoutbound}"]
                    network_status = subprocess.check_output(
                        subprocess_cmd,
                        universal_newlines=True)
                    logger.debug('Network status for node %s is %s', node_name, network_status)

                    if not network_config or not network_status:
                        print("The diagnostics information for node {} is not ready yet. "
                              "Will try again in 10 seconds.".format(node_name))
                        time.sleep(10)
                        break

                    network_config_array += json.loads('[' + network_config + ']')
                    network_status_object = json.loads(network_status)
                    network_status_array += format_diag_status(network_status_object)
                    ready_nodes[node_name] = True
                except subprocess.CalledProcessError as err:
                    raise CLIInternalError(err.output)

    print()
    if network_config_array:
        print("Below are the network configuration for each node: ")
        print()
        print(tabulate(network_config_array, headers="keys", tablefmt='simple'))
        print()
    else:
        logger.warning("Could not get network config. "
                       "Please run 'az connectedk8s troubleshoot' command again later to get the analysis results.")

    if network_status_array:
        print("Below are the network connectivity results for each node:")
        print()
        print(tabulate(network_status_array, headers="keys", tablefmt='simple'))
    else:
        logger.warning("Could not get networking status. "
                       "Please run 'az connectedk8s troubleshoot' command again later to get the analysis results.")


def format_diag_status(diag_status):
    for diag in diag_status:
        if diag["Status"]:
            if "Error:" in diag["Status"]:
                diag["Status"] = f'{colorama.Fore.RED}{diag["Status"]}{colorama.Style.RESET_ALL}'
            else:
                diag["Status"] = f'{colorama.Fore.GREEN}{diag["Status"]}{colorama.Style.RESET_ALL}'

    return diag_status


def collect_periscope_logs(resource_group_name, name, storage_account_name=None, sas_token=None, container_name="connectedk8stroubleshoot", readonly_sas_token=None, kube_context=None, kube_config=None):
    colorama.init()

    if not which('kubectl'):
        raise ValidationError('Can not find kubectl executable in PATH')

    kubectl_prior = ["kubectl"]
    if kube_config:
        kubectl_prior.extend(["--kubeconfig", kube_config])
    if kube_context:
        kubectl_prior.extend(["--context", kube_context])

    readonly_sas_token = readonly_sas_token.strip('?')

    from knack.prompting import prompt_y_n

    print()
    print('This will deploy a daemon set to your cluster to collect logs and diagnostic information and '
          f'save them to the storage account '
          f'{colorama.Style.BRIGHT}{colorama.Fore.GREEN}{storage_account_name}{colorama.Style.RESET_ALL} as '
          f'outlined in {format_hyperlink("http://aka.ms/AKSPeriscope")}.')
    print()
    print('If you share access to that storage account to Azure support, you consent to the terms outlined'
          f' in {format_hyperlink("http://aka.ms/DiagConsent")}.')
    print()
    if not prompt_y_n('Do you confirm?', default="n"):
        return

    sas_token = sas_token.strip('?')
    deployment_yaml = urlopen(
        "https://raw.githubusercontent.com/Azure/aks-periscope/master/deployment/aks-periscope.yaml").read().decode()
    deployment_yaml = deployment_yaml.replace("# <accountName, base64 encoded>",
                                              (base64.b64encode(bytes(storage_account_name, 'ascii'))).decode('ascii'))
    deployment_yaml = deployment_yaml.replace("# <saskey, base64 encoded>",
                                              (base64.b64encode(bytes("?" + sas_token, 'ascii'))).decode('ascii'))
    deployment_yaml = deployment_yaml.replace("aksrepos.azurecr.io/staging/aks-periscope:v0.4", "aksrepos.azurecr.io/staging/aks-periscope:0.5")
    container_logs = "azure-arc"
    kube_objects = "azure-arc/pod azure-arc/service"
    yaml_lines = deployment_yaml.splitlines()
    for index, line in enumerate(yaml_lines):
        if "DIAGNOSTIC_CONTAINERLOGS_LIST" in line:
            yaml_lines[index] = line + ' ' + container_logs
        if "AZURE_BLOB_SAS_KEY" in line:
            yaml_lines[index] = line + '\n' + '  AZURE_BLOB_CONTAINER_NAME: ' + base64.b64encode(bytes(container_name, 'ascii')).decode('ascii')
        if "DIAGNOSTIC_KUBEOBJECTS_LIST" in line:
            yaml_lines[index] = line.replace('kube-system/deployment', '') + kube_objects
        if "COLLECTOR_LIST" in line:
            yaml_lines[index] = '  COLLECTOR_LIST: connectedCluster'

    deployment_yaml = '\n'.join(yaml_lines)
    fd, temp_yaml_path = tempfile.mkstemp()
    temp_yaml_file = os.fdopen(fd, 'w+t')
    try:
        temp_yaml_file.write(deployment_yaml)
        temp_yaml_file.flush()
        temp_yaml_file.close()
        try:
            print("Cleaning up diagnostic container resources from the k8s cluster if existing...")
            delete_periscope_resources(kubectl_prior)

            print()

            print(f"{colorama.Fore.GREEN}Deploying diagnostic container on the K8s cluster...")
            subprocess_cmd = kubectl_prior + ["apply", "-f", temp_yaml_path, "-n", "aks-periscope"]
            subprocess.check_output(subprocess_cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            raise CLIInternalError(err.output)
    finally:
        os.remove(temp_yaml_path)

    print()
    # log_storage_account_url = f"https://{storage_account_name}.blob.core.windows.net/"

    print(f'{colorama.Fore.GREEN}Your logs are being uploaded to storage account {format_bright(storage_account_name)}...')

    print()
    print(f'You can download Azure Storage Explorer here '
          f'{format_hyperlink("https://azure.microsoft.com/en-us/features/storage-explorer/")}'
          f' to check the logs by accessing the storage account {storage_account_name}.')
    # f' to check the logs by adding the storage account using the following URL:')
    # print(f'{format_hyperlink(log_storage_account_url)}')

    print()
    if not prompt_y_n('Do you want to see analysis results now?', default="n"):
        print(f"You can rerun 'az connectedk8s troubleshoot -g {resource_group_name} -n {name}' "
              f"anytime to check the analysis results.")
    else:
        display_diagnostics_report(kubectl_prior)

    print("Deleting existing aks-periscope resources from cluster ...")

    try:
        delete_periscope_resources(kubectl_prior)
    except Exception as ex:
        raise Exception("Error occurred while deleting the aks-periscope resources. Error: {}".format(str(ex)))


def delete_periscope_resources(kubectl_prior):
    subprocess_cmd = kubectl_prior + ["delete", "serviceaccount,configmap,daemonset,secret", "--all", "-n", "aks-periscope", "--ignore-not-found"]
    subprocess.call(subprocess_cmd, stderr=subprocess.STDOUT)

    subprocess_cmd = kubectl_prior + ["delete", "ClusterRoleBinding", "aks-periscope-role-binding", "--ignore-not-found"]
    subprocess.call(subprocess_cmd, stderr=subprocess.STDOUT)

    subprocess_cmd = kubectl_prior + ["delete", "ClusterRole", "aks-periscope-role", "--ignore-not-found"]
    subprocess.call(subprocess_cmd, stderr=subprocess.STDOUT)

    subprocess_cmd = kubectl_prior + ["delete", "--all", "apd", "-n", "aks-periscope", "--ignore-not-found"]
    subprocess.call(subprocess_cmd, stderr=subprocess.STDOUT)

    subprocess_cmd = kubectl_prior + ["delete", "CustomResourceDefinition", "diagnostics.aks-periscope.azure.github.com", "--ignore-not-found"]
    subprocess.call(subprocess_cmd, stderr=subprocess.STDOUT)


def which(binary):
    path_var = os.getenv('PATH')
    if platform.system() == 'Windows':
        binary = binary + '.exe'
        parts = path_var.split(';')
    else:
        parts = path_var.split(':')

    for part in parts:
        bin_path = os.path.join(part, binary)
        if os.path.exists(bin_path) and os.path.isfile(bin_path) and os.access(bin_path, os.X_OK):
            return bin_path

    return None


def try_archive_log_file(troubleshoot_log_path, output_file):
    try:
        # Creating the .tar.gz for logs and deleting the actual log file
        import tarfile
        with tarfile.open(output_file, "w:gz") as tar:
            tar.add(troubleshoot_log_path, 'connected8s_troubleshoot.log')
        logging.shutdown()  # To release log file handler, so that the actual log file can be removed after archiving
        os.remove(troubleshoot_log_path)
        print(f"{colorama.Style.BRIGHT}{colorama.Fore.GREEN}Some diagnostic logs have been collected and archived at '{output_file}'.")
    except Exception as ex:
        logger.error("Error occured while archiving the log file: {}".format(str(ex)))
        print(f"{colorama.Style.BRIGHT}{colorama.Fore.GREEN}You can find the unarchived log file at '{troubleshoot_log_path}'.")


def validate_node_api_response(api_instance, node_api_response):
    if node_api_response is None:
        try:
            node_api_response = api_instance.list_node()
            return node_api_response
        except Exception as ex:
            logger.debug("Error occcured while listing nodes on this kubernetes cluster: {}".format(str(ex)))
            return None
    else:
        return node_api_response
