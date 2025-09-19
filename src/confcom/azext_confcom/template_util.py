# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
import copy
import json
import re
import tarfile
from hashlib import sha256
from typing import Any, Dict, List, Tuple

import deepdiff
import docker
import yaml
from azext_confcom import config, os_util
from azext_confcom.errors import eprint
from knack.log import get_logger

logger = get_logger(__name__)

# TODO: these can be optimized to not have so many groups in the single match
# make this global so it can be used in multiple functions
PARAMETER_AND_VARIABLE_REGEX = r"\[(?:parameters|variables)\(\s*'([^\.\/]+?)'\s*\)\]"
WHOLE_PARAMETER_AND_VARIABLE = r"(\s*\[\s*(parameters|variables))(\(\s*'([^\.\/]+?)'\s*\)\])"
SVN_PATTERN = r'svn\s*:=\s*"(\d+)"'
NAMESPACE_PATTERN = r'package\s+([a-zA-Z_][a-zA-Z0-9_]*)'


class DockerClient:
    _client = None

    def __enter__(self) -> docker.DockerClient:
        return self.get_client()

    def get_client(self) -> docker.DockerClient:
        if not self._client:
            self._client = docker.from_env()
        return self._client

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._client:
            self._client.close()


def case_insensitive_dict_get(dictionary, search_key, default_value=None) -> Any:
    if not isinstance(dictionary, dict):
        return None
    # if the cases happen to match, immediately return .get() result
    possible_match = dictionary.get(search_key)
    if possible_match:
        return possible_match
    # case insensitive get and return reference instead of just value
    for key in dictionary.keys():
        if key.lower() == search_key.lower():
            return dictionary[key]
    return default_value


def deep_dict_update(source: dict, destination: dict):
    """
    https://stackoverflow.com/questions/20656135/python-deep-merge-dictionary-data
    """
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            if node is None:
                destination[key] = {}
                node = destination[key]
            deep_dict_update(value, node)
        else:
            destination[key] = value

    return destination


def image_has_hash(image: str) -> bool:
    return "@sha256:" in image


def get_image_name(image: str) -> str:
    if image_has_hash(image):
        return image.split("@")[0]
    return image.split(":")[0]


def get_image_info(progress, message_queue, tar_mapping, image):
    image_info = None
    raw_image = None
    tar = False
    if not image.base:
        eprint("Image name cannot be empty")
    image_name = f"{image.base}:{image.tag}"

    # only try to grab the info locally if that's absolutely what
    # we want to do
    if tar_mapping:
        if image_has_hash(image_name):
            progress.close()
            eprint(
                f"The image name: {image_name} cannot have the digest present to use a tarball as the image source"
            )
        tar_location = get_tar_location_from_mapping(tar_mapping, image_name)
        # if we have a tar location, we can try to get the image info
        if tar_location:
            with tarfile.open(tar_location) as tar_file:
                # get all the info out of the tarfile
                try:
                    logger.info("using backwards compatibility tar file")
                    image_info = os_util.map_image_from_tar_backwards_compatibility(
                        image_name, tar_file, tar_location
                    )
                except IndexError:
                    logger.info("using docker formatted tar file")
                    image_info = os_util.map_image_from_tar(
                        image_name, tar_file, tar_location
                    )
                except (KeyError, AttributeError):
                    # manifest.json not found
                    logger.info("using OCI tar file")
                    image_info = os_util.map_image_from_tar_oci_layout_v1(image_name, tar_file, tar_location)
                if image_info is not None:
                    tar = True
                    message_queue.append(f"{image_name} read from local tar file")

    # see if we have the image locally so we can have a
    # 'clean-room'
    if not image_info:
        try:
            client = DockerClient().get_client()
            raw_image = client.images.get(image_name)
            image_info = raw_image.attrs.get("Config")
            message_queue.append(
                f"Using local version of {image_name}. It may differ from the remote image"
            )
        except docker.errors.ImageNotFound:
            message_queue.append(
                f"{image_name} is not found locally. Attempting to pull from remote..."
            )
        except docker.errors.DockerException:
            progress.close()
            eprint(
                f"{image_name} is not found in tar file and Docker is not running."
            )

    if not image_info:
        try:
            # pull image to local daemon (if not in local
            # daemon)
            if not raw_image:
                raw_image = client.images.pull(image_name)
                image_info = raw_image.attrs.get("Config")
        except (docker.errors.ImageNotFound, docker.errors.NotFound):
            progress.close()
            eprint(
                f"{image_name} is not found remotely. "
                + "Please check to make sure the image and repository exist"
            )
    # warn if the image is the "latest"
    if image.tag == "latest":
        message_queue.append(
            'Using image tag "latest" is not recommended'
        )

    progress.update()

    # error out if we're attempting to build for an unsupported
    # architecture
    if (
        raw_image and
        raw_image.attrs.get(
            config.ACI_FIELD_CONTAINERS_ARCHITECTURE_KEY
        ) !=
        config.ACI_FIELD_CONTAINERS_ARCHITECTURE_VALUE
    ) or (
        not raw_image and image_info.get(config.ACI_FIELD_CONTAINERS_ARCHITECTURE_KEY) !=
        config.ACI_FIELD_CONTAINERS_ARCHITECTURE_VALUE
    ):
        progress.close()
        eprint((
            f"{image_name} is attempting to build for unsupported architecture: "
            f"{raw_image.attrs.get(config.ACI_FIELD_CONTAINERS_ARCHITECTURE_KEY)}. "
            f"Only {config.ACI_FIELD_CONTAINERS_ARCHITECTURE_VALUE} is supported by Confidential ACI"
        ))

    return image_info, tar


def get_tar_location_from_mapping(tar_mapping: Any, image_name: str) -> str:
    # tar location can either be a dict mapping images to paths to tarfiles or a string to the tarfile
    tar_location = None
    if isinstance(tar_mapping, dict):
        # make it so the user can either put "latest" or infer it
        if image_name.endswith(":latest"):
            alternate_key = image_name.split(":")[0]
        else:
            alternate_key = None
        tar_location = tar_mapping.get(image_name) or tar_mapping.get(
            alternate_key
        )
    else:
        tar_location = tar_mapping
    # for mixed mode, the image doesn't have to be in the tarfile
    # so this can return None
    return tar_location


def process_env_vars_from_template(params: dict,
                                   vars_dict: dict,
                                   image_properties: dict,
                                   approve_wildcards: bool) -> List[Dict[str, str]]:
    env_vars = []
    # add in the env vars from the template
    template_env_vars = case_insensitive_dict_get(
        image_properties, config.ACI_FIELD_TEMPLATE_ENVS
    ) or []

    if template_env_vars:
        for env_var in template_env_vars:
            name = case_insensitive_dict_get(env_var, "name")
            value = case_insensitive_dict_get(env_var, "value")
            # "value" is allowed to be empty string
            if value is None:
                value = case_insensitive_dict_get(env_var, "secureValue")

            if not name:
                eprint(
                    f"Environment variable with value: {value} is missing a name"
                )

            if value is not None:
                param_check = find_value_in_params_and_vars(
                    params, vars_dict, value, ignore_undefined_parameters=True)
                param_name = re.findall(PARAMETER_AND_VARIABLE_REGEX, value)

                if param_name and param_check == value:
                    response = approve_wildcards or input(
                        f'Create a wildcard policy for the environment variable {name} (y/n): ')
                    if approve_wildcards or response.lower() == 'y':
                        logger.info('Creating a wildcard policy for the environment variable %s', name)
                        env_vars.append({
                            config.ACI_FIELD_CONTAINERS_ENVS_NAME: name,
                            config.ACI_FIELD_CONTAINERS_ENVS_VALUE: ".*",
                            config.ACI_FIELD_CONTAINERS_ENVS_STRATEGY: "re2",
                        })
                elif (
                    re.match(config.ACI_FIELD_TEMPLATE_SPECIAL_ENV_VAR_REGEX_VALUE, value) and
                    name == config.ACI_FIELD_TEMPLATE_SPECIAL_ENV_VAR_REGEX_NAME
                ):
                    # special case for adding THIM endpoint to container
                    env_vars.append({
                        config.ACI_FIELD_CONTAINERS_ENVS_NAME: config.ACI_FIELD_TEMPLATE_SPECIAL_ENV_VAR_REGEX_NAME,
                        config.ACI_FIELD_CONTAINERS_ENVS_VALUE: ".*",
                        config.ACI_FIELD_CONTAINERS_ENVS_STRATEGY: "re2",
                    })
                else:
                    env_vars.append({
                        config.ACI_FIELD_CONTAINERS_ENVS_NAME: name,
                        config.ACI_FIELD_CONTAINERS_ENVS_VALUE: value,
                        config.ACI_FIELD_CONTAINERS_ENVS_STRATEGY: "string",
                    })
            else:
                eprint(f'Environment variable {name} does not have a value. Please check the template file.')

    return env_vars


