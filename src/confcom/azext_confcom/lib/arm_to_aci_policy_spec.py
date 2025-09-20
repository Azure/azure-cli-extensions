from typing import Iterator, Optional
import json
import re
from azext_confcom import config
from azext_confcom.template_util import (
    get_probe_exec_processes,
    is_sidecar,
    process_configmap,
    process_env_vars_from_template,
    process_mounts
)
from azext_confcom.lib.aci_policy_spec import (
    AciContainerPropertyEnvVariable,
    AciContainerPropertyExecProcesses,
    AciContainerPropertySecurityContext,
    AciContainerPropertySecurityContextCapabilities,
    AciContainerPropertyVolumeMounts,
    AciContainerSpec,
    AciContainerProperties,
    AciFragmentSpec,
    AciPolicySpec,
)

def get_parameters(
    arm_template: dict,
    arm_template_parameters: dict,
) -> dict:

    return {
        parameter_key: (
            arm_template_parameters.get("parameters", {}).get(parameter_key, {}).get("value")
            or arm_template.get("parameters", {}).get(parameter_key, {}).get("value")
            or arm_template.get("parameters", {}).get(parameter_key, {}).get("defaultValue")
        )
        for parameter_key in arm_template.get("parameters", {}).keys()
    }


def eval_parameters(
    arm_template: dict,
    arm_template_parameters: dict,
) -> dict:

    parameters = get_parameters(arm_template, arm_template_parameters)
    return json.loads(re.compile(r"\[parameters\(\s*'([^']+)'\s*\)\]").sub(
        lambda match: json.dumps(parameters.get(match.group(1)) or match.group(0))[1:-1],
        json.dumps(arm_template),
    ))


def eval_variables(
    arm_template: dict,
    arm_template_parameters: dict,
) -> dict:

    variables = arm_template.get("variables", {})
    return json.loads(re.compile(r"\[variables\(\s*'([^']+)'\s*\)\]").sub(
        lambda match: json.dumps(variables.get(match.group(1), match.group(0)))[1:-1],
        json.dumps(arm_template),
    ))


EVAL_FUNCS = [
    eval_parameters,
    eval_variables,
]


def arm_container_env_to_aci_policy_spec_env(
    container_properties: dict,
    parameters: dict,
    approve_wildcards: bool,
) -> Iterator[AciContainerPropertyEnvVariable]:

    for env_var in [
        *process_env_vars_from_template(parameters, {}, container_properties, approve_wildcards),
        *config.OPENGCS_ENV_RULES,
        *config.FABRIC_ENV_RULES,
        *config.MANAGED_IDENTITY_ENV_RULES,
        *config.ENABLE_RESTART_ENV_RULE,
    ]:
        yield AciContainerPropertyEnvVariable(**env_var)


def arm_container_volumes_to_aci_policy_spec_volumes(
    container_properties: dict,
    container_group_volumes: list[dict],
) -> Iterator[AciContainerPropertyVolumeMounts]:

    for vol_mount in [
        *process_mounts(container_properties, container_group_volumes),
        *process_configmap(container_properties),
        *(
            config.DEFAULT_MOUNTS_USER
            if not is_sidecar(container_properties["image"]) else []
        )
    ]:
        yield AciContainerPropertyVolumeMounts(
                **{k: v for k, v in vol_mount.items() if v is not None})


def arm_container_exec_procs_to_aci_policy_spec_exec_procs(
    container_properties: dict,
    debug_mode: bool,
) -> Iterator[AciContainerPropertyVolumeMounts]:

    for exec_process in [
        *container_properties.get("execProcesses", []),
        *get_probe_exec_processes(container_properties),
        *(config.DEBUG_MODE_SETTINGS.get("execProcesses", []) if debug_mode else []),
    ]:
        yield AciContainerPropertyExecProcesses(**exec_process)


