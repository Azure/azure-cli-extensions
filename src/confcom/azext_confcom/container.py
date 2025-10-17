# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import json
import os
from typing import Any, List, Dict
from azext_confcom.template_util import (
    case_insensitive_dict_get,
    replace_params_and_vars,
    str_to_sha256,
    process_seccomp_policy,
    translate_signals
)
from azext_confcom import config
from azext_confcom.errors import eprint
from azext_confcom.os_util import base64_to_str


_DEFAULT_MOUNTS = config.DEFAULT_MOUNTS_USER
_DEFAULT_MOUNTS_VN2 = config.DEFAULT_MOUNTS_USER_VIRTUAL_NODE

_DEFAULT_USER = config.DEFAULT_USER

_INJECTED_CUSTOMER_ENV_RULES = (
    config.OPENGCS_ENV_RULES
    + config.FABRIC_ENV_RULES
    + config.MANAGED_IDENTITY_ENV_RULES
    + config.ENABLE_RESTART_ENV_RULE
)

_INJECTED_SERVICE_VN2_ENV_RULES = config.VIRTUAL_NODE_ENV_RULES

_CAPABILITIES = {
    config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_BOUNDING: [],
    config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_EFFECTIVE: [],
    config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_INHERITABLE: [],
    config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_PERMITTED: [],
    config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_AMBIENT: [],
}


def extract_container_image(container_json: Any) -> str:
    containerImage = case_insensitive_dict_get(
        container_json, config.ACI_FIELD_CONTAINERS_CONTAINERIMAGE
    )
    if not containerImage:
        eprint(
            f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
            + f'["{config.ACI_FIELD_CONTAINERS_CONTAINERIMAGE}"] is empty or can not be found.'
        )
    return containerImage


def extract_env_rules(container_json: Any) -> List[Dict]:
    environmentRules = []
    env_rules = case_insensitive_dict_get(
        container_json, config.ACI_FIELD_CONTAINERS_ENVS
    )
    if env_rules is None:  # empty(no envs) is acceptable
        eprint(
            f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
            + f'["{config.ACI_FIELD_CONTAINERS_ENVS}"] is null or can not be found.'
        )

    # parse each environment variable pair and add it to list
    for rule in env_rules:
        name, value, strategy, required = (
            case_insensitive_dict_get(rule, config.ACI_FIELD_CONTAINERS_ENVS_NAME),
            case_insensitive_dict_get(rule, config.ACI_FIELD_CONTAINERS_ENVS_VALUE),
            case_insensitive_dict_get(rule, config.ACI_FIELD_CONTAINERS_ENVS_STRATEGY),
            case_insensitive_dict_get(rule, config.ACI_FIELD_CONTAINERS_ENVS_REQUIRED),
        )
        if name is None:
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                + f'["{config.ACI_FIELD_CONTAINERS_ENVS}"]'
                + f'["{config.ACI_FIELD_CONTAINERS_ENVS_NAME}] is incorrect or missing.'
            )
        if value is None:
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                + f'["{config.ACI_FIELD_CONTAINERS_ENVS}"]'
                + f'["{config.ACI_FIELD_CONTAINERS_ENVS_VALUE}"] is empty for env var {name}.'
            )
        if strategy is None:
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                + f'["{config.ACI_FIELD_CONTAINERS_ENVS}"]'
                + f'["{config.ACI_FIELD_CONTAINERS_ENVS_STRATEGY}"] is incorrect for env var {name}.'
            )

        environmentRules.append(
            {
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE: f"{name}={value}",
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_STRATEGY: strategy,
                # default value for "required" is False
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_REQUIRED: required
                if required is not None
                else False,
            }
        )
    return environmentRules


def extract_id(container_json: Any) -> str:
    return case_insensitive_dict_get(container_json, config.ACI_FIELD_CONTAINERS_ID)


def extract_container_name(container_json: Any) -> str:
    return case_insensitive_dict_get(container_json, config.ACI_FIELD_CONTAINERS_NAME)


