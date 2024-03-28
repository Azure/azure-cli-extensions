# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
import json
import copy
import tarfile
from typing import Any, Tuple, Dict, List
from hashlib import sha256
import deepdiff
import yaml
import docker
from azext_confcom.errors import (
    eprint,
)
from azext_confcom import os_util
from azext_confcom import config


# TODO: these can be optimized to not have so many groups in the single match
# make this global so it can be used in multiple functions
PARAMETER_AND_VARIABLE_REGEX = r"\[(?:parameters|variables)\(\s*'([^\.\/]+?)'\s*\)\]"
WHOLE_PARAMETER_AND_VARIABLE = r"(\s*\[\s*(parameters|variables))(\(\s*'([^\.\/]+?)'\s*\)\])"


class DockerClient:
    def __init__(self) -> None:
        self._client = None

    def __enter__(self) -> docker.DockerClient:
        return self.get_client()

    def get_client(self) -> docker.DockerClient:
        if not self._client:
            self._client = docker.from_env()
        return self._client

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._client:
            self._client.close()


def case_insensitive_dict_get(dictionary, search_key) -> Any:
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
    return None


def image_has_hash(image: str) -> bool:
    return "@sha256:" in image


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
            with tarfile.open(tar_location) as tar:
                # get all the info out of the tarfile
                try:
                    image_info = os_util.map_image_from_tar_backwards_compatibility(
                        image_name, tar, tar_location
                    )
                except IndexError:
                    image_info = os_util.map_image_from_tar(
                        image_name, tar, tar_location
                    )
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
        eprint(
            f"{image_name} is attempting to build for unsupported architecture: " +
            f"{raw_image.attrs.get(config.ACI_FIELD_CONTAINERS_ARCHITECTURE_KEY)}. "
            + f"Only {config.ACI_FIELD_CONTAINERS_ARCHITECTURE_VALUE} is supported by Confidential ACI"
        )

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
    )

    if template_env_vars:
        for env_var in template_env_vars:
            name = case_insensitive_dict_get(env_var, "name")
            value = case_insensitive_dict_get(env_var, "value") or case_insensitive_dict_get(env_var, "secureValue")

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
                        env_vars.append({
                            config.ACI_FIELD_CONTAINERS_ENVS_NAME: name,
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
                key_name = re.search(r"'(.*?)'", key).group(1)
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


def replace_params_and_vars(params: dict, vars_dict: dict, attribute):
    out = None
    if isinstance(attribute, (int, float, bool)):
        out = attribute
    elif isinstance(attribute, str):
        out = find_value_in_params_and_vars(params, vars_dict, attribute)
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


def extract_confidential_properties(
    container_group_properties,
) -> Tuple[List[Dict], List[Dict]]:
    container_start = "containers := "
    fragment_start = "fragments := "
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
    # special case when "ccePolicy" field is blank, indicating the use of the "allow all" policy
    if not cce_policy:
        return ([], config.DEFAULT_REGO_FRAGMENTS)

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

    try:
        container_text = extract_containers_from_text(cce_policy, container_start)
        # replace tabs with 4 spaces, YAML parser can take in JSON with trailing commas but not tabs
        # so we need to get rid of the tabs
        container_text = container_text.replace("\t", "    ")

        containers = yaml.load(container_text, Loader=yaml.FullLoader)

        fragment_text = extract_containers_from_text(
            cce_policy, fragment_start
        ).replace("\t", "    ")

        fragments = yaml.load(
            fragment_text,
            Loader=yaml.FullLoader,
        )
    except yaml.YAMLError:
        # reading the rego file failed, so we'll just return the default outputs
        containers = []
        fragments = []

    return (containers, fragments)


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
    arm_template_path: str, parameter_data_path: str, policy: str, count: int, hashes: dict
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
        if item["type"] == config.ACI_FIELD_TEMPLATE_RESOURCE_LABEL
    ]

    if not aci_list:
        eprint(
            f'Field ["type"] must contain value of ["{config.ACI_FIELD_TEMPLATE_RESOURCE_LABEL}"]'
        )

    resource = aci_list[count]

    container_group_properties = case_insensitive_dict_get(
        resource, config.ACI_FIELD_TEMPLATE_PROPERTIES
    )

    # extract the existing cce policy if that's what was being asked
    confidential_compute_properties = case_insensitive_dict_get(
        container_group_properties, config.ACI_FIELD_TEMPLATE_CONFCOM_PROPERTIES
    )

    if confidential_compute_properties is None:
        eprint(
            f'Field ["{config.ACI_FIELD_TEMPLATE_CONFCOM_PROPERTIES}"] ' +
            f'not found in ["{config.ACI_FIELD_TEMPLATE_PROPERTIES}"]'
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
        user_input = input(
            "Do you want to overwrite the CCE Policy currently in container group " +
            f'"{container_group_name}" in the ARM Template? (y/n) '
        )
        if user_input.lower() == "y":
            confidential_compute_properties[
                config.ACI_FIELD_TEMPLATE_CCE_POLICY
            ] = policy
            write_flag = True
    # get containers to inject the base64 encoding of seccom profile hash into template if exists
    containers = case_insensitive_dict_get(
        container_group_properties, config.ACI_FIELD_CONTAINERS
    )
    for c in containers:
        container_image = case_insensitive_dict_get(c, config.ACI_FIELD_TEMPLATE_IMAGE)
        container_properties = case_insensitive_dict_get(c, config.ACI_FIELD_TEMPLATE_PROPERTIES)
        security_context = case_insensitive_dict_get(
            container_properties, config.ACI_FIELD_TEMPLATE_SECURITY_CONTEXT
        )
        if security_context:
            seccomp_profile = case_insensitive_dict_get(
                security_context, config.ACI_FIELD_CONTAINERS_SECCOMP_PROFILE
            )
            if seccomp_profile:
                hash_base64 = os_util.str_to_base64(hashes.get(container_image, ""))
                security_context[config.ACI_FIELD_CONTAINERS_SECCOMP_PROFILE] = hash_base64
                write_flag = True
    # write base64 encoding of seccomp profile hash to the template
    if write_flag:
        os_util.write_json_to_file(arm_template_path, input_arm_json)
        return True
    return False


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
        if item["type"] == config.ACI_FIELD_TEMPLATE_RESOURCE_LABEL
    ]

    if not aci_list:
        eprint(
            f'Field ["type"] must contain value of ["{config.ACI_FIELD_TEMPLATE_RESOURCE_LABEL}"]'
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
        if item["type"] == config.ACI_FIELD_TEMPLATE_RESOURCE_LABEL
    ]

    if not aci_list:
        eprint(
            f'Field ["type"] must contain value of ["{config.ACI_FIELD_TEMPLATE_RESOURCE_LABEL}"]'
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
