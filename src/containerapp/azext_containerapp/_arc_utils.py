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
                         CUSTOM_CORE_DNS, CORE_DNS, KUBE_SYSTEM, EMPTY_CUSTOM_CORE_DNS, OPENSHIFT_DNS)

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
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False)
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
            shutil.rmtree(filepath, ignore_errors=False)
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


def create_or_update_deployment(name, namespace, kube_client, deployment):
    validate_resource_name_and_resource_namespace_not_empty(name, namespace)

    try:
        logger.info(f"Start to create deployment {name} in namespace {namespace}")
        apps_v1_api = client.AppsV1Api(kube_client)
        apps_v1_api.create_namespaced_deployment(namespace=namespace, body=deployment)
    except client.exceptions.ApiException as e:
        if e.status == 409:
            logger.warning(f"Deployment '{name}' already exists, replacing it")
            apps_v1_api.replace_namespaced_deployment(name=name, namespace=namespace, body=deployment)
        else:
            raise CLIError(f"Failed to create or replace Deployment'{name}': {str(e)}")


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


def create_or_update_configmap(name, namespace, kube_client, configmap):
    validate_resource_name_and_resource_namespace_not_empty(name, namespace)

    try:
        logger.info(f"Start to create configmap {name} in namespace {namespace}")
        core_v1_api = client.CoreV1Api(kube_client)
        core_v1_api.create_namespaced_config_map(namespace=namespace, body=configmap)
    except client.exceptions.ApiException as e:
        if e.status == 409:
            logger.warning(f"Configmap '{name}' already exists, replacing it")
            core_v1_api.replace_namespaced_config_map(name=name, namespace=namespace, body=configmap)
        else:
            raise CLIError(f"Failed to create or replace ConfigMap '{name}': {str(e)}")


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


def create_or_replace_cluster_role(rbac_api, role_name, role):
    try:
        logger.info(f"Creating new ClusterRole '{role_name}'")
        rbac_api.create_cluster_role(body=role)
    except client.exceptions.ApiException as e:
        if e.status == 409:
            logger.info(f"ClusterRole '{role_name}' already exists, replacing it")
            rbac_api.replace_cluster_role(name=role_name, body=role)
        else:
            raise CLIError(f"Failed to create or replace ClusterRole '{role_name}': {str(e)}")


def create_or_replace_cluster_rolebinding(rbac_api, rolebinding_name, rolebinding):
    try:
        logger.info(f"Creating new ClusterRolebinding '{rolebinding_name}'")
        rbac_api.create_cluster_role_binding(body=rolebinding)
    except client.exceptions.ApiException as e:
        if e.status == 409:
            logger.info(f"ClusterRole '{rolebinding_name}' already exists, replacing it")
            rbac_api.replace_cluster_role_binding(name=rolebinding_name, body=rolebinding)
        else:
            raise CLIError(f"Failed to create or replace ClusterRole '{rolebinding_name}': {str(e)}")