def extract_working_dir(container_json: Any) -> str:
    # parse working directory
    workingDir = case_insensitive_dict_get(
        container_json, config.ACI_FIELD_CONTAINERS_WORKINGDIR
    )
    # check workingDir is an absolute path if user specified
    if workingDir:
        if not isinstance(workingDir, str):
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                + f'["{config.ACI_FIELD_CONTAINERS_WORKINGDIR}"] must be a String.'
            )
        if not os.path.isabs(workingDir):
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                + f'["{config.ACI_FIELD_CONTAINERS_WORKINGDIR}"] with value: {workingDir} is not absolute path.'
            )
    return workingDir


def extract_entrypoint(container_json: Any) -> List[str]:
    # parse entrypoint. can either be a list of strings or None in the case of non-VN2 policy generation
    entrypoint = case_insensitive_dict_get(
        container_json, config.ACI_FIELD_TEMPLATE_ENTRYPOINT
    )
    if not isinstance(entrypoint, list) and entrypoint is not None:
        eprint(
            f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
            + f'["{config.ACI_FIELD_TEMPLATE_ENTRYPOINT}"] must be list of Strings.'
        )
    return entrypoint


def extract_command(container_json: Any) -> List[str]:
    # parse command
    command = case_insensitive_dict_get(
        container_json, config.ACI_FIELD_CONTAINERS_COMMAND
    )
    if not isinstance(command, list):
        eprint(
            f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
            + f'["{config.ACI_FIELD_CONTAINERS_COMMAND}"] must be list of Strings.'
        )
    return command


def extract_mounts(container_json: Any) -> List:
    # parse mounts
    mounts = case_insensitive_dict_get(
        container_json, config.ACI_FIELD_CONTAINERS_MOUNTS
    )
    _mounts = []
    if mounts:
        if not isinstance(mounts, list):
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                + f'["{config.ACI_FIELD_CONTAINERS_MOUNTS}"] must be list of Mount configuration.'
            )

        for m in mounts:
            mount_type = case_insensitive_dict_get(
                m, config.ACI_FIELD_CONTAINERS_MOUNTS_TYPE
            )
            if mount_type not in config.MOUNT_SOURCE_TABLE:
                eprint(
                    f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                    + f'["{config.ACI_FIELD_CONTAINERS_MOUNTS}"]'
                    + f'["{config.ACI_FIELD_CONTAINERS_MOUNTS_TYPE}"]'
                    + "can only be following values:"
                    + f'{",".join(list(config.MOUNT_SOURCE_TABLE.keys()))} .'
                )

            mount_path = case_insensitive_dict_get(
                m, config.ACI_FIELD_CONTAINERS_MOUNTS_PATH
            )
            if not mount_path:
                eprint(
                    f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                    + f'["{config.ACI_FIELD_CONTAINERS_MOUNTS}"]'
                    + f'["{config.ACI_FIELD_CONTAINERS_MOUNTS_PATH}"] is empty or can not be found.'
                )

            mount_readonly = case_insensitive_dict_get(
                m, config.ACI_FIELD_CONTAINERS_MOUNTS_READONLY
            )
            if mount_readonly is not None and not isinstance(mount_readonly, bool):
                eprint(
                    f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                    + f'["{config.ACI_FIELD_CONTAINERS_MOUNTS}"]'
                    + f'["{config.ACI_FIELD_CONTAINERS_MOUNTS_READONLY}"] can only be boolean value.'
                )

            # readonly default to False if not specified
            if mount_readonly is None:
                mount_readonly = False

            _mounts.append(m)
    return _mounts


