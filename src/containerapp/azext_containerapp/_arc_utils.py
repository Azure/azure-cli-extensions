# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, consider-using-f-string, no-else-return, duplicate-string-formatting-argument, expression-not-assigned, too-many-locals, logging-fstring-interpolation, broad-except, pointless-statement, bare-except, unused-variable, redefined-outer-name, reimported, unused-import, consider-using-generator, broad-exception-raised

import json
import os
import shutil

from http import HTTPStatus
from knack.log import get_logger

from kubernetes import client, config, utils

from azure.cli.core.azclierror import (ValidationError, ResourceNotFoundError, CLIError, InvalidArgumentValueError)
from ._constants import (CUSTOM_CORE_DNS_VOLUME_NAME, CUSTOM_CORE_DNS_VOLUME_MOUNT_PATH,
                         CUSTOM_CORE_DNS, CORE_DNS, KUBE_SYSTEM, EMPTY_CUSTOM_CORE_DNS)

logger = get_logger(__name__)


def create_kube_client(kube_config, kube_context, skip_ssl_verification=False):
    default_config = get_kube_config(kube_config, kube_context, skip_ssl_verification)
    return client.ApiClient(default_config)


def get_kube_config(kube_config, kube_context, skip_ssl_verification=False):
    try:
        config.load_kube_config(config_file=kube_config, context=kube_context)
        default_config = client.Configuration.get_default_copy()
        if skip_ssl_verification:
            default_config.verify_ssl = False

        return default_config

    except config.config_exception.ConfigException as ce:
        raise ValidationError("Problem loading the kubeconfig file. "
                              "You should either save the kube configuration in the default kubernetes config location, "
                              "Or you should specify the kube config and context in parameter. Error: " + str(ce))
    except Exception as e:
        raise ValidationError("Problem loading the kubeconfig file." + str(e))


def check_kube_connection(kube_config, kube_context, skip_ssl_verification=False):
    logger.debug("Checking Connectivity to Cluster")
    get_kube_config(kube_config, kube_context, skip_ssl_verification)
    api_instance = client.VersionApi()
    try:
        api_response = api_instance.get_code()
        logger.debug(f"Api Server Version:  {api_response.git_version}")
        return api_response.git_version
    except Exception as e:  # pylint: disable=broad-except
        logger.warning("Unable to verify connectivity to the Kubernetes cluster.")
        raise ValidationError(f"Unable to verify connectivity to the Kubernetes cluster. {e}")


def create_folder(folder_name, time_stamp):
    error = ""
    # Fetching path to user directory to create the arc diagnostic folder
    home_dir = os.path.expanduser("~")
    filepath = os.path.join(home_dir, ".azure", folder_name)
    filepath_with_timestamp = os.path.join(filepath, time_stamp)
    try:

        # Creating Diagnostic folder and its subfolder with the given timestamp and cluster name to store all the logs
        try:
            os.mkdir(filepath)
        except FileExistsError:
            pass
        try:
            os.mkdir(filepath_with_timestamp)
        except FileExistsError:
            # Deleting the folder if present with the same timestamp to prevent overriding in the same folder and then
            #  creating it again
            shutil.rmtree(filepath_with_timestamp, ignore_errors=True)
            os.mkdir(filepath_with_timestamp)

        return filepath_with_timestamp, True, ""

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onexc=None)
            error = "No space left on device"
        else:
            error = f"Error while trying to create diagnostic logs folder. Exception: {str(e)}"

    # To handle any exception that may occur during the execution
    except Exception as e:
        error = f"Error while trying to create diagnostic logs folder. Exception: {str(e)}"

    return "", False, error


def create_sub_folder(parent_path, subfolder_name):
    if parent_path is None:
        return "", False, "parent_path is required."

    if subfolder_name is None:
        return "", False, "subfolder_name is required."

    error = ""
    filepath = os.path.join(parent_path, subfolder_name)
    try:
        os.mkdir(filepath)
        return filepath, True, ""
    except FileExistsError:
        return filepath, True, ""
    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            shutil.rmtree(filepath, ignore_errors=False, onexc=None)
            error = "No space left on device"
        else:
            error = f"Error while trying to create diagnostic logs folder. Exception: {str(e)}"

    # To handle any exception that may occur during the execution
    except Exception as e:
        error = f"Error while trying to create diagnostic logs folder. Exception: {str(e)}"

    return "", False, error


