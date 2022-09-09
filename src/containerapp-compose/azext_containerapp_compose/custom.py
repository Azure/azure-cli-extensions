# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.core.azclierror import InvalidArgumentValueError
from knack.log import get_logger
from knack.prompting import prompt, prompt_choice_list
from pycomposefile import ComposeFile


logger = get_logger(__name__)


def resolve_configuration_element_list(compose_service, unsupported_configuration, area=None):
    if area is not None:
        compose_service = getattr(compose_service, area)
    config_list = []
    for configuration_element in unsupported_configuration:
        try:
            attribute = getattr(compose_service, configuration_element)
        except AttributeError:
            logger.critical("Failed to resolve %s", configuration_element)
        if attribute is not None:
            config_list.append(f"{compose_service.compose_path}/{configuration_element}")
    return config_list


def warn_about_unsupported_build_configuration(compose_service):
    unsupported_configuration = ["args", "ssh", "cache_from", "cache_to", "extra_hosts",
                                 "isolation", "labels", "no_cache", "pull", "shm_size",
                                 "target", "secrets", "tags"]
    if compose_service.build is not None:
        config_list = resolve_configuration_element_list(compose_service, unsupported_configuration, 'build')
        message = "These build configuration settings from the docker-compose file are yet supported."
        message += " Currently, we support supplying a build context and optionally target Dockerfile for a service."
        message += " See https://aka.ms/containerapp/compose/build_support for more information or to add feedback."
        if len(config_list) >= 1:
            logger.warning(message)
            for item in config_list:
                logger.warning("     %s", item)


def warn_about_unsupported_runtime_host_configuration(compose_service):
    unsupported_configuration = ["blkio_config", "cpu_count", "cpu_percent", "cpu_shares", "cpu_period",
                                 "cpu_quota", "cpu_rt_runtime", "cpu_rt_period", "cpuset", "cap_add",
                                 "cap_drop", "cgroup_parent", "configs", "credential_spec",
                                 "device_cgroup_rules", "devices", "dns", "dns_opt", "dns_search",
                                 "domainname", "external_links", "extra_hosts", "group_add", "healthcheck",
                                 "hostname", "init", "ipc", "isolation", "links", "logging", "mem_limit",
                                 "mem_swappiness", "memswap_limit", "oom_kill_disable", "oom_score_adj",
                                 "pid", "pids_limit", "privileged", "profiles", "pull_policy", "read_only",
                                 "restart", "runtime", "security_opt", "shm_size", "stdin_open",
                                 "stop_grace_period", "stop_signal", "storage_opt", "sysctls", "tmpfs",
                                 "tty", "ulimits", "user", "working_dir"]
    config_list = resolve_configuration_element_list(compose_service, unsupported_configuration)
    message = "These container and host configuration elements from the docker-compose file are not supported"
    message += " in Azure Container Apps. For more information about supported configuration,"
    message += " please see https://aka.ms/containerapp/compose/configuration"
    if len(config_list) >= 1:
        logger.warning(message)
        for item in config_list:
            logger.warning("     %s", item)


def warn_about_unsupported_volumes(compose_service):
    unsupported_configuration = ["volumes", "volumes_from"]
    config_list = resolve_configuration_element_list(compose_service, unsupported_configuration)
    message = "These volume mount elements from the docker-compose file are not supported"
    message += " in Azure Container Apps. For more information about supported storage configuration,"
    message += " please see https://aka.ms/containerapp/compose/volumes"
    if len(config_list) >= 1:
        logger.warning(message)
        for item in config_list:
            logger.warning("     %s", item)


def warn_about_unsupported_network(compose_service):
    unsupported_configuration = ["networks", "network_mode", "mac_address"]
    config_list = resolve_configuration_element_list(compose_service, unsupported_configuration)
    message = "These network configuration settings from the docker-compose file are not supported"
    message += " in Azure Container Apps. For more information about supported networking configuration,"
    message += " please see https://aka.ms/containerapp/compose/networking"
    if len(config_list) >= 1:
        logger.warning(message)
        for item in config_list:
            logger.warning("     %s", item)