def create_openshift_custom_coredns_resources(kube_client, namespace=OPENSHIFT_DNS):
    try:
        logger.info("Creating custom CoreDNS resources in OpenShift")
        core_v1_api = client.CoreV1Api(kube_client)
        rbac_api = client.RbacAuthorizationV1Api(kube_client)

        # 1. Create ClusterRole
        cluster_role = client.V1ClusterRole(
            metadata=client.V1ObjectMeta(
                name=CUSTOM_CORE_DNS
            ),
            rules=[
                client.V1PolicyRule(
                    api_groups=[""],
                    resources=["services", "endpoints", "pods", "namespaces"],
                    verbs=["list", "watch"]
                ),
                client.V1PolicyRule(
                    api_groups=["discovery.k8s.io"],
                    resources=["endpointslices"],
                    verbs=["list", "watch"]
                )
            ]
        )
        create_or_replace_cluster_role(rbac_api, CUSTOM_CORE_DNS, cluster_role)

        # 2. Create ClusterRoleBinding
        cluster_role_binding = client.V1ClusterRoleBinding(
            metadata=client.V1ObjectMeta(
                name=CUSTOM_CORE_DNS
            ),
            role_ref=client.V1RoleRef(
                api_group="rbac.authorization.k8s.io",
                kind="ClusterRole",
                name=CUSTOM_CORE_DNS
            ),
            subjects=[
                client.V1Subject(
                    kind="ServiceAccount",
                    name="default",
                    namespace=namespace
                )
            ]
        )
        create_or_replace_cluster_rolebinding(rbac_api, CUSTOM_CORE_DNS, cluster_role_binding)

        # 3. Create ConfigMap
        existing_config_map = core_v1_api.read_namespaced_config_map(name=CUSTOM_CORE_DNS, namespace=KUBE_SYSTEM)
        corefile_data = existing_config_map.data.get("k4apps-default.io.server") or existing_config_map.data.get("Corefile")
        if not corefile_data:
            raise ValidationError(F"Neither 'k4apps-default.io.server' nor 'Corefile' key found in the {CUSTOM_CORE_DNS} ConfigMap in {KUBE_SYSTEM} namespace.")

        config_map = client.V1ConfigMap(
            metadata=client.V1ObjectMeta(
                name=CUSTOM_CORE_DNS,
                namespace=namespace
            ),
            data={"Corefile": corefile_data}
        )

        create_or_update_configmap(name=CUSTOM_CORE_DNS, namespace=namespace, kube_client=kube_client, configmap=config_map)
        logger.info("Custom CoreDNS ConfigMap created successfully")

        # 4. Create Deployment
        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(
                name=CUSTOM_CORE_DNS,
                namespace=namespace
            ),
            spec=client.V1DeploymentSpec(
                replicas=1,
                selector=client.V1LabelSelector(
                    match_labels={"app": CUSTOM_CORE_DNS}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={"app": CUSTOM_CORE_DNS}
                    ),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name="coredns",
                                image="coredns/coredns:latest",
                                args=["-conf", "/etc/coredns/Corefile"],
                                volume_mounts=[
                                    client.V1VolumeMount(
                                        name="config-volume",
                                        mount_path="/etc/coredns"
                                    )
                                ]
                            )
                        ],
                        volumes=[
                            client.V1Volume(
                                name="config-volume",
                                config_map=client.V1ConfigMapVolumeSource(
                                    name=CUSTOM_CORE_DNS
                                )
                            )
                        ]
                    )
                )
            )
        )
        create_or_update_deployment(name=CUSTOM_CORE_DNS, namespace=namespace, kube_client=kube_client, deployment=deployment)
        logger.info("Custom CoreDNS Deployment created successfully")

        # 5 Create Service
        service = client.V1Service(
            metadata=client.V1ObjectMeta(
                name=CUSTOM_CORE_DNS,
                namespace=namespace
            ),
            spec=client.V1ServiceSpec(
                selector={"app": CUSTOM_CORE_DNS},
                ports=[
                    client.V1ServicePort(
                        protocol="UDP",
                        port=53,
                        target_port=53
                    )
                ]
            )
        )
        core_v1_api.create_namespaced_service(namespace=namespace, body=service)
        logger.info("Custom CoreDNS Service created successfully")

    except client.exceptions.ApiException as e:
        if e.status == 409:
            logger.warning("Custom CoreDNS resources already exist")
        else:
            raise CLIError(f"Failed to create custom CoreDNS resources: {str(e)}")
    except Exception as e:
        raise CLIError(f"An error occurred while creating custom CoreDNS resources: {str(e)}")


def patch_openshift_dns_operator(kube_client, domain, original_folder=None):
    try:
        logger.info("Patching OpenShift DNS operator to add custom resolver")

        # Fetch the existing DNS operator configuration
        custom_objects_api = client.CustomObjectsApi(kube_client)

        dns_operator_config = get_and_save_openshift_dns_operator_config(kube_client, original_folder)

        coredns_service = client.CoreV1Api(kube_client).read_namespaced_service(name=CUSTOM_CORE_DNS, namespace=OPENSHIFT_DNS)

        # Add the custom resolver to the DNS operator configuration
        servers = dns_operator_config.get("spec", {}).get("servers", [])
        custom_resolver = {
            "name": CUSTOM_CORE_DNS,
            "zones": [domain, f"internal.{domain}"],
            "forwardPlugin": {
                "upstreams": [coredns_service.spec.cluster_ip],
            }
        }

        # Check if the custom resolver already exists
        if not any(server.get("name") == CUSTOM_CORE_DNS for server in servers):
            servers.append(custom_resolver)
            dns_operator_config["spec"]["servers"] = servers

            # Update the DNS operator configuration
            custom_objects_api.patch_cluster_custom_object(
                group="operator.openshift.io",
                version="v1",
                plural="dnses",
                name="default",
                body=dns_operator_config
            )
            logger.info("Successfully patched OpenShift DNS operator with custom resolver")
        else:
            logger.info("Custom resolver already exists in the DNS operator configuration")

    except client.exceptions.ApiException as e:
        raise CLIError(f"Failed to patch DNS operator: {str(e)}")
    except Exception as e:
        raise CLIError(f"An error occurred while patching DNS operator: {str(e)}")


