# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import warnings
import copy
from typing import Any, List, Dict, Tuple
from enum import Enum, auto
import docker
import deepdiff
from knack.log import get_logger
from tqdm import tqdm
from azext_confcom import os_util
from azext_confcom import config
from azext_confcom.container import UserContainerImage, ContainerImage

from azext_confcom.errors import eprint
from azext_confcom.template_util import (
    extract_confidential_properties,
    is_sidecar,
    pretty_print_func,
    print_func,
    readable_diff,
    case_insensitive_dict_get,
    compare_env_vars,
    compare_containers,
    get_values_for_params,
    process_mounts,
    extract_probe,
    process_env_vars_from_template,
    get_image_info,
    get_tar_location_from_mapping
)
from azext_confcom.rootfs_proxy import SecurityPolicyProxy

logger = get_logger()


class OutputType(Enum):
    DEFAULT = auto()
    RAW = auto()
    PRETTY_PRINT = auto()


class AciPolicy:  # pylint: disable=too-many-instance-attributes
    all_params = {}
    all_vars = {}

    def __init__(
        self,
        deserialized_config: Any,
        rego_fragments: Any = copy.deepcopy(config.DEFAULT_REGO_FRAGMENTS),
        existing_rego_fragments: Any = None,
        debug_mode: bool = False,
        disable_stdio: bool = False,
    ) -> None:
        self._docker_client = None
        self._rootfs_proxy = None
        self._policy_str = None
        self._policy_str_pp = None
        self._disable_stdio = disable_stdio
        self._fragments = rego_fragments
        self._existing_fragments = existing_rego_fragments
        self._api_version = config.API_VERSION

        if debug_mode:
            self._allow_properties_access = config.DEBUG_MODE_SETTINGS.get(
                "allowPropertiesAccess"
            )
            self._allow_dump_stacks = config.DEBUG_MODE_SETTINGS.get(
                "allowDumpStacks"
            )
            self._allow_runtime_logging = config.DEBUG_MODE_SETTINGS.get(
                "allowRuntimeLogging"
            )
            self._allow_environment_variable_dropping = config.DEBUG_MODE_SETTINGS.get(
                "allowEnvironmentVariableDropping"
            )
            self._allow_unencrypted_scratch = config.DEBUG_MODE_SETTINGS.get(
                "allowUnencryptedScratch"
            )
            self._allow_capability_dropping = config.DEBUG_MODE_SETTINGS.get(
                "allowCapabilityDropping"
            )
        else:
            self._allow_properties_access = True
            self._allow_dump_stacks = False
            self._allow_runtime_logging = False
            self._allow_environment_variable_dropping = True
            self._allow_unencrypted_scratch = False
            self._allow_capability_dropping = True

        self.version = case_insensitive_dict_get(
            deserialized_config, config.ACI_FIELD_VERSION
        )
        if not self.version:
            eprint(
                f'Field ["{config.ACI_FIELD_VERSION}"] is empty or can not be found.'
            )

        # parse cce policy if it exists
        cce_policy = case_insensitive_dict_get(
            deserialized_config, config.ACI_FIELD_TEMPLATE_CCE_POLICY
        )

        self._existing_cce_policy = cce_policy

        containers = case_insensitive_dict_get(
            deserialized_config, config.ACI_FIELD_CONTAINERS
        )
        if not containers:
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS}"] is empty or can not be found.'
            )

        container_results = []

        # parse and generate each container, either user or sidecar
        for c in containers:
            if not is_sidecar(c[config.POLICY_FIELD_CONTAINERS_ID]):
                container_image = UserContainerImage.from_json(c)
            else:
                container_image = ContainerImage.from_json(c)
            container_results.append(container_image)

        self._images = container_results

    def __enter__(self) -> None:
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback) -> None:
        self.close()

    def _get_docker_client(self) -> docker.client.DockerClient:
        if not self._docker_client:
            self._docker_client = docker.from_env()

        return self._docker_client

    def _get_rootfs_proxy(self) -> SecurityPolicyProxy:
        if not self._rootfs_proxy:
            self._rootfs_proxy = SecurityPolicyProxy()

        return self._rootfs_proxy

    def _close_docker_client(self) -> None:
        if self._docker_client:
            self._get_docker_client().close()

    def close(self) -> None:
        self._close_docker_client()

    def get_serialized_output(
        self,
        output_type: OutputType = OutputType.DEFAULT,
        rego_boilerplate=True,
    ) -> str:
        # error check the output type
        if not isinstance(output_type, Enum) or output_type.value not in [item.value for item in OutputType]:
            eprint("Unknown output type for serialization.")

        policy_str = self._policy_serialization(
            output_type == OutputType.PRETTY_PRINT
        )

        if rego_boilerplate:
            policy_str = self._add_rego_boilerplate(policy_str)

        # if we're not outputting base64
        if output_type in (OutputType.RAW, OutputType.PRETTY_PRINT):
            return policy_str
        # encode to base64
        return os_util.str_to_base64(policy_str)

    def _add_rego_boilerplate(self, output: str) -> str:

        # determine if we're outputting for a sidecar or not
        if self._images[0].get_id() and is_sidecar(self._images[0].get_id()):
            return config.SIDECAR_REGO_POLICY % (
                pretty_print_func(self._api_version),
                output
            )
        return config.CUSTOMER_REGO_POLICY % (
            pretty_print_func(self._api_version),
            pretty_print_func(self._fragments),
            output,
            pretty_print_func(self._allow_properties_access),
            pretty_print_func(self._allow_dump_stacks),
            pretty_print_func(self._allow_runtime_logging),
            pretty_print_func(self._allow_environment_variable_dropping),
            pretty_print_func(self._allow_unencrypted_scratch),
            pretty_print_func(self._allow_capability_dropping),
        )

    def validate_cce_policy(self) -> Tuple[bool, Dict]:
        """Utility method: check to see if the existing policy
        that instantiates this function would allow the policy created by the input ARM Template"""
        # this implying the "allow all" policy
        if self._existing_cce_policy is None:
            return True, {}
        # we're comparing the CCE Policy so extract it and pass it in
        policy = self._existing_cce_policy
        return self.validate(policy)

    def validate_sidecars(self) -> Tuple[bool, Dict]:
        """Utility method: check to see if the sidecar images present will pass the given the current ACI Policy"""
        policy_str = self.get_serialized_output(
            OutputType.PRETTY_PRINT, rego_boilerplate=False
        )
        arm_containers = json.loads(policy_str)
        # filter out None from the list of images in case one doesn't have an
        # ID
        policy_ids = list(
            filter(
                lambda item: item is not None,
                [i.get(config.POLICY_FIELD_CONTAINERS_ID) for i in arm_containers],
            )
        )

        # filter out any non-sidecar images
        for policy_id in policy_ids:
            if not policy_id or not is_sidecar(policy_id):
                policy_ids.remove(policy_id)

        # if there are no sidecars, then error out
        if len(policy_ids) == 0:
            eprint("No sidecar images found in the policy.")

        policy = load_policy_from_image_name(policy_ids)

        policy.populate_policy_content_for_all_images(individual_image=True)
        policy_str = self.get_serialized_output(
            OutputType.PRETTY_PRINT, rego_boilerplate=False
        )
        policy_content = json.loads(policy_str)
        # done this way instead of self.validate() because the input.json is
        # the source of truth
        return policy.validate(policy_content, sidecar_validation=True)

    def validate(self, policy, sidecar_validation=False) -> Tuple[bool, Dict]:
        """Utility method: general method to compare two policies.
        One being the current object and the other is passed in as a parameter"""
        if not policy:
            eprint("Policy is not in the expected form to validate against")

        policy_str = self.get_serialized_output(
            OutputType.PRETTY_PRINT, rego_boilerplate=False
        )
        arm_containers = json.loads(policy_str)

        reason_list = {}

        policy_ids = [
            case_insensitive_dict_get(i, config.POLICY_FIELD_CONTAINERS_ID)
            for i in policy
        ]

        for container in arm_containers:
            # see if the IDs match with any container in the policy

            id_val = case_insensitive_dict_get(container, config.ACI_FIELD_CONTAINERS_ID)

            idx = policy_ids.index(id_val) if id_val in policy_ids else None

            if idx is None:
                reason_list[id_val] = f"{id_val} not found in policy"
                continue
            matching_policy_container = policy[idx]

            # copy so we can delete fields and not affect the original data
            # structure
            container1 = copy.deepcopy(matching_policy_container)
            container2 = copy.deepcopy(container)

            # the ID does not matter so delete them from comparison
            container1.pop(config.POLICY_FIELD_CONTAINERS_ID, None)
            container2.pop(config.POLICY_FIELD_CONTAINERS_ID, None)
            # env vars will be compared later so delete them from this
            # comparison
            container1.pop(config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS, None)
            container2.pop(config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS, None)

            container_diff = compare_containers(container1, container2)

            # for sidecar validation, it's fine if the policy has
            # more things defined than the image, so we can take
            # those out of the diff because it would not hinder deployment
            if sidecar_validation:
                for k in list(container_diff.keys()):
                    if "removed" in k:
                        container_diff.pop(k)
            if container_diff != {}:
                reason_list[id_val] = container_diff

            env_reason_list = compare_env_vars(
                id_val,
                case_insensitive_dict_get(
                    matching_policy_container,
                    config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS,
                ),
                case_insensitive_dict_get(
                    container, config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS
                ),
            )

            # merge the output of checking env vars with the original reason
            # list
            for key, value in env_reason_list.items():
                if key not in reason_list:
                    reason_list[key] = {}
                reason_list[key].update(value)
        is_valid = not bool(reason_list)
        return is_valid, reason_list

    def compare_fragments(self) -> Dict[str, Any]:
        """Utility method: see if the fragments in the policy are the defaults"""
        diff = deepdiff.DeepDiff(
            self._existing_fragments, config.DEFAULT_REGO_FRAGMENTS, ignore_order=True
        )
        return readable_diff(diff)

    def save_to_file(
        self,
        file_path: str,
        output_type: OutputType = OutputType.DEFAULT,
    ) -> None:
        output = self.get_serialized_output(output_type)
        os_util.write_str_to_file(file_path, output)

    def _policy_serialization(self, pretty_print=False) -> str:
        policy = []
        regular_container_images = self.get_images()

        is_sidecars = True
        for image in regular_container_images:
            is_sidecars = is_sidecars and is_sidecar(image.containerImage)
            image_dict = image.get_policy_json()
            policy.append(image_dict)

        if not is_sidecars:
            # add in the default containers that have their hashes pre-computed
            policy += copy.deepcopy(config.DEFAULT_CONTAINERS)
            if self._disable_stdio:
                for container in policy:
                    container[config.POLICY_FIELD_CONTAINERS_ELEMENTS_ALLOW_STDIO_ACCESS] = False

        if pretty_print:
            return pretty_print_func(policy)
        return print_func(policy)

    # pylint: disable=R0914, R0915
    def populate_policy_content_for_all_images(
        self, individual_image=False, tar_mapping=None, faster_hashing=False,
    ) -> None:
        # suppress warning which will break the progress bar
        warnings.filterwarnings(
            action="ignore", message="unclosed", category=ResourceWarning
        )

        tar_location = ""
        if isinstance(tar_mapping, str):
            tar_location = tar_mapping
        proxy = self._get_rootfs_proxy()
        container_images = self.get_images()

        # total tasks to complete is number of images to pull and get layers
        # (i.e. total images * 2 tasks)
        _TOTAL = 2 * len(container_images)

        with tqdm(
            total=_TOTAL,
            desc="Pulling and hashing images...",
            unit="percent",
            colour="green",
            leave=True,
        ) as progress:
            # make a message queue so we don't interrupt the printing of the
            # progress bar
            message_queue = []
            # populate regular container images(s)
            for image in container_images:
                image.parse_all_parameters_and_variables(AciPolicy.all_params, AciPolicy.all_vars)
                image_name = f"{image.base}:{image.tag}"
                image_info, tar = get_image_info(progress, message_queue, tar_mapping, image)

                # verify and populate the working directory property
                if not image.get_working_dir() and image_info:
                    workingDir = image_info.get("WorkingDir")
                    image.set_working_dir(
                        workingDir if workingDir else config.DEFAULT_WORKING_DIR
                    )

                if (
                    isinstance(image, UserContainerImage) or individual_image
                ) and image_info:
                    # verify and populate the startup command
                    if not image.get_command():
                        # precondition: image_info exists. this is shown by the
                        # "and image_info" earlier
                        command = image_info.get("Cmd")

                        # since we don't have an entrypoint field,
                        # it needs to be added to the front of the command
                        # array
                        entrypoint = image_info.get("Entrypoint")
                        if entrypoint and command:
                            command = entrypoint + command
                        elif entrypoint and not command:
                            command = entrypoint
                        image.set_command(command)

                    # merge envs for user container image
                    envs = image_info.get("Env") or []
                    env_names = [
                        env_var[
                            config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE
                        ].split("=")[0]
                        for env_var in image.get_environment_rules()
                    ]

                    for env in envs:
                        name, value = env.split("=", 1)
                        # when user set environment variables conflict with the ones read from image, always
                        # keep user set environment variables
                        if name not in env_names:
                            image.get_environment_rules().append(
                                {
                                    config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE: f"{name}={value}",
                                    config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_STRATEGY: "string",
                                    config.POLICY_FIELD_CONTAINERS_ELEMENTS_REQUIRED: False,
                                }
                            )

                    # merge signals for user container image
                    signals = image_info.get("StopSignal")
                    if signals:
                        image.set_signals(signals)

                    if (
                        not deepdiff.DeepDiff(image.get_user(), config.DEFAULT_USER, ignore_order=True)
                        and image_info.get("User") != ""
                    ):
                        # valid values are in the form "user", "user:group", "uid", "uid:gid", "user:gid", "uid:group"
                        # where each entry is either a string or an unsigned integer
                        # "" means any user (use default)
                        # TO-DO figure out why groups is a list
                        user = copy.deepcopy(config.DEFAULT_USER)
                        parts = image_info.get("User").split(":", 1)

                        strategy = ["name", "name"]
                        if parts[0].isdigit():
                            strategy[0] = "id"
                        user[config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_USER_IDNAME] = {
                            config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_PATTERN: parts[0],
                            config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_STRATEGY: strategy[0]
                        }
                        if len(parts) == 2:
                            # group also specified
                            if parts[1].isdigit():
                                strategy[1] = "id"
                            user[config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_GROUP_IDNAMES][0] = {
                                config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_PATTERN: parts[1],
                                config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_STRATEGY: strategy[1]
                            }
                        image.set_user(user)

                # populate tar location
                if isinstance(tar_mapping, dict):
                    tar_location = get_tar_location_from_mapping(tar_mapping, image_name)
                # populate layer info
                image.set_layers(proxy.get_policy_image_layers(
                    image.base, image.tag, tar_location=tar_location if tar else "", faster_hashing=faster_hashing
                ))

                progress.update()
            progress.close()
            self.close()

            # unload the message queue
            for message in message_queue:
                logger.warning(message)

    def get_images(self) -> List[ContainerImage]:
        return self._images

    def pull_image(self, image: ContainerImage) -> Any:
        client = self._get_docker_client()
        return client.images.pull(image.base, image.tag)