# pylint: disable=too-many-branches
def process_env_vars_from_yaml(container, config_maps, secrets, approve_wildcards=False):
    # https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/pod-v1/#environment-variables-1
    output_env_vars = []
    wildcarded_resource_names = []
    not_wildcarded_resource_names = []

    # convert lists of config_maps and secrets to dictionaries for quick lookup
    config_maps_lookup = {cm['metadata']['name']: cm for cm in config_maps}
    secrets_lookup = {sec['metadata']['name']: sec for sec in secrets}

    for var in container.get("env", []):
        name = var['name']

        if 'value' in var:
            # some special values that get updated by VN2. This allows those to be wildcarded
            if re.match(config.VIRTUAL_NODE_YAML_SPECIAL_ENV_VAR_REGEX, var['value']):
                output_env_vars.append({
                    config.ACI_FIELD_CONTAINERS_ENVS_NAME: name,
                    config.ACI_FIELD_CONTAINERS_ENVS_VALUE: ".*",
                    config.ACI_FIELD_CONTAINERS_ENVS_STRATEGY: "re2",
                })
            else:
                output_env_vars.append({
                    config.ACI_FIELD_CONTAINERS_ENVS_NAME: name,
                    config.ACI_FIELD_CONTAINERS_ENVS_VALUE: var['value'],
                    config.ACI_FIELD_CONTAINERS_ENVS_STRATEGY: "string",
                })
        elif 'valueFrom' in var:
            value = None
            # 'valueFrom' to get the val from a config map / secret
            ref = var['valueFrom']
            if 'configMapKeyRef' in ref:
                value = get_value_from_configmap(
                    ref=ref['configMapKeyRef'],
                    config_maps_lookup=config_maps_lookup)
                configmap_name = ref['configMapKeyRef']['name']
                if value is None and configmap_name not in not_wildcarded_resource_names:

                    response = (approve_wildcards or
                                configmap_name in wildcarded_resource_names or
                                input((
                                    "Would you like to use a wildcard value for ConfigMap "
                                    f"{configmap_name}? (y/n): "
                                ))
                                )

                    if (
                        approve_wildcards or
                        configmap_name in wildcarded_resource_names or
                            response.lower() == 'y'
                    ):
                        wildcarded_resource_names.append(configmap_name)
                        output_env_vars.append({
                            config.ACI_FIELD_CONTAINERS_ENVS_NAME: name,
                            config.ACI_FIELD_CONTAINERS_ENVS_VALUE: ".*",
                            config.ACI_FIELD_CONTAINERS_ENVS_STRATEGY: "re2",
                        })
                    else:
                        not_wildcarded_resource_names.append(configmap_name)
                        output_env_vars.append({
                            config.ACI_FIELD_CONTAINERS_ENVS_NAME: name,
                            config.ACI_FIELD_CONTAINERS_ENVS_VALUE: "",
                            config.ACI_FIELD_CONTAINERS_ENVS_STRATEGY: "string",
                        })
                elif configmap_name in not_wildcarded_resource_names:
                    output_env_vars.append({
                        config.ACI_FIELD_CONTAINERS_ENVS_NAME: name,
                        config.ACI_FIELD_CONTAINERS_ENVS_VALUE: "",
                        config.ACI_FIELD_CONTAINERS_ENVS_STRATEGY: "string",
                    })
                else:
                    output_env_vars.append({
                        config.ACI_FIELD_CONTAINERS_ENVS_NAME: name,
                        config.ACI_FIELD_CONTAINERS_ENVS_VALUE: value,
                        config.ACI_FIELD_CONTAINERS_ENVS_STRATEGY: "string",
                    })

            elif 'secretKeyRef' in ref:
                value = get_value_from_secret(
                    ref=ref['secretKeyRef'],
                    secrets_lookup=secrets_lookup)
                secret_name = ref['secretKeyRef']['name']

                if value is None and secret_name not in not_wildcarded_resource_names:
                    response = (approve_wildcards or
                                secret_name in wildcarded_resource_names or
                                input((
                                    "Would you like to use a wildcard value for Secret "
                                    f"{secret_name}? (y/n): "
                                )))

                    if (
                            approve_wildcards or
                            secret_name in wildcarded_resource_names or
                            response.lower() == 'y'
                    ):
                        wildcarded_resource_names.append(secret_name)
                        output_env_vars.append({
                            config.ACI_FIELD_CONTAINERS_ENVS_NAME: name,
                            config.ACI_FIELD_CONTAINERS_ENVS_VALUE: ".*",
                            config.ACI_FIELD_CONTAINERS_ENVS_STRATEGY: "re2",
                        })
                    else:
                        eprint((
                            f"Secret {name} needs a value. "
                            "Either attach the Secret resource "
                            "to the yaml file or use a wildcard."
                        ))

                elif secret_name in not_wildcarded_resource_names:
                    output_env_vars.append({
                        config.ACI_FIELD_CONTAINERS_ENVS_NAME: name,
                        config.ACI_FIELD_CONTAINERS_ENVS_VALUE: "",
                        config.ACI_FIELD_CONTAINERS_ENVS_STRATEGY: "string",
                    })
                else:
                    output_env_vars.append({
                        config.ACI_FIELD_CONTAINERS_ENVS_NAME: name,
                        config.ACI_FIELD_CONTAINERS_ENVS_VALUE: value,
                        config.ACI_FIELD_CONTAINERS_ENVS_STRATEGY: "string",
                    })
            elif 'fieldRef' in ref:
                # https://kubernetes.io/docs/tasks/inject-data-application/environment-variable-expose-pod-information/#use-pod-fields-as-values-for-environment-variables
                field_path = ref.get('fieldRef').get('fieldPath')

                if not field_path:
                    continue

                output_env_vars.append({
                    config.ACI_FIELD_CONTAINERS_ENVS_NAME: name,
                    config.ACI_FIELD_CONTAINERS_ENVS_VALUE: ".*",
                    config.ACI_FIELD_CONTAINERS_ENVS_STRATEGY: "re2",
                })
            elif 'resourceFieldRef' in ref:
                # https://kubernetes.io/docs/tasks/inject-data-application/environment-variable-expose-pod-information/#use-container-fields-as-values-for-environment-variables
                container_name = ref.get('resourceFieldRef').get('containerName')

                if container_name != container.get('name'):
                    eprint(("Container names other than the current "
                           f"container are not currently supported: {container_name}"))
                resource = ref.get('resourceFieldRef').get('resource')
                request_or_limit, resource_type = resource.split('.')

                resources = container.get(config.VIRTUAL_NODE_YAML_RESOURCES)
                if not resources:
                    continue
                # get the resource field
                resource_field = resources.get(request_or_limit)
                if not resource_field:
                    continue
                # get the value of the resource field
                value = resource_field.get(resource_type)
                if not value:
                    continue

                output_env_vars.append({
                    config.ACI_FIELD_CONTAINERS_ENVS_NAME: name,
                    config.ACI_FIELD_CONTAINERS_ENVS_VALUE: value,
                    config.ACI_FIELD_CONTAINERS_ENVS_STRATEGY: "string",
                })
    return output_env_vars