def extract_exec_process(container_json: Any) -> List:
    # get the exec_processes info used as a liveness probe
    exec_processes = case_insensitive_dict_get(
        container_json, config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES
    )
    exec_processes_output = []
    if exec_processes:
        if not isinstance(exec_processes, list):
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                + f'["{config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES}"] can only be a list.'
            )

        for exec_processes_item in exec_processes:

            exec_command = case_insensitive_dict_get(
                exec_processes_item, config.ACI_FIELD_CONTAINERS_COMMAND
            )
            if not isinstance(exec_command, list) and all(
                map(lambda x: isinstance(x, str), exec_command)
            ):
                eprint(
                    f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                    + f'["{config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES}"]'
                    + f'["{config.ACI_FIELD_CONTAINERS_COMMAND}"]'
                    + "can only be a list of strings."
                )

            exec_signals = case_insensitive_dict_get(
                exec_processes_item,
                config.ACI_FIELD_CONTAINERS_SIGNAL_CONTAINER_PROCESSES,
            )
            if not isinstance(exec_signals, list) and all(
                map(lambda x: isinstance(x, int), exec_signals)
            ):
                eprint(
                    f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                    + f'["{config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES}"]'
                    + f'["{config.ACI_FIELD_CONTAINERS_COMMAND}"]'
                    + "can only be a list of integers."
                )

            exec_processes_output.append(
                {
                    config.POLICY_FIELD_CONTAINERS_ELEMENTS_COMMANDS: exec_command,
                    config.POLICY_FIELD_CONTAINERS_ELEMENTS_SIGNAL_CONTAINER_PROCESSES: exec_signals,
                }
            )
    return exec_processes_output


def extract_allow_stdio_access(container_json: Any) -> bool:
    # get the field for Standard IO access, default to true
    allow_stdio_value = case_insensitive_dict_get(
        container_json, config.ACI_FIELD_CONTAINERS_ALLOW_STDIO_ACCESS
    )
    allow_stdio_access = allow_stdio_value if allow_stdio_value is not None else True
    return allow_stdio_access


def extract_user(container_json: Any) -> Dict:
    security_context = case_insensitive_dict_get(
        container_json, config.ACI_FIELD_CONTAINERS_SECURITY_CONTEXT
    )

    user = copy.deepcopy(_DEFAULT_USER)
    # assumes that securityContext field is optional
    if security_context:
        # To-Do: figure out how to determine if regex patterns
        # get the field for run as user
        run_as_user_value = case_insensitive_dict_get(
            security_context, config.ACI_FIELD_CONTAINERS_RUN_AS_USER
        )

        if isinstance(run_as_user_value, int) and run_as_user_value >= 0:
            user[config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_USER_IDNAME] = {
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_PATTERN: str(run_as_user_value),
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_STRATEGY: "id"
            }
        elif run_as_user_value is not None:
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS}"]["{config.ACI_FIELD_CONTAINERS_SECURITY_CONTEXT}"]'
                + f'["{config.ACI_FIELD_CONTAINERS_RUN_AS_USER}"] can only be an integer value.'
            )

        # get the field for run as group
        run_as_group_value = case_insensitive_dict_get(
            security_context, config.ACI_FIELD_CONTAINERS_RUN_AS_GROUP
        )

        if isinstance(run_as_group_value, int) and run_as_group_value >= 0:
            user[config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_GROUP_IDNAMES][0] = {
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_PATTERN: str(run_as_group_value),
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_STRATEGY: "id"
            }
        elif run_as_group_value is not None:
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS}"]["{config.ACI_FIELD_CONTAINERS_SECURITY_CONTEXT}"]'
                + f'["{config.ACI_FIELD_CONTAINERS_RUN_AS_GROUP}"] can only be an integer value.'
            )

    return user