def patch_coredns(kube_client, coredns_configmap, coredns_deployment, new_filepath_with_timestamp,
                  custom_core_dns_configmap_exists, create_volume, create_volume_mount):
    import re

    if not create_volume and not create_volume_mount:
        return

    # create custom core dns config map
    if not custom_core_dns_configmap_exists:
        logger.info("coredns-custom configmap doesn't exist in namespace kube-system, create a new one")
        filepath = os.path.join(new_filepath_with_timestamp, "coredns-custom.yaml")
        with open(filepath, "w") as f:  # Opens file and casts as f
            f.write(EMPTY_CUSTOM_CORE_DNS)
        utils.create_from_yaml(kube_client, filepath, verbose=True)

    # update core dns config map.
    core_file_data = coredns_configmap.data.get('Corefile')
    lines = core_file_data.split("\n")
    has_import_custom_server = False
    for line in lines:
        if re.match(r'^\S*import custom/\*\.server$', line):
            has_import_custom_server = True
            break
    if not has_import_custom_server:
        core_file_data = rreplace(core_file_data, "\n", "\nimport custom/*.server\n", 1)
        coredns_configmap.data['Corefile'] = core_file_data
        update_configmap(CORE_DNS, KUBE_SYSTEM, kube_client, coredns_configmap)

    # update deployment
    if create_volume:
        logger.info(f"create volume {CUSTOM_CORE_DNS_VOLUME_NAME}")
        custom_coredns_volume = client.V1Volume(
            name=CUSTOM_CORE_DNS_VOLUME_NAME,
            config_map=client.V1ConfigMapVolumeSource(
                default_mode=420,
                name=CUSTOM_CORE_DNS,
                optional=True
            )
        )
        coredns_deployment.spec.template.spec.volumes.append(custom_coredns_volume)

    if create_volume_mount:
        logger.info(f"create volume mount {CUSTOM_CORE_DNS_VOLUME_NAME}")
        custom_coredns_volume_mount = client.V1VolumeMount(
            mount_path=CUSTOM_CORE_DNS_VOLUME_MOUNT_PATH,
            name=CUSTOM_CORE_DNS_VOLUME_NAME,
            read_only=True
        )
        coredns_deployment.spec.template.spec.containers[0].volume_mounts.append(custom_coredns_volume_mount)

    deployment = client.V1Deployment(
        spec=client.V1DeploymentSpec(
            selector=coredns_deployment.spec.selector,
            template=client.V1PodTemplateSpec(
                spec=client.V1PodSpec(
                    volumes=coredns_deployment.spec.template.spec.volumes,
                    containers=[client.V1Container(
                        name=coredns_deployment.spec.template.spec.containers[0].name,
                        volume_mounts=coredns_deployment.spec.template.spec.containers[0].volume_mounts
                    )]
                )
            )
        )
    )
    update_deployment(CORE_DNS, KUBE_SYSTEM, kube_client, deployment)


def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


def get_core_dns_deployment(kube_client, folder=None):
    response = get_and_save_deployment(CORE_DNS, KUBE_SYSTEM, kube_client, folder)
    if response is None:
        raise ValidationError("CoreDns deployment cannot be found in kube-system namespace")

    return response


def get_core_dns_configmap(kube_client, folder=None):
    response = get_and_save_configmap(CORE_DNS, KUBE_SYSTEM, kube_client, folder)
    if response is None:
        raise ValidationError("CoreDns Configmap cannot be found in kube-system namespace")

    return response


def backup_custom_core_dns_configmap(kube_client, folder=None):
    return get_and_save_configmap(CUSTOM_CORE_DNS, KUBE_SYSTEM, kube_client, folder)


def get_and_save_configmap(resource_name, resource_namespace, kube_client, folder=None):
    configmap = get_configmap(resource_name, resource_namespace, kube_client)
    if configmap is not None:
        if folder is not None:
            filepath = os.path.join(folder, f"configmap-{resource_name}.json")
            try:
                logger.info(f"Save ConfigMap '{resource_name}' in namespace '{resource_namespace}' to {filepath} ")
                with open(filepath, "w") as f:  # Opens file and casts as f
                    configmap_dict = json.loads(configmap.data)
                    f.write(json.dumps(configmap_dict, indent=2))
            except Exception as e:
                raise ValidationError(f"Failed to save file {filepath} with error '{str(e)}'")
        return kube_client.deserialize(configmap, client.models.v1_config_map.V1ConfigMap)

    logger.info(f"ConfigMap '{resource_name}' in namespace '{resource_namespace}' does not exist")
    return None


def get_and_save_deployment(resource_name, resource_namespace, kube_client, folder=None):
    deployment = get_deployment(resource_name, resource_namespace, kube_client)
    if deployment is not None:
        if folder is not None:
            filepath = os.path.join(folder, f"deployment-{resource_name}.json")
            try:
                logger.info(f"Save Deployment '{resource_name}' in namespace '{resource_namespace}' to {filepath} ")
                with open(filepath, "w") as f:  # Opens file and casts as f
                    deployment_dict = json.loads(deployment.data)
                    f.write(json.dumps(deployment_dict, indent=2))
            except Exception as e:
                raise ValidationError(f"Failed to save file {filepath} with error '{str(e)}'")

        return kube_client.deserialize(deployment, client.models.v1_deployment.V1Deployment)

    logger.info(f"Deployment '{resource_name}' in namespace '{resource_namespace}' does not exist")
    return None