def get_value_from_configmap(ref, config_maps_lookup):
    """
    Retrieve a value from a ConfigMap using the reference.
    """
    normal_data = binary_data = None
    config_map = config_maps_lookup.get(ref['name'])
    if config_map:
        normal_data = config_map.get('data', {}).get(ref['key'])
        if not normal_data:
            binary_data = base64.b64decode(config_map.get('binaryData', {}).get(ref['key'])).decode('utf-8')
        return normal_data or binary_data
    return None


def get_value_from_secret(ref, secrets_lookup):
    """
    Retrieve a value from a Secret using the reference.
    """
    secret = secrets_lookup.get(ref['name'])
    if secret:
        return base64.b64decode(
            secret.get('data', {}).get(ref['key']) or ""
        ).decode('utf-8') or secret.get('stringData', {}).get(ref['key'])
    return None


def convert_to_pod_spec(yaml_dict: dict):
    results = convert_to_pod_spec_helper(yaml_dict)
    return add_kind_to_pod_spec(results) if results else {}


def add_kind_to_pod_spec(pod_spec: dict):
    pod_spec["kind"] = "Pod"
    pod_spec["apiVersion"] = "v1"
    return pod_spec


def convert_to_pod_spec_helper(pod_dict):
    possible_keys = ["spec", "template", "jobTemplate"]

    if "spec" in pod_dict and "containers" in pod_dict["spec"]:
        return pod_dict
    for key in possible_keys:
        if key in pod_dict:
            return convert_to_pod_spec_helper(pod_dict[key])
    return {}


def get_volume_claim_templates(pod_spec: dict) -> List[dict]:
    volume_claim_templates = []
    if "spec" in pod_spec:
        spec = pod_spec["spec"]
        if "volumeClaimTemplates" in spec:
            return spec["volumeClaimTemplates"]
    return volume_claim_templates


def filter_non_pod_resources(resources: List[dict]) -> List[dict]:
    """
    Filter out non-pod spawning resources from a list of resources.
    """
    important_resource_names = ["Pod", "Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob", "ReplicaSet"]
    return [resource for resource in resources if resource and resource.get("kind") in important_resource_names]


def process_env_vars_from_config(container) -> List[Dict[str, str]]:
    env_vars = []
    # add in the env vars from the template
    template_env_vars = case_insensitive_dict_get(
        container, config.ACI_FIELD_TEMPLATE_ENVS
    ) or []
    for env_var in template_env_vars:
        name = case_insensitive_dict_get(env_var, "name")
        secure_value = case_insensitive_dict_get(env_var, "secureValue")
        is_secure = bool(secure_value)
        value = case_insensitive_dict_get(env_var, "value") or secure_value or ""

        if not name and not is_secure:
            eprint(
                f"Environment variable with value: {value} is missing a name"
            )
        elif not name and is_secure:
            eprint(
                "Environment variable with secure value is missing a name"
            )

        env_vars.append({
            config.ACI_FIELD_CONTAINERS_ENVS_NAME: name,
            config.ACI_FIELD_CONTAINERS_ENVS_VALUE: value,
            config.ACI_FIELD_CONTAINERS_ENVS_STRATEGY:
                env_var.get("strategy", "re2" if (case_insensitive_dict_get(env_var, "regex")) else "string"),
        })

    return env_vars


def process_fragment_imports(rego_imports) -> None:
    for rego_import in rego_imports:
        if not rego_import:
            continue
        feed = case_insensitive_dict_get(
            rego_import, config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_FEED
        )
        if not isinstance(feed, str):
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                + f'["{config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_FEED}"] '
                + "can only be a string value."
            )

        iss = case_insensitive_dict_get(
            rego_import, config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_ISSUER
        )
        if not isinstance(iss, str):
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                + f'["{config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_ISSUER}"] '
                + "can only be a string value."
            )

        minimum_svn = case_insensitive_dict_get(
            rego_import, config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_MINIMUM_SVN
        )

        if not minimum_svn or not isinstance(minimum_svn, str) or not minimum_svn.isdigit():
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                + f'["{config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_MINIMUM_SVN}"] '
                + "can only be a string with an integer value."
            )

        includes = case_insensitive_dict_get(
            rego_import, config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_INCLUDES
        )
        if not isinstance(includes, list):
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                + f'["{config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_INCLUDES}"] '
                + "can only be a list value."
            )

    return rego_imports


def process_standalone_fragments(standalone_fragments: List[str]) -> Tuple[List[str], List[str]]:
    fragment_contents = []
    feeds = []

    for fragment in standalone_fragments:
        feed = case_insensitive_dict_get(
            fragment, config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_FEED
        )
        if not isinstance(feed, str):
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                + f'["{config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_FEED}"] '
                + "can only be a string value."
            )

        filename = case_insensitive_dict_get(
            fragment, config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_FILE
        )
        if not isinstance(filename, str):
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                + f'["{config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_FILE}"] '
                + "can only be a string value."
            )

        with open(filename, "r", encoding="utf-8") as file:
            text = file.read()

        fragment_contents.append(text)
        feeds.append(feed)

    return fragment_contents, feeds


def process_mounts(image_properties: dict, volumes: List[dict]) -> List[Dict[str, str]]:
    mount_source_table_keys = config.MOUNT_SOURCE_TABLE.keys()
    # initialize empty array of mounts
    mounts = []
    # get the mount types from the mounts section of the ARM template
    volume_mounts = (
        case_insensitive_dict_get(
            image_properties, config.ACI_FIELD_TEMPLATE_VOLUME_MOUNTS
        )
        or []
    )

    if volume_mounts and not isinstance(volume_mounts, list):
        # parameter definition is in parameter file but not arm
        # template
        eprint(
            f'Parameter ["{config.ACI_FIELD_TEMPLATE_VOLUME_MOUNTS}"] must be a list'
        )

    # get list of mount information based on mount name
    for mount in volume_mounts:
        mount_name = case_insensitive_dict_get(mount, "name")

        filtered_volume = [
            x
            for x in volumes
            if case_insensitive_dict_get(x, "name") == mount_name
        ]

        if not filtered_volume:
            eprint(f'Volume ["{mount_name}"] not found in volume declarations')
        else:
            filtered_volume = filtered_volume[0]

        # figure out mount type
        mount_type_value = ""
        for i in filtered_volume.keys():
            if i in mount_source_table_keys:
                mount_type_value = i

        mounts.append(
            {
                config.ACI_FIELD_CONTAINERS_MOUNTS_TYPE: mount_type_value,
                config.ACI_FIELD_CONTAINERS_MOUNTS_PATH: case_insensitive_dict_get(
                    mount, config.ACI_FIELD_TEMPLATE_MOUNTS_PATH
                ),
                config.ACI_FIELD_CONTAINERS_MOUNTS_READONLY: case_insensitive_dict_get(
                    mount, config.ACI_FIELD_TEMPLATE_MOUNTS_READONLY
                ),
            }
        )
    return mounts


def process_configmap(image_properties: dict) -> List[Dict[str, str]]:
    # return empty list if we don't have a configmap
    if not case_insensitive_dict_get(
        image_properties, config.ACI_FIELD_CONTAINERS_CONFIGMAP
    ):
        return []

    return [{
            config.ACI_FIELD_CONTAINERS_MOUNTS_TYPE:
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_CONFIGMAP_TYPE,
            config.ACI_FIELD_CONTAINERS_MOUNTS_PATH:
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_CONFIGMAP_LOCATION,
            config.ACI_FIELD_CONTAINERS_MOUNTS_READONLY: False,
            }]