def warn_about_unsupported_elements(compose_service):
    warn_about_unsupported_build_configuration(compose_service)
    warn_about_unsupported_runtime_host_configuration(compose_service)
    warn_about_unsupported_volumes(compose_service)
    warn_about_unsupported_network(compose_service)


def check_supported_platform(platform):
    if platform is not None:
        platform = platform.split('/')
        if len(platform) >= 2:
            return platform[0] == 'linux' and platform[1] == 'amd64'
        return platform[0] == 'linux'
    return True


def create_containerapps_from_compose(cmd,  # pylint: disable=R0914
                                      resource_group_name,
                                      managed_env,
                                      compose_file_path='./docker-compose.yml',
                                      registry_server=None,
                                      registry_user=None,
                                      registry_pass=None,
                                      transport_mapping=None,
                                      logs_workspace_name=None,
                                      location=None,
                                      tags=None):
    from ._monkey_patch import (
        create_containerapp_from_service,
        create_containerapps_compose_environment,
        build_containerapp_from_compose_service,
        load_yaml_file,
        show_managed_environment)

    logger.info(   # pylint: disable=W1203
        f"Creating the Container Apps managed environment {managed_env} under {resource_group_name} in {location}.")

    try:
        managed_environment = show_managed_environment(cmd=cmd,
                                                       resource_group_name=resource_group_name,
                                                       managed_env_name=managed_env)
    except:  # pylint: disable=W0702
        managed_environment = create_containerapps_compose_environment(cmd,
                                                                       managed_env,
                                                                       resource_group_name,
                                                                       location,
                                                                       logs_workspace_name=logs_workspace_name,
                                                                       tags=tags)

    os.environ["AZURE_CONTAINERAPPS_ENV_DEFAULT_DOMAIN"] = managed_environment["properties"]["defaultDomain"]
    os.environ["AZURE_CONTAINERAPPS_ENV_STATIC_IP"] = managed_environment["properties"]["staticIp"]

    compose_yaml = load_yaml_file(compose_file_path)
    parsed_compose_file = ComposeFile(compose_yaml)

    containerapps_from_compose = []
    # Using the key to iterate to get the service name
    # pylint: disable=C0201,C0206
    for service_name in parsed_compose_file.ordered_services.keys():
        service = parsed_compose_file.services[service_name]
        if not check_supported_platform(service.platform):
            message = "Unsupported platform found. "
            message += "Azure Container Apps only supports linux/amd64 container images."
            raise InvalidArgumentValueError(message)
        image = service.image
        warn_about_unsupported_elements(service)
        logger.info(  # pylint: disable=W1203
            f"Creating the Container Apps instance for {service_name} under {resource_group_name} in {location}.")
        ingress_type, target_port = resolve_ingress_and_target_port(service)
        registry, registry_username, registry_password = resolve_registry_from_cli_args(registry_server, registry_user, registry_pass)  # pylint: disable=C0301
        transport_setting = resolve_transport_from_cli_args(service_name, transport_mapping)
        startup_command, startup_args = resolve_service_startup_command(service)
        cpu, memory = validate_memory_and_cpu_setting(
            resolve_cpu_configuration_from_service(service),
            resolve_memory_configuration_from_service(service)
        )
        replicas = resolve_replicas_from_service(service)
        environment = resolve_environment_from_service(service)
        secret_vars, secret_env_ref = resolve_secret_from_service(service, parsed_compose_file.secrets)
        if environment is not None and secret_env_ref is not None:
            environment.extend(secret_env_ref)
        elif secret_env_ref is not None:
            environment = secret_env_ref

        if service.build is not None:
            logger.warning("Build configuration defined for this service.")
            logger.warning("The build will be performed by Azure Container Registry.")
            context = service.build.context
            dockerfile = "Dockerfile"
            if service.build.dockerfile is not None:
                dockerfile = service.build.dockerfile
            image, registry, registry_username, registry_password = build_containerapp_from_compose_service(
                cmd,
                service_name,
                context,
                dockerfile,
                resource_group_name,
                managed_env,
                location,
                image,
                target_port,
                ingress_type,
                registry,
                registry_username,
                registry_password,
                environment)

        containerapps_from_compose.append(
            create_containerapp_from_service(cmd,
                                             service_name,
                                             resource_group_name,
                                             image=image,
                                             container_name=service.container_name,
                                             managed_env=managed_environment["id"],
                                             ingress=ingress_type,
                                             target_port=target_port,
                                             registry_server=registry,
                                             registry_user=registry_username,
                                             registry_pass=registry_password,
                                             transport=transport_setting,
                                             startup_command=startup_command,
                                             args=startup_args,
                                             cpu=cpu,
                                             memory=memory,
                                             env_vars=environment,
                                             secrets=secret_vars,
                                             min_replicas=replicas,
                                             max_replicas=replicas,)
        )
    return containerapps_from_compose


