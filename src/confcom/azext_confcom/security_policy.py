# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import json
import warnings
from enum import Enum, auto
from typing import Any, Dict, List, Tuple, Union

import deepdiff
from azext_confcom import config, os_util
from azext_confcom.container import ContainerImage, UserContainerImage
from azext_confcom.errors import eprint
from azext_confcom.fragment_util import sanitize_fragment_fields
from azext_confcom.oras_proxy import create_list_of_standalone_imports
from azext_confcom.rootfs_proxy import SecurityPolicyProxy
from azext_confcom.template_util import (case_insensitive_dict_get,
                                         compare_env_vars,
                                         convert_config_v0_to_v1,
                                         convert_to_pod_spec,
                                         decompose_confidential_properties,
                                         detect_old_format,
                                         extract_confidential_properties,
                                         extract_lifecycle_hook, extract_probe,
                                         extract_standalone_fragments,
                                         filter_non_pod_resources,
                                         get_container_diff, get_diff_size,
                                         get_image_info,
                                         get_tar_location_from_mapping,
                                         get_values_for_params,
                                         get_volume_claim_templates,
                                         is_sidecar, pretty_print_func,
                                         print_func, process_configmap,
                                         process_env_vars_from_config,
                                         process_env_vars_from_template,
                                         process_env_vars_from_yaml,
                                         process_fragment_imports,
                                         process_mounts,
                                         process_mounts_from_config,
                                         readable_diff)