def process_mounts_from_config(image_properties: dict) -> List[Dict[str, str]]:
    mounts = []
    # get the mount types from the mounts section of the ARM template
    volume_mounts = (
        case_insensitive_dict_get(
            image_properties, config.ACI_FIELD_TEMPLATE_VOLUME_MOUNTS
        )
        or []
    )

    if volume_mounts and not isinstance(volume_mounts, list):
        # parameter definition is in parameter file but not arm
        # template
        eprint(
            f'Parameter ["{config.ACI_FIELD_TEMPLATE_VOLUME_MOUNTS}"] must be a list'
        )

    # get list of mount information based on mount name
    for mount in volume_mounts:
        mount_type = case_insensitive_dict_get(
            mount, config.ACI_FIELD_TEMPLATE_MOUNTS_TYPE
        )

        if not mount_type:
            eprint(
                f'Field ["{config.ACI_FIELD_TEMPLATE_MOUNTS_TYPE}"] is empty or cannot be found in mount'
            )

        mount_path = case_insensitive_dict_get(
            mount, config.ACI_FIELD_TEMPLATE_MOUNTS_PATH
        )

        if not mount_path:
            eprint(
                f'Field ["{config.ACI_FIELD_TEMPLATE_MOUNTS_PATH}"] is empty or cannot be found in mount'
            )

        mounts.append(
            {
                config.ACI_FIELD_CONTAINERS_MOUNTS_TYPE: case_insensitive_dict_get(
                    mount, config.ACI_FIELD_TEMPLATE_MOUNTS_TYPE
                ),
                config.ACI_FIELD_CONTAINERS_MOUNTS_PATH: case_insensitive_dict_get(
                    mount, config.ACI_FIELD_TEMPLATE_MOUNTS_PATH
                ),
                config.ACI_FIELD_CONTAINERS_MOUNTS_READONLY: case_insensitive_dict_get(
                    mount, config.ACI_FIELD_TEMPLATE_MOUNTS_READONLY
                ),
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_OPTIONS: case_insensitive_dict_get(
                    mount, config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_OPTIONS
                )
            }
        )
    return mounts


def get_values_for_params(input_parameter_json: dict, all_params: dict) -> Dict[str, Any]:
    # combine the parameter file into a single dictionary with the template
    # parameters
    if not input_parameter_json:
        return

    input_parameter_values_json = case_insensitive_dict_get(
        input_parameter_json, config.ACI_FIELD_TEMPLATE_PARAMETERS
    )

    # parameter file is missing field "parameters"
    if input_parameter_json and not input_parameter_values_json:
        eprint(
            f'Field ["{config.ACI_FIELD_TEMPLATE_PARAMETERS}"] is empty or cannot be found in Parameter file'
        )

    for key in input_parameter_values_json.keys():
        if case_insensitive_dict_get(all_params, key):
            all_params[key]["value"] = case_insensitive_dict_get(
                case_insensitive_dict_get(input_parameter_values_json, key), "value"
            ) or case_insensitive_dict_get(
                case_insensitive_dict_get(input_parameter_values_json, key), "secureValue"
            )
        else:
            # parameter definition is in parameter file but not arm
            # template
            eprint(
                f'Parameter ["{key}"] is empty or cannot be found in ARM template'
            )


def extract_probe(exec_processes: List[dict], image_properties: dict, probe: str):

    # get the readiness probe if it exists and is an exec command
    probe = case_insensitive_dict_get(
        image_properties, probe
    )

    if probe:
        probe_exec = case_insensitive_dict_get(
            probe, config.ACI_FIELD_CONTAINERS_PROBE_ACTION
        )
        if probe_exec:
            probe_command = case_insensitive_dict_get(
                probe_exec,
                config.ACI_FIELD_CONTAINERS_PROBE_COMMAND,
            )
            if not probe_command:
                eprint("Probes must have a 'command' declaration")
            exec_processes.append({
                config.ACI_FIELD_CONTAINERS_PROBE_COMMAND: probe_command,
                config.ACI_FIELD_CONTAINERS_SIGNAL_CONTAINER_PROCESSES: [],
            })

def get_probe_exec_processes(image_properties: dict) -> List[dict]:
    exec_processes: List[dict] = []
    extract_probe(exec_processes, image_properties, config.ACI_FIELD_CONTAINERS_READINESS_PROBE)
    extract_probe(exec_processes, image_properties, config.ACI_FIELD_CONTAINERS_LIVENESS_PROBE)
    return exec_processes


def extract_lifecycle_hook(exec_processes: List[dict], image_properties: dict, hook: str):
    lifecycle = case_insensitive_dict_get(
        image_properties, config.VIRTUAL_NODE_YAML_LIFECYCLE
    )

    if not lifecycle:
        return

    hook_val = case_insensitive_dict_get(
        lifecycle, hook
    )

    if not hook_val:
        return

    hook_exec = case_insensitive_dict_get(
        hook_val, config.VIRTUAL_NODE_YAML_LIFECYCLE_EXEC
    )
    if not hook_exec:
        return

    hook_command = case_insensitive_dict_get(
        hook_exec,
        config.VIRTUAL_NODE_YAML_LIFECYCLE_COMMAND,
    )
    if not hook_command:
        eprint("Hooks must have a 'command' declaration")
    exec_processes.append({
        config.ACI_FIELD_CONTAINERS_PROBE_COMMAND: hook_command,
        config.ACI_FIELD_CONTAINERS_SIGNAL_CONTAINER_PROCESSES: [],
    })


def readable_diff(diff_dict) -> Dict[str, Any]:
    # need to rename fields in the deep diff to be more accessible to customers
    name_translation = {
        "values_changed": "values_changed",
        "iterable_item_removed": "values_removed",
        "iterable_item_added": "values_added"
    }

    human_readable_diff = {}
    # iterate through the possible types of changes i.e. "iterable_item_removed"
    for category in diff_dict:
        new_name = case_insensitive_dict_get(name_translation, category) or category
        if case_insensitive_dict_get(human_readable_diff, category) is None:
            human_readable_diff[new_name] = {}
        # sometimes the output will be an array, this next chunk doesn't work for that case in its current state
        if isinstance(diff_dict[category], dict):
            # search for the area of the ARM Template with the change i.e. "mounts" or "env_rules"
            for key in diff_dict[category]:
                key = str(key)

                key_name_group = re.search(r"'(.*?)'", key)
                if key_name_group is not None:
                    key_name = key_name_group.group(1)
                    human_readable_diff[new_name].setdefault(key_name, []).append(
                        diff_dict[category][key]
                    )

    return change_key_names(human_readable_diff)


def compare_containers(container1, container2) -> Dict[str, Any]:
    """Utility method: see if the container in test_policy
    would be allowed to run under the rules of the 'self' policy"""

    diff = deepdiff.DeepDiff(
        container1,
        container2,
        ignore_order=True,
    )
    # cast to json using built-in function in deepdiff so there's safe translation
    # e.g. a type will successfully cast to string
    return readable_diff(json.loads(diff.to_json()))


def get_container_diff(container1, container2) -> Dict[str, Any]:
    container1_copy = copy.deepcopy(container1)
    container2_copy = copy.deepcopy(container2)

    # the ID does not matter so delete them from comparison
    container1_copy.pop(config.POLICY_FIELD_CONTAINERS_ID, None)
    container2_copy.pop(config.POLICY_FIELD_CONTAINERS_ID, None)
    # env vars will be compared later so delete them from this
    # comparison
    container1_copy.pop(config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS, None)
    container2_copy.pop(config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS, None)

    return compare_containers(container1_copy, container2_copy)


def change_key_names(dictionary) -> Dict:
    """Recursive function to rename keys wherever they are in the output diff dictionary"""
    # need to rename fields in the deep diff to be more accessible to customers
    name_translation = {
        "old_value": "policy_value",
        "new_value": "tested_value",
    }

    if isinstance(dictionary, (str, int)):
        return None
    if isinstance(dictionary, list):
        for item in dictionary:
            change_key_names(item)
    if isinstance(dictionary, dict):
        keys = list(dictionary.keys())
        for key in keys:
            if key in name_translation:
                dictionary[name_translation[key]] = dictionary.pop(key)
                key = name_translation[key]
            # go through the rest of the keys in case the objects are nested
            change_key_names(dictionary[key])
    return dictionary


def get_diff_size(diff: dict) -> int:
    """Utility function: get the size of the diff dictionary"""
    size = 0
    for key in diff:
        if isinstance(diff[key], dict):
            size += get_diff_size_helper(diff[key])
        else:
            size += 1
    return size