def extract_capabilities(container_json: Any, privileged_value: bool):
    security_context = case_insensitive_dict_get(
        container_json, config.ACI_FIELD_CONTAINERS_SECURITY_CONTEXT
    )

    output_capabilities = copy.deepcopy(_CAPABILITIES)
    non_added_fields = [
        config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_BOUNDING,
        config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_EFFECTIVE,
        config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_PERMITTED,
    ]

    # add privileged default capabilities if true, otherwise add unprivileged default capabilities
    if privileged_value:
        # only ambient should be empty
        non_added_fields.append(config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_INHERITABLE)
        for key in non_added_fields:
            output_capabilities[key] = copy.deepcopy(config.DEFAULT_PRIVILEGED_CAPABILITIES)
    else:
        # add the default capabilities to the output
        for key in non_added_fields:
            output_capabilities[key] = copy.deepcopy(config.DEFAULT_UNPRIVILEGED_CAPABILITIES)

    # add and drop capabilities if they are explicitly set in the ARM template
    capabilities = case_insensitive_dict_get(
        security_context, config.ACI_FIELD_CONTAINERS_CAPABILITIES
    )

    # user can ADD and DROP capabilities in the ARM template
    if capabilities:
        # error check if capabilities is not a dict
        if not isinstance(capabilities, dict):
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS}"]["{config.ACI_FIELD_CONTAINERS_SECURITY_CONTEXT}"]'
                + f'["{config.ACI_FIELD_CONTAINERS_CAPABILITIES}"] can only be a dictionary.'
            )

        # get the add field
        add = case_insensitive_dict_get(
            capabilities, config.ACI_FIELD_CONTAINERS_CAPABILITIES_ADD
        )
        if add:
            # error check if add is not a list
            if not isinstance(add, list):
                eprint(
                    f'Field ["{config.ACI_FIELD_CONTAINERS}"]["{config.ACI_FIELD_CONTAINERS_SECURITY_CONTEXT}"]'
                    + f'["{config.ACI_FIELD_CONTAINERS_CAPABILITIES_ADD}"] can only be a list.'
                )
            # error check if add contains non-string values
            for capability in add:
                # error check that all the items in "add" are strings
                if not isinstance(capability, str):
                    eprint(
                        f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                        + f'["{config.ACI_FIELD_CONTAINERS_SECURITY_CONTEXT}"]'
                        + f'["{config.ACI_FIELD_CONTAINERS_CAPABILITIES_ADD}"] can only contain strings.'
                    )
            for key in non_added_fields:
                # add the capabilities to the output, except ambient list
                # we still want the ambient set to be empty
                output_capabilities[key] += add

        # get the drop field
        drop = case_insensitive_dict_get(
            capabilities, config.ACI_FIELD_CONTAINERS_CAPABILITIES_DROP
        )
        if drop:
            # error check if drop is not a list
            if not isinstance(drop, list):
                eprint(
                    f'Field ["{config.ACI_FIELD_CONTAINERS}"]["{config.ACI_FIELD_CONTAINERS_SECURITY_CONTEXT}"]'
                    + f'["{config.ACI_FIELD_CONTAINERS_CAPABILITIES_DROP}"] can only be a list.'
                )
            # error check that all the items in "drop" are strings
            for capability in drop:
                if not isinstance(capability, str):
                    eprint(
                        f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                        + f'["{config.ACI_FIELD_CONTAINERS_SECURITY_CONTEXT}"]'
                        + f'["{config.ACI_FIELD_CONTAINERS_CAPABILITIES_DROP}"] can only contain strings.'
                    )
            # drop the capabilities from the output
            for keys in output_capabilities:
                output_capabilities[keys] = [x for x in output_capabilities[keys] if x not in drop]
    # de-duplicate the capabilities
    for key, value in output_capabilities.items():
        output_capabilities[key] = sorted(list(set(value)))

    return output_capabilities