from knack.log import get_logger
from tqdm import tqdm

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
        is_vn2: bool = False,
        fragment_contents: Any = None,
    ) -> None:
        self._rootfs_proxy = None
        self._policy_str = None
        self._policy_str_pp = None
        self._disable_stdio = disable_stdio
        self._fragments = rego_fragments
        self._existing_fragments = existing_rego_fragments
        self._api_version = config.API_VERSION
        self._fragment_contents = fragment_contents

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
        if containers is None:
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS}"] is empty or can not be found.'
            )

        container_results = []

        # parse and generate each container, either user or sidecar
        for c in containers:
            if not is_sidecar(c[config.POLICY_FIELD_CONTAINERS_ID]):
                container_image = UserContainerImage.from_json(c, is_vn2=is_vn2)
            else:
                container_image = ContainerImage.from_json(c)
            container_image.parse_all_parameters_and_variables(self.all_params, self.all_vars)
            container_results.append(container_image)

        self._images = container_results

    def __enter__(self) -> Any:
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback) -> None:
        return None

    def _get_rootfs_proxy(self) -> SecurityPolicyProxy:
        if not self._rootfs_proxy:
            self._rootfs_proxy = SecurityPolicyProxy()

        return self._rootfs_proxy

    def set_fragment_contents(self, fragment_contents: List[str]) -> None:
        self._fragment_contents = fragment_contents

    def get_fragments(self) -> List[str]:
        return self._fragments or []

    def get_serialized_output(
        self,
        output_type: OutputType = OutputType.DEFAULT,
        rego_boilerplate=True,
        omit_id: bool = False,
        include_sidecars: bool = True,
    ):
        # error check the output type
        if not isinstance(output_type, Enum) or output_type.value not in [item.value for item in OutputType]:
            eprint("Unknown output type for serialization.")

        policy_str = self._policy_serialization(
            output_type == OutputType.PRETTY_PRINT, include_sidecars=include_sidecars, omit_id=omit_id
        )

        if rego_boilerplate:
            policy_str = self._add_rego_boilerplate(policy_str)

        # if we're not outputting base64
        if output_type in (OutputType.RAW, OutputType.PRETTY_PRINT):
            return policy_str
        # encode to base64
        return os_util.str_to_base64(policy_str)

    def generate_fragment(self, namespace: str, svn: str, output_type: int, omit_id: bool = False) -> str:
        # get rid of fields that aren't strictly needed for the fragment import
        sanitized_fragments = sanitize_fragment_fields(self.get_fragments())
        return config.CUSTOMER_REGO_FRAGMENT % (
            namespace,
            pretty_print_func(svn),
            pretty_print_func(sanitized_fragments),
            self.get_serialized_output(output_type, rego_boilerplate=False, include_sidecars=False, omit_id=omit_id),
        )

    def _add_rego_boilerplate(self, output: str) -> str:
        # determine if we're outputting for a sidecar or not
        if self._images and self._images[0].get_id() and is_sidecar(self._images[0].get_id()):
            return config.SIDECAR_REGO_POLICY % (
                pretty_print_func(self._api_version),
                output
            )

        # get rid of fields that aren't strictly needed for the fragment import
        sanitized_fragments = sanitize_fragment_fields(self.get_fragments())
        return config.CUSTOMER_REGO_POLICY % (
            pretty_print_func(self._api_version),
            pretty_print_func(sanitized_fragments),
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

        for container in policy_content:
            # the test sets the sidecar to have the name be the same as the ID, so we need to simulate that
            container[config.ACI_FIELD_CONTAINERS_NAME] = container[config.ACI_FIELD_CONTAINERS_ID]
        # done this way instead of self.validate() because the input.json is
        # the source of truth

        return policy.validate(policy_content, sidecar_validation=True)

    # pylint: disable=too-many-locals
    def validate(self, policy, sidecar_validation=False) -> Tuple[bool, Dict]:
        """Utility method: general method to compare two policies.
        One being the current object and the other is passed in as a parameter.

        This is done by comparing first the container names (IDs) and then
        the contents of the containers with special logic for environment variables,
        since they can use regular expressions.

        The minimum difference is used to match up the containers in the policy vs
        the containers in the ARM template. Afterwards, the differences are compiled
        and returned as a dictionary organized by container name."""
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
        policy_names = [
            case_insensitive_dict_get(i, config.POLICY_FIELD_CONTAINERS_NAME)
            for i in policy
        ]

        for container in arm_containers:
            # see if the IDs match with any container in the policy

            id_val = case_insensitive_dict_get(container, config.ACI_FIELD_CONTAINERS_ID)
            container_name = case_insensitive_dict_get(
                container,
                config.POLICY_FIELD_CONTAINERS_NAME
            )

            # container names are required for valid k8s yamls and ARM templates. So this would only happen
            # in a future scenario where we enable diff mode for pure json files and the user does not provide
            # a name for the container
            if id_val is None and container_name is None:
                raise ValueError(
                    (
                        "Container ID and Name cannot both be None to use diff mode. "
                        "Try adding a name to the container and regenerate the CCE policy."
                    )
                )

            idx_arr = [i for i, item in enumerate(policy_ids) if item == id_val]
            idx_arr_name = [i for i, item in enumerate(policy_names) if item == container_name]
            set_idx = set(idx_arr + idx_arr_name)

            if len(set_idx) == 0:
                reason_list[container_name] = f"{id_val} not found in policy"
                continue

            temp_diff_list = []
            for idx in set_idx:
                temp_diff = {}
                matching_policy_container = policy[idx]

                diff_values = get_container_diff(matching_policy_container, container)
                # label the diff with the ID so it can be merged
                # with the env vars and other container diffs
                temp_diff[container_name] = diff_values
                # for sidecar validation, it's fine if the policy has
                # more things defined than the image, so we can take
                # those out of the diff because it would not hinder deployment
                if sidecar_validation:
                    for k in list(temp_diff.keys()):
                        if "removed" in k:
                            temp_diff.pop(k)

                env_reason_list = compare_env_vars(
                    container_name,
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
                    if key not in temp_diff:
                        temp_diff[key] = {}
                    temp_diff[key].update(value)

                temp_diff_list.append(copy.deepcopy(temp_diff))

            diff_sizes = [get_diff_size(diff) for diff in copy.deepcopy(temp_diff_list)]

            if diff_sizes.count(0) >= 1:
                continue

            reason_list.update(temp_diff_list[diff_sizes.index(min(diff_sizes))])

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

    def _policy_serialization(self, pretty_print=False, include_sidecars: bool = True, omit_id: bool = False) -> str:
        policy = []
        regular_container_images = self.get_images()

        # in the case where fragments cover all the customer containers, we still need the pause container
        is_sidecars = all(is_sidecar(image.containerImage) for image in regular_container_images)
        for image in regular_container_images:
            image_dict = image.get_policy_json(omit_id=omit_id)
            policy.append(image_dict)
        if (not is_sidecars or len(regular_container_images) == 0) and include_sidecars:
            # add in the default containers that have their hashes pre-computed
            policy += copy.deepcopy(config.DEFAULT_CONTAINERS)
            if self._disable_stdio:
                for container in policy:
                    container[config.POLICY_FIELD_CONTAINERS_ELEMENTS_ALLOW_STDIO_ACCESS] = False

        if pretty_print:
            return pretty_print_func(policy)
        return print_func(policy)

    # pylint: disable=R0914, R0915, R0912
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

        if isinstance(tar_mapping, str) and len(container_images) > 1:
            eprint(
                "Cannot have only one tar file when generating policy for multiple images. " +
                "Please create a json file that maps image name to tar file path"
            )

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
                image_name = f"{image.base}:{image.tag}"
                logger.info("Processing image: %s", image_name)
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
                    # verify and populate the startup command for VN2 since "command" and "args"
                    # can be set independent of each other. These names correspond to what we call
                    # "entrypoint" and "command"
                    # entrypoint should be None for everything except VN2
                    image_entrypoint = image.get_entrypoint()
                    if image_entrypoint is not None:
                        image_command = image.get_command()
                        manifest_entrypoint = image_info.get("Entrypoint") or []
                        manifest_command = image_info.get("Cmd") or []
                        # pylint: disable=line-too-long
                        # this describes the potential options that can happen: https://unofficial-kubernetes.readthedocs.io/en/latest/concepts/configuration/container-command-args/
                        if image_entrypoint and not image_command:
                            command = image_entrypoint
                        elif image_entrypoint and image_command:
                            command = image_entrypoint + image_command
                        elif image_command:
                            command = manifest_entrypoint + image_command
                        else:
                            command = manifest_entrypoint + manifest_command
                        image.set_command(command)

                    elif not image.get_command():
                        # precondition: image_info exists. this is shown by the
                        # "and image_info" earlier
                        command = image_info.get("Cmd")

                        # since we don't have an entrypoint field,
                        # it needs to be added to the front of the command
                        # array
                        # update: there is now an entrypoint field for VN2 use cases
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
                        and (image_info.get("User") != "" and image_info.get("User") is not None)
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

                # should have all fragments before this point
                if self._fragment_contents and self.should_eliminate_container_covered_by_fragments(image):
                    # these containers will get taken out later in the function
                    # since they are covered by a fragment
                    logger.info("Container covered by fragment: %s", image_name)
                    continue

                # populate tar location
                if isinstance(tar_mapping, dict):
                    tar_location = get_tar_location_from_mapping(tar_mapping, image_name)
                # populate layer info
                image.set_layers(proxy.get_policy_image_layers(
                    image.base, image.tag, tar_location=tar_location if tar else "", faster_hashing=faster_hashing
                ))

                progress.update()
            progress.close()

            # unload the message queue
            for message in message_queue:
                logger.warning(message)

            out_images = list(filter(lambda image: image.get_layers(), self.get_images()))
            self.set_images(out_images)

    def should_eliminate_container_covered_by_fragments(self, image):
        for fragment_image in self._fragment_contents:
            # we're not comparing layers to save computation time
            fragment_image["layers"] = []
            # TODO: make this print a warning if there is a fragment image that's close
            # save some computation time by checking if the image tag is the same first
            container_name = case_insensitive_dict_get(
                fragment_image,
                config.POLICY_FIELD_CONTAINERS_NAME
            )
            fragment_image_id = fragment_image.get(config.ACI_FIELD_CONTAINERS_ID)
            if isinstance(fragment_image_id, str) and ":" not in fragment_image_id:
                fragment_image_id = f"{fragment_image_id}:latest"
            if (
                fragment_image_id == f"{image.base}:{image.tag}" or
                container_name == image.get_name()
            ):
                image_policy = image.get_policy_json()

                container_diff = get_container_diff(fragment_image, image_policy)

                # if the rest of the container is good, check the env vars
                if not container_diff:
                    env_reason_list = compare_env_vars(
                        fragment_image_id,
                        case_insensitive_dict_get(
                            fragment_image,
                            config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS,
                        ),
                        case_insensitive_dict_get(
                            image_policy, config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS
                        ),
                    )

                    # if the env vars are the same, then we can eliminate the container
                    if not env_reason_list:
                        return True
        return False

    def get_images(self) -> List[ContainerImage]:
        return self._images

    def set_images(self, images: List[ContainerImage]) -> None:
        self._images = images


# pylint: disable=R0914,
def load_policy_from_arm_template_str(
    template_data: str,
    parameter_data: str,
    infrastructure_svn: str = None,
    debug_mode: bool = False,
    disable_stdio: bool = False,
    approve_wildcards: bool = False,
    diff_mode: bool = False,
    rego_imports: Any = None,
    fragment_contents: Any = None,
    exclude_default_fragments: bool = False,
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
        if item["type"] in config.ACI_FIELD_SUPPORTED_RESOURCES
    ]

    if not aci_list:
        eprint(
            f'Field ["type"] must contain one of {config.ACI_FIELD_SUPPORTED_RESOURCES}'
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
        exclude_default_fragments_this_group = exclude_default_fragments

        tags = case_insensitive_dict_get(resource, config.ACI_FIELD_TEMPLATE_TAGS)
        if tags:
            exclude_default_fragments_this_group = case_insensitive_dict_get(tags, config.ACI_FIELD_TEMPLATE_ZERO_SIDECAR)
            if isinstance(exclude_default_fragments_this_group, str):
                exclude_default_fragments_this_group = exclude_default_fragments_this_group.lower() == "true"

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

        # these are standalone fragments coming from the ARM template itself
        standalone_fragments = extract_standalone_fragments(container_group_properties)
        if standalone_fragments:
            standalone_fragment_imports = create_list_of_standalone_imports(standalone_fragments)
            unique_imports = set(rego_imports)
            for fragment in standalone_fragment_imports:
                if fragment not in unique_imports:
                    rego_imports.append(fragment)
                    unique_imports.add(fragment)

        try:
            existing_containers, fragments = extract_confidential_properties(
                container_group_properties
            )
        except ValueError as e:
            if diff_mode:
                # In diff mode, we raise an error if the base64 policy is malformed
                eprint(f"Unable to decode existing policy. Please check the base64 encoding.\n{e}")
            else:
                # In non-diff mode, we ignore the error and proceed without the policy
                existing_containers, fragments = ([], [])

        rego_fragments = copy.deepcopy(config.DEFAULT_REGO_FRAGMENTS) if not exclude_default_fragments_this_group else []
        if infrastructure_svn:
            # assumes the first DEFAULT_REGO_FRAGMENT is always the
            # infrastructure fragment
            rego_fragments[0][
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_MINIMUM_SVN
            ] = infrastructure_svn
        if rego_imports:
            # error check the rego imports for invalid data types
            processed_imports = process_fragment_imports(rego_imports)
            rego_fragments.extend(processed_imports)

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

            # this is guaranteed unique for a valid ARM template
            container_name = case_insensitive_dict_get(
                container, config.ACI_FIELD_CONTAINERS_NAME
            )

            if not image_name:
                eprint(
                    f'Field ["{config.ACI_FIELD_TEMPLATE_IMAGE}"] is empty or cannot be found'
                )

            exec_processes = []
            extract_probe(exec_processes, image_properties, config.ACI_FIELD_CONTAINERS_READINESS_PROBE)
            extract_probe(exec_processes, image_properties, config.ACI_FIELD_CONTAINERS_LIVENESS_PROBE)

            containers.append(
                {
                    config.ACI_FIELD_CONTAINERS_ID: image_name,
                    config.ACI_FIELD_CONTAINERS_NAME: container_name,
                    config.ACI_FIELD_CONTAINERS_CONTAINERIMAGE: image_name,
                    config.ACI_FIELD_CONTAINERS_ENVS: process_env_vars_from_template(
                        AciPolicy.all_params, AciPolicy.all_vars, image_properties, approve_wildcards),
                    config.ACI_FIELD_CONTAINERS_COMMAND: case_insensitive_dict_get(
                        image_properties, config.ACI_FIELD_TEMPLATE_COMMAND
                    )
                    or [],
                    config.ACI_FIELD_CONTAINERS_MOUNTS: process_mounts(image_properties, volumes)
                    + process_configmap(image_properties),
                    config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES: exec_processes
                    + config.DEBUG_MODE_SETTINGS.get(config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES)
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
                fragment_contents=fragment_contents,
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
    diff_mode: bool = False,
    rego_imports: list = None,
    fragment_contents: list = None,
    exclude_default_fragments: bool = False,
) -> List[AciPolicy]:
    """Utility function: generate policy object from given arm template and parameter file paths"""
    input_arm_json = os_util.load_str_from_file(template_path)
    input_parameter_json = None
    if parameter_path:
        input_parameter_json = os_util.load_str_from_file(parameter_path)
    return load_policy_from_arm_template_str(
        input_arm_json,
        input_parameter_json,
        infrastructure_svn,
        debug_mode=debug_mode,
        disable_stdio=disable_stdio,
        approve_wildcards=approve_wildcards,
        rego_imports=rego_imports,
        diff_mode=diff_mode,
        fragment_contents=fragment_contents,
        exclude_default_fragments=exclude_default_fragments,
    )


def load_policy_from_image_name(
    image_names: Union[List[str], str], debug_mode: bool = False, disable_stdio: bool = False
) -> AciPolicy:
    # can either take a list of image names or a single image name
    if isinstance(image_names, str):
        image_names = [image_names]

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
        container[config.ACI_FIELD_CONTAINERS_NAME] = image_name

        container[config.ACI_FIELD_CONTAINERS_CONTAINERIMAGE] = image_name
        container[config.ACI_FIELD_CONTAINERS_ALLOW_STDIO_ACCESS] = not disable_stdio

        containers.append(container)

    return AciPolicy(
        {
            config.ACI_FIELD_VERSION: "1.0",
            config.ACI_FIELD_CONTAINERS: containers,
        },
        debug_mode=debug_mode,
        disable_stdio=disable_stdio,
    )


def load_policy_from_json_file(
    data: str,
    debug_mode: bool = False,
    disable_stdio: bool = False,
    infrastructure_svn: str = None,
    exclude_default_fragments: bool = False,
) -> AciPolicy:
    json_content = os_util.load_str_from_file(data)
    return load_policy_from_json(
        json_content,
        debug_mode=debug_mode,
        disable_stdio=disable_stdio,
        infrastructure_svn=infrastructure_svn,
        exclude_default_fragments=exclude_default_fragments
    )


def load_policy_from_json(
    data: str,
    debug_mode: bool = False,
    disable_stdio: bool = False,
    infrastructure_svn: str = None,
    exclude_default_fragments: bool = False,
) -> AciPolicy:
    output_containers = []
    # 1) Parse incoming string as JSON
    policy_input_json = os_util.load_json_from_str(data)
    if not isinstance(policy_input_json, dict):
        eprint("Input JSON is not a valid dictionary")

    is_old_format = detect_old_format(policy_input_json)
    if is_old_format:
        policy_input_json = convert_config_v0_to_v1(policy_input_json)

    # 2) Extract top-level fields
    input_containers = case_insensitive_dict_get(
        policy_input_json, config.ACI_FIELD_CONTAINERS
    ) or []

    version = case_insensitive_dict_get(
        policy_input_json, config.ACI_FIELD_VERSION
    )

    if not version:
        version = "1.0"
        policy_input_json[config.ACI_FIELD_VERSION] = "1.0"

    rego_fragments = case_insensitive_dict_get(
        policy_input_json, config.ACI_FIELD_CONTAINERS_REGO_FRAGMENTS
    ) or []

    scenario = case_insensitive_dict_get(
        policy_input_json, config.ACI_FIELD_SCENARIO
    ) or ""

    # 3) Process rego_fragments
    standalone_rego_fragments = case_insensitive_dict_get(
        policy_input_json, config.ACI_FIELD_TEMPLATE_STANDALONE_REGO_FRAGMENTS
    )

    if rego_fragments:
        process_fragment_imports(rego_fragments)

    if standalone_rego_fragments:
        rego_fragments.extend(standalone_rego_fragments)

    if not input_containers and not rego_fragments:
        eprint(
            f'Field ["{config.ACI_FIELD_CONTAINERS}"]' +
            f' and field ["{config.ACI_FIELD_CONTAINERS_REGO_FRAGMENTS}"] can not both be empty.'
        )

    for container in input_containers:
        container_properties = case_insensitive_dict_get(
            container, config.ACI_FIELD_TEMPLATE_PROPERTIES
        )

        image_name = case_insensitive_dict_get(
            container_properties, config.ACI_FIELD_TEMPLATE_IMAGE
        )

        if not image_name:
            eprint(
                f'Field ["{config.ACI_FIELD_TEMPLATE_IMAGE}"] is empty or cannot be found'
            )

        container_name = case_insensitive_dict_get(
            container, config.ACI_FIELD_CONTAINERS_NAME
        ) or image_name

        if not container_name:
            eprint(f'Field ["{config.ACI_FIELD_CONTAINERS_NAME}"] is empty or cannot be found')

        exec_processes = case_insensitive_dict_get(
            container_properties, config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES
        ) or []

        # add the signal section if it's not present
        for exec_process in exec_processes:
            if config.ACI_FIELD_CONTAINERS_SIGNAL_CONTAINER_PROCESSES not in exec_process:
                exec_process[config.ACI_FIELD_CONTAINERS_SIGNAL_CONTAINER_PROCESSES] = []

        extract_probe(exec_processes, container_properties, config.ACI_FIELD_CONTAINERS_READINESS_PROBE)
        extract_probe(exec_processes, container_properties, config.ACI_FIELD_CONTAINERS_LIVENESS_PROBE)

        container_security_context = case_insensitive_dict_get(
            container_properties, config.ACI_FIELD_TEMPLATE_SECURITY_CONTEXT
        ) or {}

        working_dir = case_insensitive_dict_get(container_properties, config.ACI_FIELD_CONTAINERS_WORKINGDIR)

        mounts = process_mounts_from_config(container_properties) + process_configmap(container_properties)
        if (
            scenario.lower() == config.VN2 and
            case_insensitive_dict_get(container_security_context, config.ACI_FIELD_CONTAINERS_PRIVILEGED)
        ):
            mounts += config.DEFAULT_MOUNTS_PRIVILEGED_VIRTUAL_NODE

        labels = case_insensitive_dict_get(policy_input_json, config.VIRTUAL_NODE_YAML_LABELS) or []
        envs = []
        # use workload identity
        if (
            scenario.lower() == config.VN2 and
            config.VIRTUAL_NODE_YAML_LABEL_WORKLOAD_IDENTITY in labels and
            case_insensitive_dict_get(labels, config.VIRTUAL_NODE_YAML_LABEL_WORKLOAD_IDENTITY)
        ):
            envs += config.VIRTUAL_NODE_ENV_RULES_WORKLOAD_IDENTITY
            mounts += config.DEFAULT_MOUNTS_WORKLOAD_IDENTITY_VIRTUAL_NODE

        envs += process_env_vars_from_config(container_properties)

        output_containers.append(
            {
                config.ACI_FIELD_CONTAINERS_ID: image_name,
                config.ACI_FIELD_CONTAINERS_NAME: container_name,
                config.ACI_FIELD_CONTAINERS_CONTAINERIMAGE: image_name,
                config.ACI_FIELD_CONTAINERS_WORKINGDIR: working_dir,
                config.ACI_FIELD_CONTAINERS_ENVS: envs,
                config.ACI_FIELD_CONTAINERS_COMMAND: case_insensitive_dict_get(
                    container_properties, config.ACI_FIELD_TEMPLATE_COMMAND
                ) or [],
                config.ACI_FIELD_CONTAINERS_MOUNTS: mounts,
                config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES: exec_processes
                + config.DEBUG_MODE_SETTINGS.get(config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES)
                if debug_mode
                else exec_processes,
                config.ACI_FIELD_CONTAINERS_SIGNAL_CONTAINER_PROCESSES: [],
                config.ACI_FIELD_CONTAINERS_ALLOW_STDIO_ACCESS: not disable_stdio,
                config.ACI_FIELD_CONTAINERS_SECURITY_CONTEXT: case_insensitive_dict_get(
                    container_properties, config.ACI_FIELD_TEMPLATE_SECURITY_CONTEXT
                ),
            }
        )

    # Add default fragments if necessary
    if not exclude_default_fragments:
        rego_fragments.extend(copy.deepcopy(config.DEFAULT_REGO_FRAGMENTS))

    # changes the svn of the infrastructure fragment provided by ACI
    if infrastructure_svn:
        # assumes the first DEFAULT_REGO_FRAGMENT is always the
        # infrastructure fragment
        rego_fragments[0][
            config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_MINIMUM_SVN
        ] = infrastructure_svn

    return AciPolicy(
        {
            config.ACI_FIELD_VERSION: version,
            config.ACI_FIELD_CONTAINERS: output_containers,
        },
        disable_stdio=disable_stdio,
        rego_fragments=rego_fragments,
        debug_mode=debug_mode,
        is_vn2=scenario.lower() == config.VN2,
    )


def load_policy_from_virtual_node_yaml_file(
        virtual_node_yaml_path: str,
        debug_mode: bool = False,
        disable_stdio: bool = False,
        approve_wildcards: bool = False,
        diff_mode: bool = False,
        rego_imports: list = None,
        exclude_default_fragments: bool = False,
        fragment_contents: list = None,
        infrastructure_svn: str = None,
) -> List[AciPolicy]:
    yaml_contents_str = os_util.load_str_from_file(virtual_node_yaml_path)
    return load_policy_from_virtual_node_yaml_str(
        yaml_contents_str,
        debug_mode=debug_mode,
        disable_stdio=disable_stdio,
        approve_wildcards=approve_wildcards,
        diff_mode=diff_mode,
        rego_imports=rego_imports,
        exclude_default_fragments=exclude_default_fragments,
        fragment_contents=fragment_contents,
        infrastructure_svn=infrastructure_svn,
    )


# pylint: disable=R0912
def load_policy_from_virtual_node_yaml_str(
        yaml_contents_str: List[str],
        debug_mode: bool = False,
        disable_stdio: bool = False,
        approve_wildcards: bool = False,
        diff_mode: bool = False,
        rego_imports: list = None,
        exclude_default_fragments: bool = False,
        fragment_contents: Any = None,
        infrastructure_svn: str = None,
) -> List[AciPolicy]:
    """
    Load a virtual node yaml file and generate a policy object
    This happens in two passes:
    1. Parse the yaml file and extract ConfigMaps and Secrets
    2. Gather the container information
    """
    all_policies = []
    existing_containers = []
    existing_fragments = []
    yaml_contents = os_util.load_multiple_yaml_from_str(yaml_contents_str)
    config_map_data = []
    secrets_data = []
    for yaml in yaml_contents:
        kind = case_insensitive_dict_get(yaml, "kind")
        if kind == "ConfigMap":
            config_map_data.append(yaml)
        elif kind == "Secret":
            secrets_data.append(yaml)

    # we only want to look at the things that create containers
    yaml_contents = filter_non_pod_resources(yaml_contents)
    for yaml in yaml_contents:
        # extract existing policy and fragments for diff mode
        metadata = case_insensitive_dict_get(yaml, config.VIRTUAL_NODE_YAML_METADATA)
        annotations = case_insensitive_dict_get(metadata, config.VIRTUAL_NODE_YAML_ANNOTATIONS)

        existing_policy = case_insensitive_dict_get(annotations, config.VIRTUAL_NODE_YAML_POLICY)
        try:
            if existing_policy:
                existing_containers, existing_fragments = decompose_confidential_properties(existing_policy)
        except ValueError as e:
            if diff_mode:
                # In diff mode, we raise an error if the base64 policy is malformed
                eprint(f"Unable to decode existing policy. Please check the base64 encoding.\n{e}")
            else:
                # In non-diff mode, we ignore the error and proceed without the policy
                existing_containers, existing_fragments = ([], [])
        # because there are many ways to get pod information, we normalize them so the interface is the same
        normalized_yaml = convert_to_pod_spec(yaml)
        volume_claim_templates = get_volume_claim_templates(yaml)

        normalized_metadata = case_insensitive_dict_get(normalized_yaml, config.VIRTUAL_NODE_YAML_METADATA)
        labels = case_insensitive_dict_get(normalized_metadata, config.VIRTUAL_NODE_YAML_LABELS) or []
        use_workload_identity = (
            config.VIRTUAL_NODE_YAML_LABEL_WORKLOAD_IDENTITY in labels
            and labels.get(config.VIRTUAL_NODE_YAML_LABEL_WORKLOAD_IDENTITY) == "true")

        spec = case_insensitive_dict_get(normalized_yaml, "spec")
        if not spec:
            eprint("YAML file does not contain a spec field")

        # pod security context
        pod_security_context = case_insensitive_dict_get(spec, "securityContext") or {}

        policy_containers = []
        containers = case_insensitive_dict_get(spec, config.ACI_FIELD_TEMPLATE_CONTAINERS)
        if not containers:
            eprint("YAML file does not contain a containers field")
        # NOTE: initContainers are not treated differently in the security policy
        # but they are treated differently in the pod spec
        # e.g. lifecycle and probes are not supported in initContainers
        init_containers = case_insensitive_dict_get(spec, config.ACI_FIELD_TEMPLATE_INIT_CONTAINERS) or []

        rego_fragments = copy.deepcopy(config.DEFAULT_REGO_FRAGMENTS) if not exclude_default_fragments else []
        if infrastructure_svn:
            # assumes the first DEFAULT_REGO_FRAGMENT is always the
            # infrastructure fragment
            rego_fragments[0][
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_MINIMUM_SVN
            ] = infrastructure_svn
        if rego_imports:
            # error check the rego imports for invalid data types
            processed_imports = process_fragment_imports(rego_imports)
            rego_fragments.extend(processed_imports)

        for container in containers + init_containers:
            # image and name
            image = case_insensitive_dict_get(container, config.ACI_FIELD_TEMPLATE_IMAGE)
            if not image:
                eprint("Container does not have an image field")

            # env vars
            envs = process_env_vars_from_yaml(
                container,
                config_map_data,
                secrets_data,
                approve_wildcards=approve_wildcards
            )

            # command
            command = case_insensitive_dict_get(container, config.VIRTUAL_NODE_YAML_COMMAND) or []
            args = case_insensitive_dict_get(container, config.VIRTUAL_NODE_YAML_ARGS) or []

            # mounts
            mounts = []
            volumes = case_insensitive_dict_get(spec, "volumes") or []

            if use_workload_identity:
                envs += config.VIRTUAL_NODE_ENV_RULES_WORKLOAD_IDENTITY
                mounts += config.DEFAULT_MOUNTS_WORKLOAD_IDENTITY_VIRTUAL_NODE

            # there can be implicit volumes from volumeClaimTemplates
            # We need to add them to the list of volumes and note if they are readonly
            for volume_claim_template in volume_claim_templates:
                vct_metadata = case_insensitive_dict_get(volume_claim_template, config.VIRTUAL_NODE_YAML_METADATA)
                temp_volume = {
                    config.VIRTUAL_NODE_YAML_NAME:
                    case_insensitive_dict_get(vct_metadata, config.VIRTUAL_NODE_YAML_NAME),
                }
                vct_spec = case_insensitive_dict_get(volume_claim_template, "spec")
                if vct_spec:
                    vct_access_modes = case_insensitive_dict_get(vct_spec, "accessModes")
                    if vct_access_modes and config.VIRTUAL_NODE_YAML_READ_ONLY_MANY in vct_access_modes:
                        temp_volume[config.ACI_FIELD_TEMPLATE_MOUNTS_READONLY] = True

                volumes.append(temp_volume)

            # set of volume types that are read-only by default
            read_only_types = {"configMap", "secret", "downwardAPI", "projected"}

            volume_mounts = case_insensitive_dict_get(container, "volumeMounts")
            if volume_mounts:
                for mount in volume_mounts:
                    mount_name = case_insensitive_dict_get(mount, config.VIRTUAL_NODE_YAML_NAME)
                    mount_path = case_insensitive_dict_get(mount, "mountPath")

                    # find the corresponding volume
                    volume = next(
                        (
                            vol for vol in volumes if case_insensitive_dict_get(
                                vol, config.VIRTUAL_NODE_YAML_NAME
                            ) == mount_name
                        ),
                        None
                    ) or {}

                    # determine if this volume is one of the read-only types
                    read_only_default = (
                        any(key in read_only_types for key in volume.keys()) or
                        volume.get(config.ACI_FIELD_TEMPLATE_MOUNTS_READONLY)
                    )

                    if read_only_default:
                        # log warning if readOnly is explicitly set to false for a read-only volume type
                        if case_insensitive_dict_get(mount, config.ACI_FIELD_TEMPLATE_MOUNTS_READONLY) is False:
                            logger.warning(
                                "Volume '%s' in container '%s' is of a type that requires readOnly access (%s), "
                                "but readOnly: false was specified. Enforcing readOnly: true for policy generation.",
                                mount_name,
                                case_insensitive_dict_get(container, config.VIRTUAL_NODE_YAML_NAME),
                                ', '.join(read_only_types)
                            )
                        mount_readonly = True
                    else:
                        # use the readOnly field or default to False for non-read-only volumes
                        mount_readonly = case_insensitive_dict_get(
                            mount, config.ACI_FIELD_TEMPLATE_MOUNTS_READONLY
                        ) or False

                    mounts.append({
                        config.ACI_FIELD_CONTAINERS_MOUNTS_TYPE: config.ACI_FIELD_YAML_MOUNT_TYPE,
                        config.ACI_FIELD_CONTAINERS_MOUNTS_PATH: mount_path,
                        config.ACI_FIELD_CONTAINERS_MOUNTS_READONLY: mount_readonly,
                    })

            # container security context
            container_security_context = case_insensitive_dict_get(
                container, config.ACI_FIELD_TEMPLATE_SECURITY_CONTEXT
            ) or {}

            if case_insensitive_dict_get(container_security_context, config.ACI_FIELD_CONTAINERS_PRIVILEGED) is True:
                mounts += config.DEFAULT_MOUNTS_PRIVILEGED_VIRTUAL_NODE

            # security context
            security_context = pod_security_context.copy()
            security_context.update(container_security_context)

            # probes
            # NOTE: this is reused from ARM template parsing in case of future incompatibility
            exec_processes = []
            extract_probe(exec_processes, container, config.ACI_FIELD_YAML_LIVENESS_PROBE)
            extract_probe(exec_processes, container, config.ACI_FIELD_YAML_READINESS_PROBE)
            extract_probe(exec_processes, container, config.ACI_FIELD_YAML_STARTUP_PROBE)
            # lifecycle hooks
            extract_lifecycle_hook(exec_processes, container, config.VIRTUAL_NODE_YAML_LIFECYCLE_POST_START)
            extract_lifecycle_hook(exec_processes, container, config.VIRTUAL_NODE_YAML_LIFECYCLE_PRE_STOP)

            policy_containers.append(
                {
                    config.ACI_FIELD_CONTAINERS_ID: image,
                    config.ACI_FIELD_CONTAINERS_NAME: case_insensitive_dict_get(
                        container, config.VIRTUAL_NODE_YAML_NAME) or image,
                    config.ACI_FIELD_CONTAINERS_CONTAINERIMAGE: image,
                    config.ACI_FIELD_CONTAINERS_ENVS: envs,
                    config.ACI_FIELD_TEMPLATE_ENTRYPOINT: command,
                    config.ACI_FIELD_CONTAINERS_COMMAND: args,
                    config.ACI_FIELD_CONTAINERS_MOUNTS: mounts,
                    config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES: exec_processes
                    + config.DEBUG_MODE_SETTINGS.get(config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES)
                    if debug_mode
                    else exec_processes,
                    config.ACI_FIELD_CONTAINERS_SIGNAL_CONTAINER_PROCESSES: [],
                    config.ACI_FIELD_CONTAINERS_ALLOW_STDIO_ACCESS: not disable_stdio,
                    config.ACI_FIELD_CONTAINERS_SECURITY_CONTEXT: security_context
                }
            )
        all_policies.append(
            AciPolicy(
                {
                    config.ACI_FIELD_VERSION: "1.0",
                    config.ACI_FIELD_CONTAINERS: policy_containers,
                    config.ACI_FIELD_TEMPLATE_CCE_POLICY: existing_containers,
                },
                debug_mode=debug_mode,
                disable_stdio=disable_stdio,
                rego_fragments=rego_fragments,
                # fallback to default fragments if the policy is not present
                is_vn2=True,
                existing_rego_fragments=existing_fragments,
                fragment_contents=fragment_contents,
            )
        )
    return all_policies