def get_diff_size_helper(diff: dict) -> int:
    size = 0
    for key in diff:
        if isinstance(diff[key], dict):
            size += get_diff_size_helper(diff[key])
        elif isinstance(diff[key], list) and key == "env_rules":
            size += len(diff[key])
        else:
            size += 1
    return size


def replace_params_and_vars(params: dict, vars_dict: dict, attribute):
    out = None
    if isinstance(attribute, (int, float, bool)):
        out = attribute
    elif isinstance(attribute, str):
        out = find_value_in_params_and_vars(params, vars_dict, attribute, ignore_undefined_parameters=True)
        param_name = re.finditer(WHOLE_PARAMETER_AND_VARIABLE, attribute)

        # there should only be one match
        full_param_name = next(param_name, None)
        if full_param_name:
            full_param_name = full_param_name.group(0)
            # cast to string
            out = f"{out}"
            out = attribute.replace(full_param_name, out)

    elif isinstance(attribute, list):
        out = []
        for item in attribute:
            out.append(replace_params_and_vars(params, vars_dict, item))
    elif isinstance(attribute, dict):
        out = {}
        for key, value in attribute.items():
            out[key] = replace_params_and_vars(params, vars_dict, value)
    return out


def find_value_in_params_and_vars(params: dict, vars_dict: dict, search: str, ignore_undefined_parameters=False) -> str:
    """Utility function: either returns the input search value,
    or replaces it with the defined value in either params or vars of the ARM template"""
    # this pattern might need to be updated for more naming options in the future
    param_name = re.findall(PARAMETER_AND_VARIABLE_REGEX, search)
    if not param_name:
        return search

    # this could be updated in the future if more than one variable/parameter is used in one value
    param_name = param_name[0]

    # figure out if we need to search in variables or parameters

    match = None
    if config.ACI_FIELD_TEMPLATE_PARAMETERS in search:

        param_value = case_insensitive_dict_get(params, param_name)

        if param_value is None:
            eprint(
                f"""Field "{param_name}" not found in ["{config.ACI_FIELD_TEMPLATE_PARAMETERS}"]
                 or ["{config.ACI_FIELD_TEMPLATE_VARIABLES}"]"""
            )
        # fallback to default value
        match = case_insensitive_dict_get(
            param_value, "value"
        ) if "value" in param_value else case_insensitive_dict_get(param_value, "defaultValue")
    else:
        match = case_insensitive_dict_get(vars_dict, param_name)

    if match is None and not ignore_undefined_parameters:
        eprint(
            f"""Field "{param_name}"'s value not found in ["{config.ACI_FIELD_TEMPLATE_PARAMETERS}"]
             or ["{config.ACI_FIELD_TEMPLATE_VARIABLES}"]"""
        )

    return match if match is not None else search


def parse_template(params: dict, vars_dict: dict, template, ignore_undefined_parameters=False) -> Any:
    """Utility function: replace all instances of variable and parameter references in an ARM template
    current limitations:
        - object values for parameters and variables
        - template functions
        - complex values for parameters and variables
        - parameter and variables names might not be recognized all the time
    """
    if isinstance(template, dict):
        for key, value in template.items():
            if isinstance(value, str):
                # we want to ignore undefined parameters for only env var values, not names
                template[key] = find_value_in_params_and_vars(params, vars_dict, value,
                                                              ignore_undefined_parameters=ignore_undefined_parameters
                                                              and key.lower() in ("value", "securevalue"))
            elif isinstance(value, dict):
                parse_template(params, vars_dict, value)
            elif isinstance(value, list):
                for i, _ in enumerate(value):
                    template[key][i] = parse_template(params, vars_dict, value[i],
                                                      ignore_undefined_parameters=key
                                                      == config.ACI_FIELD_CONTAINERS_ENVS)
    return template


def extract_containers_from_text(text, start) -> str:
    """Utility function: extract the container and fragment
    information from the string version of a rego file.
     The contained information is assumed to be an array between square brackets"""
    start_index = text.find(start)
    ending = text[start_index + len(start):]

    count = bracket_count = 0
    character = ending[count]
    flag = True
    # kind of an FSM to get everything between starting square bracket and end
    while bracket_count > 0 or flag:
        count += 1
        # make sure we're ending on the correct end bracket
        if character == "[":
            bracket_count += 1
            flag = False
        elif character == "]":
            bracket_count -= 1

        if count == len(ending):
            # throw error, invalid rego file
            break
        character = ending[count]
    # get everything between the square brackets
    return ending[:count]


def extract_standalone_fragments(
    container_group_properties,
) -> List[str]:
    # extract the existing cce policy if that's what was being asked
    confidential_compute_properties = case_insensitive_dict_get(
        container_group_properties, config.ACI_FIELD_TEMPLATE_CONFCOM_PROPERTIES
    )

    if confidential_compute_properties is None:
        return []

    # in the ARM template, this is a list of references (strings) to OCI registries
    standalone_fragments = case_insensitive_dict_get(
        confidential_compute_properties, config.ACI_FIELD_TEMPLATE_STANDALONE_REGO_FRAGMENTS
    ) or []
    return standalone_fragments


def extract_confidential_properties(
    container_group_properties,
) -> Tuple[List[Dict], List[Dict]]:
    # extract the existing cce policy if that's what was being asked
    confidential_compute_properties = case_insensitive_dict_get(
        container_group_properties, config.ACI_FIELD_TEMPLATE_CONFCOM_PROPERTIES
    )

    if confidential_compute_properties is None:
        return ([], [])

    cce_policy = case_insensitive_dict_get(
        confidential_compute_properties, config.ACI_FIELD_TEMPLATE_CCE_POLICY
    )
    # special case when "ccePolicy" field is blank, indicating the use of the "allow all" policy
    if not cce_policy:
        return ([], config.DEFAULT_REGO_FRAGMENTS)

    return decompose_confidential_properties(cce_policy)


def decompose_confidential_properties(cce_policy: str) -> Tuple[List[Dict], List[Dict]]:
    cce_policy = os_util.base64_to_str(cce_policy)
    # error check that the decoded policy existing in the template is not in JSON format
    try:
        json.loads(cce_policy)
        eprint(
            """The existing security policy within the ARM Template
             is not in the expected Rego format when decoded from base64"""
        )
    except json.decoder.JSONDecodeError:
        # this is expected, we do not want json
        pass

    return extract_containers_and_fragments_from_text(cce_policy)


def extract_containers_and_fragments_from_text(text: str) -> Tuple[List[Dict], List[Dict]]:
    try:
        container_text = extract_containers_from_text(text, config.REGO_CONTAINER_START)
        # replace tabs with 4 spaces, YAML parser can take in JSON with trailing commas but not tabs
        # so we need to get rid of the tabs
        container_text = container_text.replace("\t", "    ")
        containers = yaml.load(container_text, Loader=yaml.FullLoader)
        fragment_text = extract_containers_from_text(
            text, config.REGO_FRAGMENT_START
        ).replace("\t", "    ")

        fragments = yaml.load(
            fragment_text,
            Loader=yaml.FullLoader,
        )
    except yaml.YAMLError as e:
        eprint(f"Error parsing rego file: {e}")
        # reading the rego file failed, so we'll just return the default outputs
        containers = []
        fragments = []

    return (containers, fragments)


def extract_svn_from_text(text: str) -> int:
    """Extract SVN value from text using regex pattern matching.

    Args:
        text: The input text containing the SVN definition

    Returns:
        int: The SVN value
    """
    # Pattern matches: svn := "123" or svn := "1"
    match = re.search(SVN_PATTERN, text)

    if not match:
        eprint("SVN value not found in the input text.")

    try:
        return int(match.group(1))
    except (AttributeError, ValueError, IndexError):
        eprint("Unable to extract valid SVN value from the text.")