def extract_allow_elevated(container_json: Any) -> bool:
    security_context = case_insensitive_dict_get(
        container_json, config.ACI_FIELD_CONTAINERS_SECURITY_CONTEXT
    )

    # get the field for privileged, default to false
    privileged_value = case_insensitive_dict_get(
        security_context, config.ACI_FIELD_CONTAINERS_PRIVILEGED
    )
    if privileged_value and not isinstance(privileged_value, bool) and not isinstance(privileged_value, str):
        eprint(
            f'Field ["{config.ACI_FIELD_CONTAINERS}"]["{config.ACI_FIELD_CONTAINERS_SECURITY_CONTEXT}"]'
            + f'["{config.ACI_FIELD_CONTAINERS_PRIVILEGED}"] can only be a boolean or string value.'
        )

    # force the field into a bool
    if isinstance(privileged_value, str):
        privileged_value = privileged_value.lower() == "true"
    # default to false
    return privileged_value or False


def extract_seccomp_profile_sha256(container_json: Any, seccomp_json: dict = None) -> Dict:
    security_context = case_insensitive_dict_get(
        container_json, config.ACI_FIELD_CONTAINERS_SECURITY_CONTEXT
    )

    seccomp_profile_sha256 = ""
    # assumes that securityContext field is optional
    if security_context:
        # get the field for seccomp_profile
        seccomp_profile = case_insensitive_dict_get(
            security_context, config.ACI_FIELD_CONTAINERS_SECCOMP_PROFILE
        )

        if isinstance(seccomp_profile, str):
            # clean up and jsonify the seccomp profile
            seccomp_profile = process_seccomp_policy(base64_to_str(seccomp_profile))
            seccomp_profile_str = json.dumps(seccomp_profile, separators=(',', ':'))
            # hash the seccomp profile
            seccomp_profile_sha256 = str_to_sha256(seccomp_profile_str)

        elif isinstance(seccomp_profile, dict):
            profile_type = seccomp_profile.get('type')

            if profile_type == 'RuntimeDefault':
                # Tied to container runtime. Not sure how to extract it.
                pass

            elif profile_type == 'Localhost':
                if seccomp_json:
                    # If seccomp JSON is provided directly, use it
                    processed_seccomp_profile = process_seccomp_policy(json.dumps(seccomp_json))
                    seccomp_profile_str = json.dumps(processed_seccomp_profile, separators=(',', ':'))
                    seccomp_profile_sha256 = str_to_sha256(seccomp_profile_str)
                else:
                    eprint("Localhost profile type specified but no seccomp JSON provided.")

    # NOTE: this is also returned if profile_type == 'Unconfined'
    return seccomp_profile_sha256


def extract_allow_privilege_escalation(container_json: Any) -> bool:
    security_context = case_insensitive_dict_get(
        container_json, config.ACI_FIELD_CONTAINERS_SECURITY_CONTEXT
    )

    # default to false so that no_new_privileges defaults to false
    allow_privilege_escalation = True
    # assumes that securityContext field is optional
    if security_context:
        # get the field for allow privilege escalation, default to true
        temp_privilege_escalation = case_insensitive_dict_get(
            security_context,
            config.ACI_FIELD_CONTAINERS_ALLOW_PRIVILEGE_ESCALATION
        )
        if temp_privilege_escalation is not None:
            if not isinstance(temp_privilege_escalation, bool) and not isinstance(temp_privilege_escalation, str):
                eprint(
                    f'Field ["{config.ACI_FIELD_CONTAINERS}"]["{config.ACI_FIELD_CONTAINERS_SECURITY_CONTEXT}"]'
                    + f'["{config.ACI_FIELD_CONTAINERS_PRIVILEGED}"] can only be a boolean or string value.'
                )

            # force the field into a bool
            if isinstance(temp_privilege_escalation, str):
                temp_privilege_escalation = temp_privilege_escalation.lower() == "true"
            allow_privilege_escalation = temp_privilege_escalation
    return allow_privilege_escalation