def service_deploy_exists(service):
    return service.deploy is not None


def service_deploy_resources_exists(service):
    return service_deploy_exists(service) and service.deploy.resources is not None


def flatten_list(source_value):
    flat_list = []
    for sub_list in source_value:
        flat_list += sub_list
    return flat_list


def resolve_transport_from_cli_args(service_name, transport):
    if transport is not None:
        transport = flatten_list(transport)
        for setting in transport:
            key, value = setting.split('=')
            if key.lower() == service_name.lower():
                return value
    return 'auto'


def resolve_registry_from_cli_args(registry_server, registry_user, registry_pass):
    if registry_server is not None:
        if registry_user is None and registry_pass is None:
            registry_user = prompt("Please enter the registry's username: ")
            registry_pass = prompt("Please enter the registry's password: ")
        elif registry_user is not None and registry_pass is None:
            registry_pass = prompt("Please enter the registry's password: ")
    return (registry_server, registry_user, registry_pass)


def resolve_environment_from_service(service):
    env_array = []

    env_vars = service.resolve_environment_hierarchy()

    if env_vars is None:
        return None

    for k, v in env_vars.items():
        if v is None:
            v = prompt(f"{k} is empty. What would you like the value to be? ")
        env_array.append(f"{k}={v}")

    return env_array


def resolve_secret_from_service(service, secrets_map):
    secret_array = []
    secret_env_ref = []

    if service.secrets is None:
        return (None, None)

    for secret in service.secrets:

        secret_config = secrets_map[secret.source]
        if secret_config is not None and secret_config.file is not None:
            value = secret_config.file.readFile()
            if secret.target is None:
                secret_name = secret.source.replace('_', '-')
            else:
                secret_name = secret.target.replace('_', '-')
            secret_array.append(f"{secret_name}={value}")
            secret_env_ref.append(f"{secret_name}=secretref:{secret_name}")

    if len(secret_array) == 0:
        return (None, None)

    logger.warning("Note: Secrets will be mapped as secure environment variables in Azure Container Apps.")

    return (secret_array, secret_env_ref)


def resolve_replicas_from_service(service):
    replicas = None

    if service.scale:
        replicas = service.scale
    if service_deploy_exists(service):
        if service.deploy.replicas is not None:
            replicas = service.deploy.replicas
        if service.deploy.mode == "global":
            replicas = 1

    return replicas


def valid_resource_settings():
    # vCPU and Memory reservations
    # https://docs.microsoft.com/azure/container-apps/containers#configuration
    return {
        "0.25": "0.5",
        "0.5": "1",
        "0.75": "1.5",
        "1.0": "2",
        "1.25": "2.5",
        "1.5": "3",
        "1.75": "3.5",
        "2.0": "4",
    }