def extract_domain_from_configmap(kube_client, resource_name=CUSTOM_CORE_DNS, namespace=KUBE_SYSTEM):
    import re

    try:
        core_v1_api = client.CoreV1Api(kube_client)
        configmap = core_v1_api.read_namespaced_config_map(name=CUSTOM_CORE_DNS, namespace=KUBE_SYSTEM)
        if configmap is None:
            raise ResourceNotFoundError(f"ConfigMap '{resource_name}' not found in namespace '{namespace}'.")

        corefile = configmap.data.get("k4apps-default.io.server")
        if not corefile:
            raise ValidationError("'k4apps-default.io.server' key found in the coredns-custom ConfigMap in kube-system namespace.")

        # Extract the domain (excluding 'dapr')
        for line in corefile.splitlines():
            match = re.match(r'^\s*([a-zA-Z0-9\-\.]+):53\s*{', line)
            if match and match.group(1) != "dapr":
                return match.group(1)

        raise ValidationError("No valid domain found in CoreDNS configmap data.")
    except Exception as e:
        logger.error(f"Failed to extract domain from configmap: {str(e)}")
        return None


def get_and_save_openshift_dns_operator_config(kube_client, folder=None):
    try:
        custom_objects_api = client.CustomObjectsApi(kube_client)
        dns_operator_config = custom_objects_api.get_cluster_custom_object(
            group="operator.openshift.io",
            version="v1",
            plural="dnses",
            name="default"
        )

        if folder is not None:
            filepath = os.path.join(folder, "openshift-dns-operator-config.json")
            with open(filepath, "w") as f:
                f.write(json.dumps(dns_operator_config, indent=2))
            logger.info(f"OpenShift DNS operator configuration saved to {filepath}")

        return dns_operator_config
    except Exception as e:
        raise ValidationError(f"Failed to retrieve OpenShift DNS operator configuration: {str(e)}")


def restart_openshift_dns_daemonset(kube_client):
    try:
        # Get the DaemonSet
        apps_v1_api = client.AppsV1Api(kube_client)
        daemonset_name = "dns-default"

        try:
            apps_v1_api.read_namespaced_daemon_set(
                name=daemonset_name,
                namespace=OPENSHIFT_DNS
            )
        except client.exceptions.ApiException as e:
            if e.status == 404:
                logger.warning(f"DaemonSet '{daemonset_name}' not found in namespace '{OPENSHIFT_DNS}'")
                return
            else:
                raise

        logger.info(f"Restarting DaemonSet '{daemonset_name}' in namespace '{OPENSHIFT_DNS}'...")

        try:
            response = input(f"The DNS DaemonSet in namespace '{OPENSHIFT_DNS}' needs to be restarted. Are you sure you want to proceed? (y/n): ")
            confirmed = response.lower() in ['y', 'yes']
        except (EOFError, KeyboardInterrupt):
            confirmed = False

        if not confirmed:
            logger.info(f"The restart of daemonset was cancelled by the user. Please manually restart the daemonset by running 'kubectl rollout restart daemonset {daemonset_name} -n {OPENSHIFT_DNS}'")
            return

        # Rollout restart - this is exactly what kubectl rollout restart does
        import datetime

        restart_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        # The kubectl rollout restart command internally does this exact patch
        patch_body = {
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "kubectl.kubernetes.io/restartedAt": restart_time
                        }
                    }
                }
            }
        }

        # Patch the daemon set to trigger a restart
        apps_v1_api.patch_namespaced_daemon_set(
            name=daemonset_name,
            namespace=OPENSHIFT_DNS,
            body=patch_body
        )

        logger.info(f"Successfully initiated restart of DaemonSet '{daemonset_name}'. Pods will be recreated automatically.")

    except client.exceptions.ApiException as e:
        if e.status == 404:
            logger.warning(f"DaemonSet '{daemonset_name}' not found in namespace '{OPENSHIFT_DNS}'")
        else:
            raise CLIError(f"Failed to restart DaemonSet: {str(e)}")
    except Exception as e:
        raise CLIError(f"An error occurred while restarting DaemonSet: {str(e)}")