def get_deployment(resource_name, resource_namespace, kube_client):
    validate_resource_name_and_resource_namespace_not_empty(resource_name, resource_namespace)

    try:
        logger.info(f"Get Deployment '{resource_name}' from namespace '{resource_namespace}'")
        apps_v1_api = client.AppsV1Api(kube_client)
        deployment = apps_v1_api.read_namespaced_deployment(name=resource_name, namespace=resource_namespace, pretty=True, _preload_content=False)
    except client.exceptions.ApiException as e:
        if e.status == 404:
            deployment = None
        else:
            raise e
    except Exception as e:
        raise ValidationError(f"other errors while getting deployment coredns in kube-system {str(e)}")

    return deployment


def update_deployment(resource_name, resource_namespace, kube_client, deployment):
    validate_resource_name_and_resource_namespace_not_empty(resource_name, resource_namespace)

    try:
        logger.info(f"Start to patch deployment {resource_name} in namespace {resource_namespace}")
        apps_v1_api = client.AppsV1Api(kube_client)
        apps_v1_api.patch_namespaced_deployment(name=resource_name, namespace=resource_namespace, body=deployment)
    except Exception as e:
        raise ValidationError(f"other errors while patching deployment coredns in kube-system {str(e)}")


def replace_deployment(resource_name, resource_namespace, kube_client, deployment):
    validate_resource_name_and_resource_namespace_not_empty(resource_name, resource_namespace)

    try:
        logger.info(f"Start to replace deployment {resource_name} in namespace {resource_namespace}")
        apps_v1_api = client.AppsV1Api(kube_client)
        apps_v1_api.replace_namespaced_deployment(name=resource_name, namespace=resource_namespace, body=deployment)
    except Exception as e:
        raise ValidationError(f"other errors while replacing deployment coredns in kube-system {str(e)}")


def get_configmap(resource_name, resource_namespace, kube_client):
    validate_resource_name_and_resource_namespace_not_empty(resource_name, resource_namespace)

    try:
        logger.info(f"Get ConfigMap '{resource_name}' from namespace '{resource_namespace}'")
        core_v1_api = client.api.core_v1_api.CoreV1Api(kube_client)
        config_map = core_v1_api.read_namespaced_config_map(name=resource_name, namespace=resource_namespace, pretty=True, _preload_content=False)
    except client.exceptions.ApiException as e:
        if e.status == 404:
            config_map = None
        else:
            raise e
    except Exception as e:
        raise ValidationError(f"other errors while getting config map coredns in kube-system {str(e)}")

    return config_map


def update_configmap(resource_name, resource_namespace, kube_client, config_map):
    validate_resource_name_and_resource_namespace_not_empty(resource_name, resource_namespace)

    try:
        logger.info(f"Start to update configmap {resource_name} in namespace {resource_namespace}")
        core_v1_api = client.api.core_v1_api.CoreV1Api(kube_client)
        core_v1_api.patch_namespaced_config_map(name=resource_name, namespace=resource_namespace, body=config_map)

    except Exception as e:
        raise CLIError(f"other errors while patching config map coredns in kube-system {str(e)}")


def replace_configmap(resource_name, resource_namespace, kube_client, config_map):
    validate_resource_name_and_resource_namespace_not_empty(resource_name, resource_namespace)

    try:
        logger.info(f"Start to replace configmap {resource_name} in namespace {resource_namespace}")
        core_v1_api = client.api.core_v1_api.CoreV1Api(kube_client)
        core_v1_api.replace_namespaced_config_map(name=resource_name, namespace=resource_namespace, body=config_map)

    except Exception as e:
        raise CLIError(f"other errors while replacing config map coredns in kube-system {str(e)}")


def delete_configmap(resource_name, resource_namespace, kube_client):
    validate_resource_name_and_resource_namespace_not_empty(resource_name, resource_namespace)

    try:
        logger.info(f"Start to delete configmap {resource_name} in namespace {resource_namespace}")
        core_v1_api = client.api.core_v1_api.CoreV1Api(kube_client)
        core_v1_api.delete_namespaced_config_map(name=resource_name, namespace=resource_namespace)

    except client.rest.ApiException as e:
        if e.status == HTTPStatus.NOT_FOUND:
            logger.info(f"Configmap {resource_name} in namespace {resource_namespace} has been deleted")
            return
        raise CLIError(f"other ApiException while deleting config map coredns in kube-system {str(e)}")

    except Exception as e:
        raise CLIError(f"other errors while deleting config map coredns in kube-system {str(e)}")


def validate_resource_name_and_resource_namespace_not_empty(resource_name, resource_namespace):
    if resource_name is None or len(resource_name) == 0:
        raise InvalidArgumentValueError("Arg resource_name should not be None or Empty")
    if resource_namespace is None or len(resource_namespace) == 0:
        raise InvalidArgumentValueError("Arg resource_namespace should not be None or Empty")