def extract_namespace_from_text(text: str) -> str:
    """Extract namespace value from text by finding text after 'package' keyword.

    Args:
        text: The input text containing the namespace definition

    Returns:
        str: The namespace value
    """
    # Find the package declaration line
    lines = text.split('\n')
    for line in lines:
        stripped_line = line.strip()
        beginning = 'package '
        if stripped_line.startswith(beginning):
            # Extract everything after 'package ' (first whitespace)
            namespace = stripped_line[len(beginning):].strip()
            if namespace:
                return namespace

    eprint("Namespace value not found in the input text.")
    return None


# making these lambda print functions looks cleaner than having "json.dumps" 6 times
def print_func(x: dict) -> str:
    return json.dumps(x, separators=(",", ":"), sort_keys=True)


def pretty_print_func(x: dict) -> str:
    return json.dumps(x, indent=2, sort_keys=True)


def str_to_sha256(x: str) -> str:
    return sha256(x.encode('utf-8')).hexdigest()


def is_sidecar(image_name: str) -> bool:
    return image_name.split(":")[0] in config.BASELINE_SIDECAR_CONTAINERS


def translate_signals(signals: List[str]) -> List[int]:
    for i, signal_val in enumerate(signals):
        if isinstance(signal_val, str) and signal_val.upper() in config.SIGNALS:
            signals[i] = config.SIGNALS[signal_val.upper()]
    return signals


def compare_env_vars(
    id_val, env_list1: List[Dict[str, Any]], env_list2: List[Dict[str, Any]]
) -> Dict[str, List[str]]:
    reason_list = {}
    policy_env_rules_regex = [
        case_insensitive_dict_get(i, config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE)
        for i in env_list1
        if case_insensitive_dict_get(
            i, config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_STRATEGY
        )
        == "re2"
    ]

    policy_env_rules_str = [
        case_insensitive_dict_get(i, config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE)
        for i in env_list1
        if case_insensitive_dict_get(
            i, config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_STRATEGY
        )
        == "string"
    ]

    # check that all env vars in the container match rules that are present in the policy
    for env_rule in env_list2:
        # case where rule with strategy string is not in the policy's list of string rules
        # we need to check if it fits one of the patterns in the regex list
        if (
            case_insensitive_dict_get(
                env_rule, config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_STRATEGY
            )
            == "string"
            and case_insensitive_dict_get(
                env_rule, config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE
            )
            not in policy_env_rules_str
        ):
            # check if the env var matches any of the regex rules
            matching = False
            for pattern in policy_env_rules_regex:
                matching = matching or re.search(
                    pattern,
                    case_insensitive_dict_get(
                        env_rule, config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE
                    ),
                )
                if matching:
                    break

            if not matching:
                # create the env_rules entry in the diff output if it doesn't exist
                reason_list.setdefault(id_val, {})
                # add this to the list of rules violating policy
                reason_list[id_val].setdefault(
                    config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS, []
                ).append(
                    "environment variable with rule "
                    + f"'{case_insensitive_dict_get(env_rule, config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE)}' "
                    + "does not match strings or regex in policy rules"
                )
        # make sure all the regex patterns are included in the policy too
        elif (
            case_insensitive_dict_get(
                env_rule, config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_STRATEGY
            )
            == "re2"
            and case_insensitive_dict_get(
                env_rule, config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE
            )
            not in policy_env_rules_regex
        ):
            # create the env_rules entry in the diff output if it doesn't exist
            reason_list.setdefault(id_val, {})
            # add this to the list of rules violating policy
            reason_list[id_val].setdefault(
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS, []
            ).append(
                "environment variable with rule "
                + f"'{case_insensitive_dict_get(env_rule, config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE)}' "
                + "is not in the policy"
            )
    return reason_list


def inject_policy_into_template(
    arm_template_path: str, parameter_data_path: str, policy: str, count: int
) -> bool:
    write_flag = False
    parameter_data = None
    input_arm_json = os_util.load_json_from_file(arm_template_path)
    if parameter_data_path:
        parameter_data = os_util.load_json_from_file(arm_template_path)
    # find the image names and extract them from the template
    arm_resources = case_insensitive_dict_get(
        input_arm_json, config.ACI_FIELD_RESOURCES
    )

    if not arm_resources:
        eprint(f"Field [{config.ACI_FIELD_RESOURCES}] is empty or cannot be found")

    aci_list = [
        item
        for item in arm_resources
        if item["type"] in config.ACI_FIELD_SUPPORTED_RESOURCES
    ]

    if not aci_list:
        eprint(
            f'Field ["type"] must contain one of {config.ACI_FIELD_SUPPORTED_RESOURCES}'
        )

    resource = aci_list[count]

    container_group_properties = case_insensitive_dict_get(
        resource, config.ACI_FIELD_TEMPLATE_PROPERTIES
    )

    # extract the existing cce policy if that's what was being asked
    confidential_compute_properties = case_insensitive_dict_get(
        container_group_properties, config.ACI_FIELD_TEMPLATE_CONFCOM_PROPERTIES
    )

    if not confidential_compute_properties:
        # initialize the confcom properties and reassign the variable to the empty dict
        container_group_properties[config.ACI_FIELD_TEMPLATE_CONFCOM_PROPERTIES] = {}
        confidential_compute_properties = case_insensitive_dict_get(
            container_group_properties, config.ACI_FIELD_TEMPLATE_CONFCOM_PROPERTIES
        )

    cce_policy = case_insensitive_dict_get(
        confidential_compute_properties, config.ACI_FIELD_TEMPLATE_CCE_POLICY
    )
    # special case when "ccePolicy" field is blank, indicating the use of the "allow all" policy
    if not cce_policy:
        confidential_compute_properties[config.ACI_FIELD_TEMPLATE_CCE_POLICY] = policy
        write_flag = True
    else:
        container_group_name = get_container_group_name(
            input_arm_json, parameter_data, count
        )
        user_input = input((
            "Do you want to overwrite the CCE Policy currently in container group "
            f'"{container_group_name}" in the ARM Template? (y/n) '
        ))
        if user_input.lower() == "y":
            confidential_compute_properties[
                config.ACI_FIELD_TEMPLATE_CCE_POLICY
            ] = policy
            write_flag = True

    if write_flag:
        os_util.write_json_to_file(arm_template_path, input_arm_json)
        return True
    return False


def inject_policy_into_yaml(
    yaml_file_path: str, policy: str, count: int
) -> bool:
    virtual_node_yaml = list(os_util.load_multiple_yaml_from_file(yaml_file_path))
    filtered_yaml = filter_non_pod_resources(virtual_node_yaml)
    current_yaml = filtered_yaml[count]
    pod_item = convert_to_pod_spec_helper(current_yaml)

    # extract existing policy (if any)
    try:
        existing_policy = pod_item[config.VIRTUAL_NODE_YAML_METADATA][
            config.VIRTUAL_NODE_YAML_ANNOTATIONS][config.VIRTUAL_NODE_YAML_POLICY]
    except KeyError:
        existing_policy = None

    # check if the existing policy should be overwritten
    if existing_policy:
        workload_name = pod_item.get("metadata", {}).get("name", f"Workload {count}")
        user_input = input(
            f"Do you want to overwrite the Base64 Policy currently in workload '{workload_name}'? (y/n) "
        )
        # if user declines, exit
        if user_input.lower() != "y":
            return False

    # prepare new metadata with updated policy
    needed_metadata = {
        config.VIRTUAL_NODE_YAML_METADATA: {
            config.VIRTUAL_NODE_YAML_ANNOTATIONS: {
                config.VIRTUAL_NODE_YAML_POLICY: policy
            }
        }
    }

    # update workload metadata with new policy
    deep_dict_update(needed_metadata, pod_item)

    # find index of current YAML in the original YAML file
    count_in_file = virtual_node_yaml.index(current_yaml)

    # replace current YAML with updated yaml in the original list
    virtual_node_yaml[count_in_file] = current_yaml

    # write updated yaml back to file
    os_util.write_multiple_yaml_to_file(yaml_file_path, virtual_node_yaml)

    return True