def extract_get_signals(container_json: Any) -> List:
    # get the signals info used as a liveness probe
    signals = (
        case_insensitive_dict_get(
            container_json, config.ACI_FIELD_CONTAINERS_SIGNAL_CONTAINER_PROCESSES
        )
        or []
    )
    if signals:
        if not isinstance(signals, list):
            eprint(
                f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                + f'["{config.ACI_FIELD_CONTAINERS_SIGNAL_CONTAINER_PROCESSES}"]'
                + "can only be a list."
            )

        for signals_item in signals:
            if not isinstance(signals_item, int):
                eprint(
                    f'Field ["{config.ACI_FIELD_CONTAINERS}"]'
                    + f'["{config.ACI_FIELD_CONTAINERS_SIGNAL_CONTAINER_PROCESSES}"]'
                    + "can only be an integer."
                )
    return signals


class ContainerImage:
    # pylint: disable=too-many-instance-attributes, too-many-public-methods

    @classmethod
    def from_json(
        cls, container_json: Any
    ) -> "ContainerImage":

        container_image = extract_container_image(container_json)
        id_val = extract_id(container_json)
        container_name = extract_container_name(container_json)
        environment_rules = extract_env_rules(container_json=container_json)
        entrypoint = extract_entrypoint(container_json)
        command = extract_command(container_json)
        working_dir = extract_working_dir(container_json)
        mounts = extract_mounts(container_json)
        # the first half of the conditional is for backwards compatibility with input.json-formatted files
        allow_elevated = case_insensitive_dict_get(
            container_json,
            config.ACI_FIELD_CONTAINERS_ALLOW_ELEVATED) or extract_allow_elevated(container_json)
        exec_processes = extract_exec_process(
            container_json
        )
        signals = extract_get_signals(container_json)
        user = extract_user(container_json)
        capabilities = extract_capabilities(container_json, allow_elevated)
        seccomp_profile_sha256 = extract_seccomp_profile_sha256(container_json)
        allow_stdio_access = extract_allow_stdio_access(container_json)
        allow_privilege_escalation = extract_allow_privilege_escalation(container_json)
        return ContainerImage(
            containerImage=container_image,
            containerName=container_name,
            environmentRules=environment_rules,
            entrypoint=entrypoint,
            command=command,
            workingDir=working_dir,
            mounts=mounts,
            allow_elevated=allow_elevated,
            extraEnvironmentRules=[],
            execProcesses=exec_processes,
            signals=signals,
            user=user,
            capabilities=capabilities,
            seccomp_profile_sha256=seccomp_profile_sha256,
            allowStdioAccess=allow_stdio_access,
            allowPrivilegeEscalation=allow_privilege_escalation,
            id_val=id_val,
        )

    def __init__(
        self,
        containerImage: str,
        environmentRules: Dict,
        command: List[str],
        workingDir: str,
        mounts: List,
        allow_elevated: bool,
        id_val: str,
        extraEnvironmentRules: Dict,
        entrypoint: List[str] = None,
        capabilities: Dict = copy.deepcopy(_CAPABILITIES),
        user: Dict = copy.deepcopy(_DEFAULT_USER),
        seccomp_profile_sha256: str = "",
        allowStdioAccess: bool = True,
        allowPrivilegeEscalation: bool = True,
        execProcesses: List = None,
        signals: List = None,
        containerName: str = "",
    ) -> None:
        self.containerImage = containerImage
        self.containerName = containerName
        if ":" in containerImage:
            self.base, self.tag = containerImage.split(":", 1)
        else:
            self.base, self.tag = containerImage, "latest"
        self._environmentRules = environmentRules
        self._entrypoint = entrypoint
        self._command = command
        self._workingDir = workingDir
        self._layers = []
        self._mounts = mounts
        self._allow_elevated = allow_elevated
        self._allow_stdio_access = allowStdioAccess
        self._seccomp_profile_sha256 = seccomp_profile_sha256
        self._user = user or {}
        self._capabilities = capabilities
        self._allow_privilege_escalation = allowPrivilegeEscalation
        self._identifier = id_val
        self._exec_processes = execProcesses or []
        self._signals = signals or []
        self._extraEnvironmentRules = extraEnvironmentRules

    def get_policy_json(self, omit_id: bool = False) -> str:
        return self._populate_policy_json_elements(omit_id=omit_id)

    def get_id(self) -> str:
        return self._identifier

    def get_name(self) -> str:
        return self.containerName

    def get_container_image(self) -> str:
        return self.containerImage

    def get_working_dir(self) -> str:
        return self._workingDir

    def set_signals(self, signals: List) -> None:
        signals = translate_signals([signals] if not isinstance(signals, list) else signals)
        self._signals = signals

    def set_working_dir(self, workingDir: str) -> None:
        self._workingDir = workingDir

    # note that entrypoint is only used for VN2 containers because of kubernetes discrepancy in naming
    # entrypoint -> command, args -> command
    def get_entrypoint(self) -> List[str]:
        return self._entrypoint

    def get_command(self) -> List[str]:
        return self._command

    def set_command(self, command: List[str]) -> None:
        self._command = command

    def get_environment_rules(self) -> Dict:
        return self._environmentRules

    def get_layers(self) -> List[str]:
        return self._layers

    def set_layers(self, layers: List[str]) -> None:
        self._layers = layers

    def get_user(self) -> Dict:
        return self._user

    def set_user(self, user: Dict) -> None:
        self._user = user

    def get_mounts(self) -> List:
        return self._mounts

    def set_mounts(self, mounts) -> None:
        self._mounts = mounts

    def get_seccomp_profile_sha256(self) -> str:
        return self._seccomp_profile_sha256

    def set_extra_environment_rules(self, rules: Dict) -> None:
        self._extraEnvironmentRules = rules

    def parse_all_parameters_and_variables(self, params, vars_dict) -> None:
        field_names = [
            "containerImage",
            "containerName",
            "_identifier",
            "_environmentRules",
            "_command",
            "_workingDir",
            "_mounts",
            "_identifier",
            "_exec_processes",
            "_extraEnvironmentRules",
        ]
        for field_name in field_names:
            attribute = getattr(self, field_name)
            out = replace_params_and_vars(params, vars_dict, attribute)
            setattr(self, field_name, out)
        # set these at the end since they're derived from containerImage, which could have been altered
        if ":" in self.containerImage:
            self.base, self.tag = self.containerImage.split(":", 1)
        else:
            self.base, self.tag = self.containerImage, "latest"

    def _get_environment_rules(self) -> List[Dict[str, Any]]:
        out_rules = copy.deepcopy(self._environmentRules)
        env_var_names = [
            var[config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE].split("=")[0]
            for var in out_rules
        ]
        for rule in self._extraEnvironmentRules:
            if rule[config.ACI_FIELD_CONTAINERS_ENVS_NAME] not in env_var_names:
                out_rules.append(
                    {
                        config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE:
                        f"{rule[config.ACI_FIELD_CONTAINERS_ENVS_NAME]}="
                        + f"{rule[config.ACI_FIELD_CONTAINERS_ENVS_VALUE]}",
                        config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_STRATEGY: rule[
                            config.ACI_FIELD_CONTAINERS_ENVS_STRATEGY
                        ],
                        config.POLICY_FIELD_CONTAINERS_ELEMENTS_REQUIRED: rule[
                            config.ACI_FIELD_CONTAINERS_ENVS_REQUIRED
                        ],
                    }
                )

        return out_rules

    def _get_mounts_json(self) -> Dict[str, Any]:
        # if mount is empty, return []
        if not self._mounts:
            return []

        mounts = []
        for m in self._mounts:
            mount = copy.deepcopy(config.DEFAULT_MOUNT_POLICY)
            mount[
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_SOURCE
            ] = config.MOUNT_SOURCE_TABLE[
                case_insensitive_dict_get(m, config.ACI_FIELD_TEMPLATE_MOUNTS_TYPE)
            ]
            mount[
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_DESTINATION
            ] = case_insensitive_dict_get(m, config.ACI_FIELD_TEMPLATE_MOUNTS_PATH)
            if case_insensitive_dict_get(
                m, "readonly"
            ) is not None and case_insensitive_dict_get(m, "readonly"):
                mount[config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_OPTIONS][2] = "ro"
            # specified options will overwrite default options in default mount policy
            if case_insensitive_dict_get(m, "options"):
                mount[
                    config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_OPTIONS
                ] = case_insensitive_dict_get(m, "options")
            # TODO: figure out what type of mount it is for secretsSource. For now, assume it is a bind mount
            mount[
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_TYPE
            ] = config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_TYPE_BIND
            mounts.append(mount)

        return mounts

    def _populate_policy_json_elements(self, omit_id: bool = False) -> Dict[str, Any]:
        elements = {
            config.POLICY_FIELD_CONTAINERS_NAME: self.get_name(),
            config.POLICY_FIELD_CONTAINERS_ELEMENTS_LAYERS: self._layers,
            config.POLICY_FIELD_CONTAINERS_ELEMENTS_COMMANDS: self._command,
            config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS: self._get_environment_rules(),
            config.POLICY_FIELD_CONTAINERS_ELEMENTS_WORKINGDIR: self._workingDir,
            config.POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS: self._get_mounts_json(),
            config.POLICY_FIELD_CONTAINERS_ELEMENTS_ALLOW_ELEVATED: self._allow_elevated,
            config.POLICY_FIELD_CONTAINERS_ELEMENTS_EXEC_PROCESSES: self._exec_processes,
            config.POLICY_FIELD_CONTAINERS_ELEMENTS_SIGNAL_CONTAINER_PROCESSES: self._signals,
            config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER: self.get_user(),
            config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES: self._capabilities,
            config.POLICY_FIELD_CONTAINERS_ELEMENTS_SECCOMP_PROFILE_SHA256: self._seccomp_profile_sha256,
            config.POLICY_FIELD_CONTAINERS_ELEMENTS_ALLOW_STDIO_ACCESS: self._allow_stdio_access,
            config.POLICY_FIELD_CONTAINERS_ELEMENTS_NO_NEW_PRIVILEGES: not self._allow_privilege_escalation
        }

        if not omit_id:
            elements[config.POLICY_FIELD_CONTAINERS_ID] = self._identifier
        # if we are omitting the id, we should remove the id value from the policy if it's in the name field
        elif omit_id and self.get_name() == self._identifier:
            del elements[config.POLICY_FIELD_CONTAINERS_NAME]

        return elements