def arm_container_props_to_aci_policy_spec_props(
    container_group: dict,
    container_properties: dict,
    parameters: dict,
    debug_mode: bool,
    allow_stdio_access: bool,
    approve_wildcards: bool,
) -> AciContainerProperties:

    capabilities = container_properties.get("securityContext", {}).pop("capabilities", None)

    return AciContainerProperties(
        image=container_properties["image"],
        command=container_properties.get("command", []),
        allowStdioAccess=allow_stdio_access,
        environmentVariables=list(arm_container_env_to_aci_policy_spec_env(
            container_properties=container_properties,
            parameters=parameters,
            approve_wildcards=approve_wildcards,
        )),
        volumeMounts=list(arm_container_volumes_to_aci_policy_spec_volumes(
            container_properties=container_properties,
            container_group_volumes=container_group["properties"].get("volumes", [])),
        ),
        execProcesses=list(arm_container_exec_procs_to_aci_policy_spec_exec_procs(
            container_properties=container_properties,
            debug_mode=debug_mode,
        )),
        securityContext=AciContainerPropertySecurityContext(
            capabilities=AciContainerPropertySecurityContextCapabilities(
                add=capabilities.get("add", []),
                drop=capabilities.get("drop", []),
            ) if capabilities else None,
            **container_properties["securityContext"]
        ) if "securityContext" in container_properties else None,
    )


def arm_container_to_aci_policy_spec_container(
    container_group: dict,
    container: dict,
    parameters: dict,
    debug_mode: bool,
    allow_stdio_access: bool,
    approve_wildcards: bool,
) -> AciContainerSpec:

    return AciContainerSpec(
        name=container["name"],
        properties=arm_container_props_to_aci_policy_spec_props(
            container_group=container_group,
            container_properties=container["properties"],
            parameters=parameters,
            debug_mode=debug_mode,
            allow_stdio_access=allow_stdio_access,
            approve_wildcards=approve_wildcards,
        ),
    )


def arm_container_group_to_aci_policy_spec_fragments(
    container_group: dict,
) -> Iterator[AciFragmentSpec]:

    for fragment in container_group.get("properties", {}).get("standaloneFragments", []):
        yield AciFragmentSpec(**fragment)


def arm_container_group_to_aci_policy_spec(
    container_group: dict,
    parameters: dict,
    fragments: list[AciFragmentSpec],
    debug_mode: bool,
    allow_stdio_access: bool,
    approve_wildcards: bool,
) -> AciPolicySpec:

    containers = container_group.get("properties", {})["containers"]
    assert containers

    return AciPolicySpec(
        fragments=[
            *(fragments if not container_group.get("tags", {}).get("Annotate-zero-sidecar") else []),
            *arm_container_group_to_aci_policy_spec_fragments(container_group),
        ],
        containers=[
            arm_container_to_aci_policy_spec_container(
                container_group=container_group,
                container=c,
                parameters=parameters,
                debug_mode=debug_mode,
                allow_stdio_access=allow_stdio_access,
                approve_wildcards=approve_wildcards,
            )
            for c in containers + container_group.get("properties", {}).get("initContainers", [])
        ]
    )


def arm_to_aci_policy_spec(
    arm_template: dict,
    arm_template_parameters: dict,
    fragments: list[AciFragmentSpec],
    debug_mode: bool = False,
    allow_stdio_access: bool = True,
    approve_wildcards: bool = False,
) -> Iterator[AciPolicySpec]:

    for eval_func in EVAL_FUNCS:
        arm_template = eval_func(arm_template, arm_template_parameters)

    parameters = arm_template.get("parameters", {})

    for resource in arm_template.get("resources", []):
        parser = {
            "Microsoft.ContainerInstance/containerGroups": arm_container_group_to_aci_policy_spec,
            "Microsoft.ContainerInstance/containerGroupProfiles": arm_container_group_to_aci_policy_spec,
        }.get(resource["type"], (lambda r, p, f, d, io, w: None))

        spec = parser(resource, parameters, fragments, debug_mode, allow_stdio_access, approve_wildcards)
        if spec is not None:
            yield spec