def load_policy_from_arm_template_str(
    template_data: str,
    parameter_data: str,
    infrastructure_svn: str = None,
    debug_mode: bool = False,
    disable_stdio: bool = False,
    approve_wildcards: bool = False,
) -> List[AciPolicy]:
    """Function that converts ARM template string to an ACI Policy"""
    input_arm_json = os_util.load_json_from_str(template_data)

    input_parameter_json = {}
    if parameter_data:
        input_parameter_json = os_util.load_json_from_str(parameter_data)

    # find the image names and extract them from the template
    arm_resources = case_insensitive_dict_get(
        input_arm_json, config.ACI_FIELD_RESOURCES
    )

    if not arm_resources:
        eprint(f"Field [{config.ACI_FIELD_RESOURCES}] is empty or cannot be found")

    aci_list = [
        item
        for item in arm_resources
        if item["type"] == config.ACI_FIELD_TEMPLATE_RESOURCE_LABEL
    ]

    if not aci_list:
        eprint(
            f'Field ["type"] must contain value of ["{config.ACI_FIELD_TEMPLATE_RESOURCE_LABEL}"]'
        )

    # extract variables and parameters in case we need to do substitutions
    # while searching for image names
    all_params = (
        case_insensitive_dict_get(input_arm_json, config.ACI_FIELD_TEMPLATE_PARAMETERS)
        or {}
    )

    get_values_for_params(input_parameter_json, all_params)

    AciPolicy.all_params = all_params
    AciPolicy.all_vars = case_insensitive_dict_get(input_arm_json, config.ACI_FIELD_TEMPLATE_VARIABLES) or {}

    container_groups = []

    for resource in aci_list:
        # initialize the list of containers we need to generate policies for
        containers = []
        existing_containers = None
        fragments = None

        container_group_properties = case_insensitive_dict_get(
            resource, config.ACI_FIELD_TEMPLATE_PROPERTIES
        )
        container_list = case_insensitive_dict_get(
            container_group_properties, config.ACI_FIELD_TEMPLATE_CONTAINERS
        )

        if not container_list:
            eprint(
                f'Field ["{config.POLICY_FIELD_CONTAINERS}"] must be a list of {config.POLICY_FIELD_CONTAINERS}'
            )

        init_container_list = case_insensitive_dict_get(
            container_group_properties, config.ACI_FIELD_TEMPLATE_INIT_CONTAINERS
        )
        # add init containers to the list of other containers since they aren't treated differently
        # in the security policy
        if init_container_list:
            container_list.extend(init_container_list)

        existing_containers, fragments = extract_confidential_properties(
            container_group_properties
        )

        rego_fragments = copy.deepcopy(config.DEFAULT_REGO_FRAGMENTS)
        if infrastructure_svn:
            # assumes the first DEFAULT_REGO_FRAGMENT is always the
            # infrastructure fragment
            rego_fragments[0][
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_MINIMUM_SVN
            ] = infrastructure_svn

        volumes = (
            case_insensitive_dict_get(
                container_group_properties, config.ACI_FIELD_TEMPLATE_VOLUMES
            )
            or []
        )
        if volumes and not isinstance(volumes, list):
            # parameter definition is in parameter file but not arm template
            eprint(f'Parameter ["{config.ACI_FIELD_TEMPLATE_VOLUMES}"] must be a list')

        for container in container_list:
            image_properties = case_insensitive_dict_get(
                container, config.ACI_FIELD_TEMPLATE_PROPERTIES
            )
            image_name = case_insensitive_dict_get(
                image_properties, config.ACI_FIELD_TEMPLATE_IMAGE
            )

            if not image_name:
                eprint(
                    f'Field ["{config.ACI_FIELD_TEMPLATE_PARAMETERS}"] is empty or cannot be found'
                )

            exec_processes = []
            extract_probe(exec_processes, image_properties, config.ACI_FIELD_CONTAINERS_READINESS_PROBE)
            extract_probe(exec_processes, image_properties, config.ACI_FIELD_CONTAINERS_LIVENESS_PROBE)

            containers.append(
                {
                    config.ACI_FIELD_CONTAINERS_ID: image_name,
                    config.ACI_FIELD_CONTAINERS_CONTAINERIMAGE: image_name,
                    config.ACI_FIELD_CONTAINERS_ENVS: process_env_vars_from_template(
                        AciPolicy.all_params, AciPolicy.all_vars, image_properties, approve_wildcards),
                    config.ACI_FIELD_CONTAINERS_COMMAND: case_insensitive_dict_get(
                        image_properties, config.ACI_FIELD_TEMPLATE_COMMAND
                    )
                    or [],
                    config.ACI_FIELD_CONTAINERS_MOUNTS: process_mounts(image_properties, volumes),
                    config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES: exec_processes
                    + config.DEBUG_MODE_SETTINGS.get("execProcesses")
                    if debug_mode
                    else exec_processes,
                    config.ACI_FIELD_CONTAINERS_SIGNAL_CONTAINER_PROCESSES: [],
                    config.ACI_FIELD_CONTAINERS_ALLOW_STDIO_ACCESS: not disable_stdio,
                    config.ACI_FIELD_CONTAINERS_SECURITY_CONTEXT: case_insensitive_dict_get(
                        image_properties, config.ACI_FIELD_TEMPLATE_SECURITY_CONTEXT
                    ),
                }
            )

        container_groups.append(
            AciPolicy(
                {
                    config.ACI_FIELD_VERSION: "1.0",
                    config.ACI_FIELD_CONTAINERS: containers,
                    config.ACI_FIELD_TEMPLATE_CCE_POLICY: existing_containers,
                },
                disable_stdio=disable_stdio,
                rego_fragments=rego_fragments,
                # fallback to default fragments if the policy is not present
                existing_rego_fragments=fragments,
                debug_mode=debug_mode,
            )
        )
    return container_groups