def validate_memory_and_cpu_setting(cpu, memory):
    settings = valid_resource_settings()
    if cpu in settings.keys():  # pylint: disable=C0201
        if memory != settings[cpu]:
            if memory is not None:
                warning = f"Unsupported memory reservation request of {memory}. "
                warning += f"The default value of {settings[cpu]} GB for {cpu} vCPUs will be used. "
                warning += "Please see memory and vCPU configuration options for Azure Container Apps at "
                warning += "https://docs.microsoft.com/en-us/azure/container-apps/containers#configuration "
                logger.warning(warning)
            memory = settings[cpu]
        return (cpu, f"{memory}Gi")

    if memory in settings.values():
        new_cpu = "0.25"
        for c, m in settings.items():
            if memory == m:
                new_cpu = c
        if cpu != new_cpu:
            if cpu is not None:
                warning = f"Unsupported cpu configuration request of {cpu}. "
                warning += f"The default value of {new_cpu} vCPUs for {memory} GB will be used. "
                warning += "Please see memory and vCPU configuration options for Azure Container Apps at "
                warning += "https://docs.microsoft.com/en-us/azure/container-apps/containers#configuration "
                logger.warning(warning)
        return (new_cpu, f"{memory}Gi")

    warning = ""
    if cpu is not None and memory is not None:
        warning += f"Invalid CPU and memory reservation request of {cpu} vCPU and {memory}. "
    elif cpu is not None:
        warning += f"Invalid CPU reservation request of {cpu} vCPU. "
    elif memory is not None:
        warning += f"Invalid memory reservation request of {memory} GB. "
    if cpu is not None or memory is not None:
        warning += "The default resource values of 0.25 vCPU and 0.5 GB will be used. "
        warning += "Please see memory and vCPU configuration options for Azure Container Apps at "
        warning += "https://docs.microsoft.com/en-us/azure/container-apps/containers#configuration "
        logger.warning(warning)
    return (None, None)


def resolve_cpu_configuration_from_service(service):
    cpu = None
    if service_deploy_resources_exists(service):
        resources = service.deploy.resources
        if resources.reservations is not None and resources.reservations.cpus is not None:
            cpu = str(resources.reservations.cpus)
    elif service.cpus is not None:
        cpu = str(service.cpus)
    return cpu


def resolve_memory_configuration_from_service(service):
    memory = None
    if service_deploy_resources_exists(service):
        resources = service.deploy.resources
        if resources.reservations is not None and resources.reservations.memory is not None:
            memory = str(resources.reservations.memory.as_gigabytes())
    elif service.mem_reservation is not None:
        memory = str(service.mem_reservation.as_gigabytes())
    return memory


def resolve_port_or_expose_list(ports, name):
    if len(ports) > 1:
        message = f"You have more than one {name} mapping defined in your docker-compose file."
        message += " Which port would you like to use? "
        choice_index = prompt_choice_list(message, ports)

    return ports[choice_index]


def resolve_ingress_and_target_port(service):
    # External Ingress Check
    if service.ports is not None:
        ingress_type = "external"

        if len(service.ports) == 1:
            target_port = service.ports[0].target
        else:
            ports_list = []

            for p in service.ports:
                ports_list.append(p.target)
            target_port = resolve_port_or_expose_list(ports_list, "port")

    # Internal Ingress Check
    elif service.expose is not None:
        ingress_type = "internal"

        if len(service.expose) == 1:
            target_port = service.expose[0]
        else:
            target_port = resolve_port_or_expose_list(service.expose, "expose")
    else:
        ingress_type = None
        target_port = None
    return (ingress_type, target_port)


def resolve_service_startup_command(service):
    startup_command_array = []
    startup_args_array = []
    if service.entrypoint is not None:
        startup_command = service.entrypoint.command_string()
        startup_command_array.append(startup_command)
        if service.command is not None:
            startup_args = service.command.command_string()
            startup_args_array.append(startup_args)
    elif service.command is not None:
        startup_args = service.command.command_string()
        startup_command_array.append(startup_args)
        startup_args_array = None
    else:
        startup_command_array = None
        startup_args_array = None
    return (startup_command_array, startup_args_array)