def get_container_group_name(
    input_arm_json: dict, input_parameter_json: dict, count: int
) -> bool:
    arm_json = copy.deepcopy(input_arm_json)
    # extract variables and parameters in case we need to do substitutions
    # while searching for image names
    all_vars = case_insensitive_dict_get(arm_json, config.ACI_FIELD_TEMPLATE_VARIABLES) or {}
    all_params = (
        case_insensitive_dict_get(arm_json, config.ACI_FIELD_TEMPLATE_PARAMETERS) or {}
    )

    if input_parameter_json:
        # combine the parameter file into a single dictionary with the template parameters
        input_parameter_values_json = case_insensitive_dict_get(
            input_parameter_json, config.ACI_FIELD_TEMPLATE_PARAMETERS
        )
        for key in input_parameter_values_json.keys():
            if case_insensitive_dict_get(all_params, key):
                all_params[key]["value"] = case_insensitive_dict_get(
                    case_insensitive_dict_get(input_parameter_values_json, key), "value"
                ) if case_insensitive_dict_get(
                    case_insensitive_dict_get(input_parameter_values_json, key), "value"
                ) is not None else case_insensitive_dict_get(
                    case_insensitive_dict_get(input_parameter_values_json, key),
                    "secureValue",
                )
            else:
                # parameter definition is in parameter file but not arm template
                eprint(
                    f'Parameter ["{key}"] is empty or cannot be found in ARM template'
                )
    # parameter file is missing field "parameters"
    elif input_parameter_json and not input_parameter_values_json:
        eprint(
            f'Field ["{config.ACI_FIELD_TEMPLATE_PARAMETERS}"] is empty or cannot be found in Parameter file'
        )

    # find the image names and extract them from the template
    arm_resources = case_insensitive_dict_get(arm_json, config.ACI_FIELD_RESOURCES)

    if not arm_resources:
        eprint(f"Field [{config.ACI_FIELD_RESOURCES}] is empty or cannot be found")

    aci_list = [
        item
        for item in arm_resources
        if item["type"] in config.ACI_FIELD_SUPPORTED_RESOURCES
    ]

    if not aci_list:
        eprint(
            f'Field ["type"] must contain one of {config.ACI_FIELD_SUPPORTED_RESOURCES}'
        )

    resource = aci_list[count]
    resource = replace_params_and_vars(all_params, all_vars, resource)
    container_group_name = case_insensitive_dict_get(resource, config.ACI_FIELD_RESOURCES_NAME)
    return container_group_name


def print_existing_policy_from_arm_template(arm_template_path, parameter_data_path):
    if not arm_template_path:
        eprint("Can only print existing policy from ARM Template")
    input_arm_json = os_util.load_json_from_file(arm_template_path)
    parameter_data = None
    if parameter_data_path:
        parameter_data = os_util.load_json_from_file(parameter_data_path)

    # find the image names and extract them from the template
    arm_resources = case_insensitive_dict_get(
        input_arm_json, config.ACI_FIELD_RESOURCES
    )

    if not arm_resources:
        eprint(f"Field [{config.ACI_FIELD_RESOURCES}] is empty or cannot be found")

    aci_list = [
        item
        for item in arm_resources
        if item["type"] in config.ACI_FIELD_SUPPORTED_RESOURCES
    ]

    if not aci_list:
        eprint(
            f'Field ["type"] must contain one of {config.ACI_FIELD_SUPPORTED_RESOURCES}'
        )
    for i, resource in enumerate(aci_list):
        container_group_properties = case_insensitive_dict_get(
            resource, config.ACI_FIELD_TEMPLATE_PROPERTIES
        )
        container_group_name = get_container_group_name(input_arm_json, parameter_data, i)

        # extract the existing cce policy if that's what was being asked
        confidential_compute_properties = case_insensitive_dict_get(
            container_group_properties, config.ACI_FIELD_TEMPLATE_CONFCOM_PROPERTIES
        )

        if confidential_compute_properties is None:
            eprint(
                f"""Field ["{config.ACI_FIELD_TEMPLATE_CONFCOM_PROPERTIES}"]
                not found in ["{config.ACI_FIELD_TEMPLATE_PROPERTIES}"]"""
            )

        cce_policy = case_insensitive_dict_get(
            confidential_compute_properties, config.ACI_FIELD_TEMPLATE_CCE_POLICY
        )

        if not cce_policy:
            eprint("CCE Policy is either in an supported format or not present")

        cce_policy = os_util.base64_to_str(cce_policy)
        print(f"CCE Policy for Container Group: {container_group_name}\n")
        print(cce_policy)


def print_existing_policy_from_yaml(virtual_node_yaml_path: str) -> None:
    if not virtual_node_yaml_path:
        eprint("Can only print existing policy from Virtual Node YAML file")
    yaml_contents = os_util.load_multiple_yaml_from_file(virtual_node_yaml_path)
    yaml_contents = filter_non_pod_resources(yaml_contents)
    for resource in yaml_contents:
        # normalize the resource to be a pod spec
        resource = convert_to_pod_spec(resource)
        # get the policy from the pod spec
        metadata = case_insensitive_dict_get(
            resource, config.VIRTUAL_NODE_YAML_METADATA
        )

        if not metadata:
            eprint("Metadata not found in Virtual Node YAML resource")

        annotations = case_insensitive_dict_get(metadata, config.VIRTUAL_NODE_YAML_ANNOTATIONS)

        name = case_insensitive_dict_get(metadata, config.VIRTUAL_NODE_YAML_NAME)

        if not annotations:
            eprint(f"Annotations not found in Virtual Node YAML resource: {name}")

        policy = case_insensitive_dict_get(
            annotations, config.VIRTUAL_NODE_YAML_POLICY
        )

        if not policy:
            eprint(f"Policy not found in Virtual Node YAML resource: {name}")

        print(f"Policy for Pod: {name}\n")
        print(os_util.base64_to_str(policy))


def process_seccomp_policy(policy2):
    # helper function to add fields to a dictionary if they don't exist
    def defaults(obj, default):
        for key in default:
            obj.setdefault(key, default[key])
        return obj

    # helper function to pick fields from a dictionary
    def pick(obj, *keys):
        result = {}
        for key in keys:
            if key in obj:
                result[key] = obj[key]
        return result

    policy = json.loads(policy2)
    policy = defaults(policy, {'defaultAction': ""})
    policy = pick(policy, 'defaultAction', 'defaultErrnoRet', 'architectures',
                  'flags', 'listenerPath', 'listenerMetadata', 'syscalls')
    if 'syscalls' in policy:
        syscalls = policy['syscalls']
        temp_syscalls = []
        for s in syscalls:
            syscall = s
            syscall = defaults(syscall, {'names': [], 'action': ""})
            syscall = pick(syscall, 'names', 'action', 'errnoRet', 'args')

            if 'args' in syscall:
                temp_args = []
                args = syscall['args']

                for j in args:
                    arg = j
                    arg = defaults(arg, {'value': 0, 'op': "", 'index': 0})
                    arg = pick(arg, 'index', 'value', 'valueTwo', 'op')
                    temp_args.append(arg)
                syscall['args'] = temp_args
            temp_syscalls.append(syscall)
        # put temp_syscalls back into policy
        policy['syscalls'] = temp_syscalls
    return policy