def load_policy_from_arm_template_file(
    infrastructure_svn: str,
    template_path: str,
    parameter_path: str,
    debug_mode: bool = False,
    disable_stdio: bool = False,
    approve_wildcards: bool = False,
) -> List[AciPolicy]:
    """Utility function: generate policy object from given arm template and parameter file paths"""
    input_arm_json = os_util.load_str_from_file(template_path)
    input_parameter_json = None
    if parameter_path:
        input_parameter_json = os_util.load_str_from_file(parameter_path)
    return load_policy_from_arm_template_str(
        input_arm_json, input_parameter_json, infrastructure_svn,
        debug_mode=debug_mode, disable_stdio=disable_stdio, approve_wildcards=approve_wildcards,
    )


def load_policy_from_file(path: str, debug_mode: bool = False) -> AciPolicy:
    """Utility function: generate policy object from given json file path"""
    policy_input_json = os_util.load_str_from_file(path)

    return load_policy_from_str(policy_input_json, debug_mode=debug_mode, )


def load_policy_from_image_name(
    image_names: List[str] or str, debug_mode: bool = False, disable_stdio: bool = False
) -> AciPolicy:
    # can either take a list of image names or a single image name
    if isinstance(image_names, str):
        image_names = [image_names]

    client = docker.from_env()
    containers = []
    for image_name in image_names:
        container = {}
        # assign just the fields that are expected
        # the values will come when calling
        # populate_policy_content_for_all_images later on
        container[config.ACI_FIELD_TEMPLATE_COMMAND] = []
        container[config.ACI_FIELD_CONTAINERS_ENVS] = []

        # assign image name to ID field
        container[config.ACI_FIELD_CONTAINERS_ID] = image_name

        container[config.ACI_FIELD_CONTAINERS_CONTAINERIMAGE] = image_name
        container[config.ACI_FIELD_CONTAINERS_ALLOW_STDIO_ACCESS] = not disable_stdio

        containers.append(container)
    client.close()

    return AciPolicy(
        {
            config.ACI_FIELD_VERSION: "1.0",
            config.ACI_FIELD_CONTAINERS: containers,
            # fallback to default fragments if the policy is not present
            config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS: config.DEFAULT_REGO_FRAGMENTS,
        },
        debug_mode=debug_mode,
        disable_stdio=disable_stdio,
    )