class UserContainerImage(ContainerImage):
    # pylint: disable=arguments-differ
    @classmethod
    def from_json(
        cls, container_json: Any, is_vn2=False
    ) -> "UserContainerImage":
        image = super().from_json(container_json)
        image.__class__ = UserContainerImage
        mount_paths = {m["mountPath"] for m in image.get_mounts()}
        # inject default mounts for user container
        if image.base not in config.BASELINE_SIDECAR_CONTAINERS and not is_vn2:
            for mount in _DEFAULT_MOUNTS:
                if mount["mountPath"] not in mount_paths:
                    image.get_mounts().append(mount)

        if (image.base not in config.BASELINE_SIDECAR_CONTAINERS) and (is_vn2):
            for mount in _DEFAULT_MOUNTS_VN2:
                if mount["mountPath"] not in mount_paths:
                    image.get_mounts().append(mount)

        # Start with the customer environment rules
        env_rules = copy.deepcopy(_INJECTED_CUSTOMER_ENV_RULES)
        # If is_vn2, add the VN2 environment rules
        if is_vn2:
            env_rules += _INJECTED_SERVICE_VN2_ENV_RULES
            image.set_mounts(image.get_mounts() + copy.deepcopy(config.DEFAULT_MOUNTS_VIRTUAL_NODE))

        image.set_extra_environment_rules(env_rules)
        return image

    def _populate_policy_json_elements(self, omit_id: bool = False) -> Dict[str, Any]:
        return super()._populate_policy_json_elements(omit_id=omit_id)