def convert_config_v0_to_v1(old_data):
    """
    Convert a JSON structure from the 'v0' format to the 'v1' format.
    If the input is already in 'v1' format, return the original input.

    :param old_data: Dictionary in the old format.
    :return: Dictionary in the new format.

    Expected old_data schema (simplified):
    {
        "version": "1.0",
        "containers": [
            {
                "name": "...",
                "containerImage": "...",
                "environmentVariables": [
                    {
                        "name": "...",
                        "value": "...",
                        "strategy": "string" or "re2" (optional, default is string)
                    }
                ],
                "command": [...],
                "workingDir": "...",
                "mounts": [
                    {
                        "mountType": "...",
                        "mountPath": "...",
                        "readonly": bool
                    }
                ]
            },
            ...
        ]
    }

    Returns a structure matching the 'new' format:
    {
        "version": "...",
        "fragments": [],
        "containers": [
            {
                "name": "...",
                "properties": {
                    "image": "...",
                    "workingDir": "...",
                    "execProcesses": [
                        {
                            "command": [...]
                        }
                    ],
                    "volumeMounts": [
                        {
                            "name": "...",
                            "mountPath": "...",
                            "mountType": "...",
                            "readOnly": bool
                        }
                    ],
                    "environmentVariables": [
                        {
                            "name": "...",
                            "value": "...",
                            "regex": bool (only present if we decide so, default is false)
                        }
                    ]
                }
            },
            ...
        ]
    }
    """
    if not detect_old_format(old_data):
        logger.warning("JSON config is already in v1 format")
        return old_data

    # Prepare the structure of the new JSON
    new_data = {
        config.ACI_FIELD_VERSION: case_insensitive_dict_get(
            old_data, config.ACI_FIELD_VERSION, "1.0"
        ),  # default if missing
        config.ACI_FIELD_CONTAINERS_REGO_FRAGMENTS: [],
        config.ACI_FIELD_CONTAINERS: []
    }

    old_containers = case_insensitive_dict_get(old_data, config.ACI_FIELD_CONTAINERS, [])

    for old_container in old_containers:
        # Build the 'environmentVariables' section in the new format
        new_envs = []
        for env_var in case_insensitive_dict_get(old_container, config.ACI_FIELD_CONTAINERS_ENVS) or []:
            # Decide if we need 'regex' or not, based on 'strategy' or your custom logic
            # Here we'll assume "strategy"=="re2" means 'regex' = True
            # If strategy is missing or 'string', omit 'regex' or set it to False
            env_entry = {
                config.ACI_FIELD_CONTAINERS_ENVS_NAME: case_insensitive_dict_get(
                    env_var, config.ACI_FIELD_CONTAINERS_ENVS_NAME
                ),
                config.ACI_FIELD_CONTAINERS_ENVS_VALUE: case_insensitive_dict_get(
                    env_var, config.ACI_FIELD_CONTAINERS_ENVS_VALUE, ""
                )
            }
            strategy = case_insensitive_dict_get(env_var, config.ACI_FIELD_CONTAINERS_ENVS_STRATEGY)
            if strategy == "re2":
                env_entry["regex"] = True

            new_envs.append(env_entry)

        # Build the 'execProcesses' from the old 'command'
        exec_processes = []
        old_command_list = case_insensitive_dict_get(old_container, config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES, [])
        if old_command_list:
            exec_processes.append({config.ACI_FIELD_CONTAINERS_COMMAND: old_command_list})

        command = case_insensitive_dict_get(old_container, config.ACI_FIELD_CONTAINERS_COMMAND)

        # Liveness probe => exec process
        liveness_probe = case_insensitive_dict_get(old_container, config.ACI_FIELD_CONTAINERS_LIVENESS_PROBE, {})
        liveness_exec = case_insensitive_dict_get(liveness_probe, config.ACI_FIELD_CONTAINERS_PROBE_ACTION, {})
        liveness_command = case_insensitive_dict_get(liveness_exec, config.ACI_FIELD_CONTAINERS_COMMAND, [])
        if liveness_command:
            exec_processes.append({
                config.ACI_FIELD_CONTAINERS_COMMAND: liveness_command
            })

        # Readiness probe => exec process
        readiness_probe = case_insensitive_dict_get(old_container, config.ACI_FIELD_CONTAINERS_READINESS_PROBE, {})
        readiness_exec = case_insensitive_dict_get(readiness_probe, config.ACI_FIELD_CONTAINERS_PROBE_ACTION, {})
        readiness_command = case_insensitive_dict_get(readiness_exec, config.ACI_FIELD_CONTAINERS_COMMAND, [])
        if readiness_command:
            exec_processes.append({
                config.ACI_FIELD_CONTAINERS_COMMAND: readiness_command
            })

        # Build the 'volumeMounts' section
        volume_mounts = []
        for mount in case_insensitive_dict_get(old_container, config.ACI_FIELD_CONTAINERS_MOUNTS) or []:
            # For 'name', we can take the mountType or generate something else:
            # e.g. if mountType is "azureFile", name "azurefile"
            mount_name = case_insensitive_dict_get(
                mount, config.ACI_FIELD_CONTAINERS_MOUNTS_TYPE, "defaultName"
            ).lower()
            volume_mount = {
                config.ACI_FIELD_CONTAINERS_ENVS_NAME: mount_name,
                config.ACI_FIELD_TEMPLATE_MOUNTS_PATH: case_insensitive_dict_get(
                    mount, config.ACI_FIELD_CONTAINERS_MOUNTS_PATH
                ),
                config.ACI_FIELD_TEMPLATE_MOUNTS_TYPE: case_insensitive_dict_get(
                    mount, config.ACI_FIELD_CONTAINERS_MOUNTS_TYPE
                ),
                config.ACI_FIELD_TEMPLATE_MOUNTS_READONLY: case_insensitive_dict_get(
                    mount, config.ACI_FIELD_CONTAINERS_MOUNTS_READONLY, True
                ),
            }
            volume_mounts.append(volume_mount)

        # Create the container's "properties" object
        container_properties = {
            config.ACI_FIELD_TEMPLATE_IMAGE: case_insensitive_dict_get(
                old_container, config.ACI_FIELD_CONTAINERS_CONTAINERIMAGE
            ),
            config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES: exec_processes,
            config.ACI_FIELD_TEMPLATE_VOLUME_MOUNTS: volume_mounts,
            config.ACI_FIELD_CONTAINERS_ENVS: new_envs,
            config.ACI_FIELD_CONTAINERS_COMMAND: command,
        }

        if case_insensitive_dict_get(old_container, config.ACI_FIELD_TEMPLATE_SECURITY_CONTEXT) is not None:
            container_properties[
                config.ACI_FIELD_TEMPLATE_SECURITY_CONTEXT
            ] = old_container[config.ACI_FIELD_TEMPLATE_SECURITY_CONTEXT]

        if case_insensitive_dict_get(old_container, config.ACI_FIELD_CONTAINERS_ALLOW_ELEVATED) is not None:
            if config.ACI_FIELD_TEMPLATE_SECURITY_CONTEXT not in container_properties:
                container_properties[config.ACI_FIELD_TEMPLATE_SECURITY_CONTEXT] = {}
            container_properties[
                config.ACI_FIELD_TEMPLATE_SECURITY_CONTEXT
            ][config.ACI_FIELD_CONTAINERS_PRIVILEGED] = case_insensitive_dict_get(
                old_container, config.ACI_FIELD_CONTAINERS_ALLOW_ELEVATED
            )

        if case_insensitive_dict_get(old_container, config.ACI_FIELD_CONTAINERS_WORKINGDIR) is not None:
            container_properties[
                config.ACI_FIELD_CONTAINERS_WORKINGDIR
            ] = case_insensitive_dict_get(old_container, config.ACI_FIELD_CONTAINERS_WORKINGDIR)

        # Finally, assemble the new container dict
        new_container = {
            config.ACI_FIELD_CONTAINERS_NAME: case_insensitive_dict_get(
                old_container, config.ACI_FIELD_CONTAINERS_NAME
            ),
            config.ACI_FIELD_TEMPLATE_PROPERTIES: container_properties
        }

        new_data[config.ACI_FIELD_CONTAINERS].append(new_container)

    return new_data


def detect_old_format(old_data):
    # we want to encourage customers to transition to the new format. The best way to check for the old format is
    # to see if the json is flattened. This is an appropriate check since the image name is required
    # and they are located in different places in the two formats
    old_containers = case_insensitive_dict_get(old_data, config.ACI_FIELD_CONTAINERS, [])
    if len(old_containers) > 0 and case_insensitive_dict_get(
        old_containers[0], config.ACI_FIELD_CONTAINERS_CONTAINERIMAGE
    ) is not None:
        logger.warning(
            "%s %s %s",
            "(Deprecation Warning) The input format used is deprecated.",
            "To view the current format, please look at the examples in: ",
            "https://github.com/Azure/azure-cli-extensions/blob/main/src/confcom/azext_confcom/README.md"
        )
        return True
    return False