def load_policy_from_str(data: str, debug_mode: bool = False) -> AciPolicy:
    """Utility function: generate policy object from given json string"""
    policy_input_json = os_util.load_json_from_str(data)
    containers = case_insensitive_dict_get(
        policy_input_json, config.ACI_FIELD_CONTAINERS
    )

    rego_fragments = case_insensitive_dict_get(
        policy_input_json, config.ACI_FIELD_CONTAINERS_REGO_FRAGMENTS
    )

    if rego_fragments:
        if not isinstance(rego_fragments, list):
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                + f'["{config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS}"]'
                + "can only be a list."
            )

        for fragment in rego_fragments:
            feed = case_insensitive_dict_get(
                fragment, config.ACI_FIELD_CONTAINERS_REGO_FRAGMENTS_FEED
            )
            if not isinstance(feed, str):
                eprint(
                    f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                    + f'["{config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS}"]'
                    + f'["{config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS}"]'
                    + "can only be a string value."
                )

            iss = case_insensitive_dict_get(
                fragment, config.ACI_FIELD_CONTAINERS_REGO_FRAGMENTS_ISS
            )
            if not isinstance(iss, str):
                eprint(
                    f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                    + f'["{config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS}"]'
                    + f'["{config.ACI_FIELD_CONTAINERS_REGO_FRAGMENTS_ISS}"]'
                    + "can only be a string value."
                )

            minimum_svn = case_insensitive_dict_get(
                fragment, config.ACI_FIELD_CONTAINERS_REGO_FRAGMENTS_MINIMUM_SVN
            )
            if not isinstance(minimum_svn, str):
                eprint(
                    f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                    + f'["{config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS}"]'
                    + f'["{config.ACI_FIELD_CONTAINERS_REGO_FRAGMENTS_MINIMUM_SVN}"]'
                    + "can only be a string value."
                )

            includes = case_insensitive_dict_get(
                fragment, config.ACI_FIELD_CONTAINERS_REGO_FRAGMENTS_INCLUDES
            )
            if not isinstance(includes, list):
                eprint(
                    f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                    + f'["{config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS}"]'
                    + f'["{config.ACI_FIELD_CONTAINERS_REGO_FRAGMENTS_INCLUDES}"]'
                    + "can only be a list."
                )

    if not containers:
        eprint(f'Field ["{config.ACI_FIELD_CONTAINERS}"] is empty or can not be found.')

    for container in containers:
        image_name = case_insensitive_dict_get(
            container, config.ACI_FIELD_CONTAINERS_CONTAINERIMAGE
        )

        if not image_name:
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS_CONTAINERIMAGE}"] is empty or can not be found.'
            )
        container[config.ACI_FIELD_CONTAINERS_ID] = image_name

        # set the fields that are present in the container but not in the
        # config
        container[config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES] = container.get(
            config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES, []) + (
            config.DEBUG_MODE_SETTINGS.get("execProcesses") if debug_mode else []
        )
        container[config.ACI_FIELD_CONTAINERS_SIGNAL_CONTAINER_PROCESSES] = []

    return AciPolicy(
        policy_input_json,
        rego_fragments=rego_fragments or config.DEFAULT_REGO_FRAGMENTS,
        debug_mode=debug_mode,
    )
