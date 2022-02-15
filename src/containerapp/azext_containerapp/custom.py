# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from platform import platform
from turtle import update
from azure.cli.core.azclierror import (RequiredArgumentMissingError, ResourceNotFoundError, ValidationError)
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import sdk_no_wait
from knack.util import CLIError
from knack.log import get_logger
from msrestazure.tools import parse_resource_id

from ._client_factory import handle_raw_exception
from ._clients import ManagedEnvironmentClient, ContainerAppClient
from ._models import (ManagedEnvironment, VnetConfiguration, AppLogsConfiguration, LogAnalyticsConfiguration,
                     Ingress, Configuration, Template, RegistryCredentials, ContainerApp, Dapr, ContainerResources, Scale, Container)
from ._utils import (_validate_subscription_registered, _get_location_from_resource_group, _ensure_location_allowed,
                    parse_secret_flags, store_as_secret_and_return_secret_ref, parse_list_of_strings, parse_env_var_flags)

logger = get_logger(__name__)


def create_containerapp(cmd,
                        name,
                        resource_group_name,
                        yaml=None,
                        image_name=None,
                        managed_env=None,
                        min_replicas=None,
                        max_replicas=None,
                        target_port=None,
                        transport="auto",
                        ingress=None,
                        revisions_mode=None,
                        secrets=None,
                        env_vars=None,
                        cpu=None,
                        memory=None,
                        registry_server=None,
                        registry_user=None,
                        registry_pass=None,
                        dapr_enabled=False,
                        dapr_app_port=None,
                        dapr_app_id=None,
                        dapr_app_protocol=None,
                        # dapr_components=None,
                        location=None,
                        startup_command=None,
                        args=None,
                        tags=None,
                        no_wait=False):
    location = location or _get_location_from_resource_group(cmd.cli_ctx, resource_group_name)

    _validate_subscription_registered(cmd, "Microsoft.App")
    _ensure_location_allowed(cmd, location, "Microsoft.App")

    if yaml:
        # TODO: Implement yaml
        raise CLIError("--yaml is not yet implemented")

    if image_name is None:
        raise RequiredArgumentMissingError('Usage error: --image is required if not using --yaml')

    if managed_env is None:
        raise RequiredArgumentMissingError('Usage error: --environment is required if not using --yaml')

    # Validate managed environment
    parsed_managed_env = parse_resource_id(managed_env)
    managed_env_name = parsed_managed_env['name']
    managed_env_rg = parsed_managed_env['resource_group']
    managed_env_info = None

    try:
        managed_env_info = ManagedEnvironmentClient.show(cmd=cmd, resource_group_name=managed_env_rg, name=managed_env_name)
    except:
        pass

    if not managed_env_info:
        raise ValidationError("The environment '{}' does not exist. Specify a valid environment".format(managed_env))

    location = location or managed_env_info.location

    external_ingress = None
    if ingress is not None:
        if ingress.lower() == "internal":
            external_ingress = False
        elif ingress.lower() == "external":
            external_ingress = True

    ingress_def = None
    if target_port is not None and ingress is not None:
        ingress_def = Ingress
        ingress_def["external"] = external_ingress
        ingress_def["targetPort"] = target_port
        ingress_def["transport"] = transport

    secrets_def = None
    if secrets is not None:
        secrets_def = parse_secret_flags(secrets)

    registries_def = None
    if registry_server is not None:
        registries_def = RegistryCredentials
        registries_def["server"] = registry_server
        registries_def["username"] = registry_user

        if secrets_def is None:
            secrets_def = []
        registries_def["passwordSecretRef"] = store_as_secret_and_return_secret_ref(secrets_def, registry_user, registry_server, registry_pass)

    config_def = Configuration
    config_def["secrets"] = secrets_def
    config_def["activeRevisionsMode"] = revisions_mode
    config_def["ingress"] = ingress_def
    config_def["registries"] = [registries_def]

    scale_def = None
    if min_replicas is not None or max_replicas is not None:
        scale_def = Scale
        scale_def["minReplicas"] = min_replicas
        scale_def["maxReplicas"] = max_replicas

    resources_def = None
    if cpu is not None or memory is not None:
        resources_def = ContainerResources
        resources_def["cpu"] = cpu
        resources_def["memory"] = memory

    container_def = Container
    container_def["name"] = name
    container_def["image"] = image_name
    if env_vars is not None:
        container_def["env"] = parse_env_var_flags(env_vars)
    if startup_command is not None:
        container_def["command"] = parse_list_of_strings(startup_command)
    if args is not None:
        container_def["args"] = parse_list_of_strings(args)
    if resources_def is not None:
        container_def["resources"] = resources_def

    dapr_def = None
    if dapr_enabled:
        dapr_def = Dapr
        dapr_def["daprEnabled"] = True
        dapr_def["appId"] = dapr_app_id
        dapr_def["appPort"] = dapr_app_port
        dapr_def["appProtocol"] = dapr_app_protocol

    template_def = Template
    template_def["containers"] = [container_def]
    template_def["scale"] = scale_def
    template_def["dapr"] = dapr_def

    containerapp_def = ContainerApp
    containerapp_def["location"] = location
    containerapp_def["properties"]["managedEnvironmentId"] = managed_env
    containerapp_def["properties"]["configuration"] = config_def
    containerapp_def["properties"]["template"] = template_def
    containerapp_def["tags"] = tags

    try:
        r = ContainerAppClient.create_or_update(
            cmd=cmd, resource_group_name=resource_group_name, name=name, container_app_envelope=containerapp_def, no_wait=no_wait)

        if "properties" in r and "provisioningState" in r["properties"] and r["properties"]["provisioningState"].lower() == "waiting" and not no_wait:
            logger.warning('Containerapp creation in progress. Please monitor the creation using `az containerapp show -n {} -g {}`'.format(name, resource_group_name))

        return r
    except Exception as e:
        handle_raw_exception(e)


def update_containerapp(cmd,
                        name,
                        resource_group_name,
                        yaml=None,
                        image_name=None,
                        min_replicas=None,
                        max_replicas=None,
                        ingress=None,
                        target_port=None,
                        transport=None,
                        # traffic_weights=None,
                        revisions_mode=None,
                        secrets=None,
                        env_vars=None,
                        cpu=None,
                        memory=None,
                        registry_server=None,
                        registry_user=None,
                        registry_pass=None,
                        dapr_enabled=None,
                        dapr_app_port=None,
                        dapr_app_id=None,
                        dapr_app_protocol=None,
                        # dapr_components=None,
                        revision_suffix=None,
                        startup_command=None,
                        args=None,
                        tags=None,
                        no_wait=False):
    _validate_subscription_registered(cmd, "Microsoft.App")

    if yaml:
        # TODO: Implement yaml
        raise CLIError("--yaml is not yet implemented")

    containerapp_def = None
    try:
        containerapp_def = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if not containerapp_def:
        raise CLIError("The containerapp '{}' does not exist".format(name))

    update_map = {}
    update_map['secrets'] = secrets is not None
    update_map['ingress'] = ingress or target_port or transport
    update_map['registries'] = registry_server or registry_user or registry_pass
    update_map['scale'] = min_replicas or max_replicas
    update_map['container'] = image_name or env_vars or cpu or memory or startup_command or args
    update_map['dapr'] = dapr_enabled or dapr_app_port or dapr_app_id or dapr_app_protocol
    update_map['configuration'] = update_map['secrets'] or update_map['ingress'] or update_map['registries'] or revisions_mode is not None

    if update_map['container'] and len(containerapp_def['properties']['template']['containers']) > 1:
        raise CLIError("Usage error: trying to update image, environment variables, resources claims on a multicontainer containerapp. Please use --yaml or ARM templates for multicontainer containerapp update")

    if tags:
        containerapp_def['tags'] = tags

    if revision_suffix is not None:
        containerapp_def["properties"]["template"]["revisionSuffix"] = revision_suffix

    # Containers
    if image_name is not None:
        containerapp_def["properties"]["template"]["containers"][0]["image"] = image_name
    if env_vars is not None:
        containerapp_def["properties"]["template"]["containers"][0]["env"] = parse_env_var_flags(env_vars)
    if startup_command is not None:
        containerapp_def["properties"]["template"]["containers"][0]["command"] = parse_list_of_strings(startup_command)
    if args is not None:
        containerapp_def["properties"]["template"]["containers"][0]["args"] = parse_list_of_strings(startup_command)
    if cpu is not None or memory is not None:
        resources = containerapp_def["properties"]["template"]["containers"][0]["resources"]
        if resources:
            if cpu is not None:
                resources["cpu"] = cpu
            if memory is not None:
                resources["memory"] = memory
        else:
            resources = containerapp_def["properties"]["template"]["containers"][0]["resources"] = {
                "cpu": cpu,
                "memory": memory
            }

    # Scale
    if update_map["scale"]:
        if "scale" not in containerapp_def["properties"]["template"]:
            containerapp_def["properties"]["template"]["scale"] = {}
        if min_replicas is not None:
            containerapp_def["properties"]["template"]["scale"]["minReplicas"] = min_replicas
        if max_replicas is not None:
            containerapp_def["properties"]["template"]["scale"]["maxReplicas"] = max_replicas

    # Dapr
    if update_map["dapr"]:
        if "dapr" not in containerapp_def["properties"]["template"]:
            containerapp_def["properties"]["template"]["dapr"] = {}
        if dapr_enabled is not None:
            containerapp_def["properties"]["template"]["dapr"]["daprEnabled"] = dapr_enabled
        if dapr_app_id is not None:
            containerapp_def["properties"]["template"]["dapr"]["appId"] = dapr_app_id
        if dapr_app_port is not None:
            containerapp_def["properties"]["template"]["dapr"]["appPort"] = dapr_app_port
        if dapr_app_protocol is not None:
            containerapp_def["properties"]["template"]["dapr"]["appProtocol"] = dapr_app_protocol

    # Configuration
    if revisions_mode is not None:
        containerapp_def["properties"]["configuration"]["activeRevisionsMode"] = revisions_mode

    if update_map["ingress"]:
        external_ingress = None
        if ingress is not None:
            if ingress.lower() == "internal":
                external_ingress = False
            elif ingress.lower() == "external":
                external_ingress = True
        containerapp_def["properties"]["configuration"]["external"] = external_ingress

        if target_port is not None:
            containerapp_def["properties"]["configuration"]["targetPort"] = target_port

        config = containerapp_def["properties"]["configuration"]
        if (config["targetPort"] is not None and config["external"] is None) or (config["targetPort"] is None and config["external"] is not None):
            raise ValidationError("Usage error: must specify --target-port with --ingress")

        if transport is not None:
            containerapp_def["properties"]["configuration"]["transport"] = transport

    # TODO: Need list_secrets API to do secrets before registries

    if update_map["registries"]:
        registries_def = None
        registry = None

        if "registries" not in containerapp_def["properties"]["configuration"]:
            containerapp_def["properties"]["configuration"]["registries"] = []

        registries_def = containerapp_def["properties"]["configuration"]["registries"]

        if len(registries_def) == 0: # Adding new registry
            if not(registry_server is not None and registry_user is not None and registry_pass is not None):
                raise ValidationError("Usage error: --registry-login-server, --registry-password and --registry-username are required when adding a registry")

            registry = RegistryCredentials
            registry["server"] = registry_server
            registry["username"] = registry_user
            registries_def.append(registry)
        elif len(registries_def) == 1: # Modifying single registry
            if registry_server is not None:
                registries_def[0]["server"] = registry_server
            if registry_user is not None:
                registries_def[0]["username"] = registry_user
        else: # Multiple registries
            raise ValidationError("Usage error: trying to update image, environment variables, resources claims on a multicontainer containerapp. Please use --yaml or ARM templates for multicontainer containerapp update")

        if "secrets" not in containerapp_def["properties"]["configuration"]:
            containerapp_def["properties"]["configuration"]["secrets"] = []
        secrets_def = containerapp_def["properties"]["configuration"]["secrets"]

        registries_def[0]["passwordSecretRef"] = store_as_secret_and_return_secret_ref(secrets_def, registry_user, registry_server, registry_pass, update_existing_secret=True)

    try:
        r = ContainerAppClient.create_or_update(
            cmd=cmd, resource_group_name=resource_group_name, name=name, container_app_envelope=containerapp_def, no_wait=no_wait)

        if "properties" in r and "provisioningState" in r["properties"] and r["properties"]["provisioningState"].lower() == "waiting" and not no_wait:
            logger.warning('Containerapp update in progress. Please monitor the update using `az containerapp show -n {} -g {}`'.format(name, resource_group_name))

        return r
    except Exception as e:
        handle_raw_exception(e)


def scale_containerapp(cmd, name, resource_group_name, min_replicas=None, max_replicas=None, no_wait=False):
    containerapp_def = None
    try:
        containerapp_def = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if not containerapp_def:
        raise CLIError("The containerapp '{}' does not exist".format(name))

    shouldWork = False # TODO: Should only setting minReplicas and maxReplicas in the body work? Or do we have to do a GET on the containerapp, add in secrets, then modify minReplicas and maxReplicas
    if shouldWork:
        updated_containerapp_def = {
            "location": containerapp_def["location"],
            "properties": {
                "template": {
                    "scale": None
                }
            }
        }

        if "scale" not in containerapp_def["properties"]["template"]:
            updated_containerapp_def["properties"]["template"]["scale"] = {}
        else:
            updated_containerapp_def["properties"]["template"]["scale"] = containerapp_def["properties"]["template"]["scale"]

        if min_replicas is not None:
            updated_containerapp_def["properties"]["template"]["scale"]["minReplicas"] = min_replicas

        if max_replicas is not None:
            updated_containerapp_def["properties"]["template"]["scale"]["maxReplicas"] = max_replicas

        try:
            r = ContainerAppClient.create_or_update(
                cmd=cmd, resource_group_name=resource_group_name, name=name, container_app_envelope=updated_containerapp_def, no_wait=no_wait)

            if "properties" in r and "provisioningState" in r["properties"] and r["properties"]["provisioningState"].lower() == "waiting" and not no_wait:
                logger.warning('Containerapp scale in progress. Please monitor the update using `az containerapp show -n {} -g {}`'.format(name, resource_group_name))

            return r
        except Exception as e:
            handle_raw_exception(e)
    else:
        if "scale" not in containerapp_def["properties"]["template"]:
            containerapp_def["properties"]["template"]["scale"] = {}

        if min_replicas is not None:
            containerapp_def["properties"]["template"]["scale"]["minReplicas"] = min_replicas

        if max_replicas is not None:
            containerapp_def["properties"]["template"]["scale"]["maxReplicas"] = max_replicas

        del containerapp_def["properties"]["configuration"]["registries"]
        del containerapp_def["properties"]["configuration"]["secrets"]

        try:
            r = ContainerAppClient.create_or_update(
                cmd=cmd, resource_group_name=resource_group_name, name=name, container_app_envelope=containerapp_def, no_wait=no_wait)

            if "properties" in r and "provisioningState" in r["properties"] and r["properties"]["provisioningState"].lower() == "waiting" and not no_wait:
                logger.warning('Containerapp scale in progress. Please monitor the update using `az containerapp show -n {} -g {}`'.format(name, resource_group_name))

            return r
        except Exception as e:
            handle_raw_exception(e)


def show_containerapp(cmd, name, resource_group_name):
    _validate_subscription_registered(cmd, "Microsoft.App")

    try:
        return ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except CLIError as e:
        handle_raw_exception(e)


def list_containerapp(cmd, resource_group_name=None):
    _validate_subscription_registered(cmd, "Microsoft.App")

    try:
        containerapps = []
        if resource_group_name is None:
            containerapps = ContainerAppClient.list_by_subscription(cmd=cmd)
        else:
            containerapps = ContainerAppClient.list_by_resource_group(cmd=cmd, resource_group_name=resource_group_name)

        return containerapps
    except CLIError as e:
        handle_raw_exception(e)


def delete_containerapp(cmd, name, resource_group_name, no_wait=False):
    _validate_subscription_registered(cmd, "Microsoft.App")

    try:
        r = ContainerAppClient.delete(cmd=cmd, name=name, resource_group_name=resource_group_name, no_wait=no_wait)
        if not r and not no_wait:
            logger.warning('Containerapp successfully deleted')
        return r
    except CLIError as e:
        handle_raw_exception(e)


def create_managed_environment(cmd,
                              name,
                              resource_group_name,
                              logs_customer_id,
                              logs_key,
                              logs_destination="log-analytics",
                              location=None,
                              instrumentation_key=None,
                              infrastructure_subnet_resource_id=None,
                              app_subnet_resource_id=None,
                              docker_bridge_cidr=None,
                              platform_reserved_cidr=None,
                              platform_reserved_dns_ip=None,
                              internal_only=False,
                              tags=None,
                              no_wait=False):

    location = location or _get_location_from_resource_group(cmd.cli_ctx, resource_group_name)

    _validate_subscription_registered(cmd, "Microsoft.App")
    _ensure_location_allowed(cmd, location, "Microsoft.App")

    log_analytics_config_def = LogAnalyticsConfiguration
    log_analytics_config_def["customerId"] = logs_customer_id
    log_analytics_config_def["sharedKey"] = logs_key

    app_logs_config_def = AppLogsConfiguration
    app_logs_config_def["destination"] = logs_destination
    app_logs_config_def["logAnalyticsConfiguration"] = log_analytics_config_def

    managed_env_def = ManagedEnvironment
    managed_env_def["location"] = location
    managed_env_def["properties"]["internalLoadBalancerEnabled"] = False
    managed_env_def["properties"]["appLogsConfiguration"] = app_logs_config_def
    managed_env_def["tags"] = tags

    if instrumentation_key is not None:
        managed_env_def["properties"]["daprAIInstrumentationKey"] = instrumentation_key

    if infrastructure_subnet_resource_id or app_subnet_resource_id or docker_bridge_cidr or platform_reserved_cidr or platform_reserved_dns_ip:
        vnet_config_def = VnetConfiguration

        if infrastructure_subnet_resource_id is not None:
            if not app_subnet_resource_id:
                raise ValidationError('App subnet resource ID needs to be supplied with infrastructure subnet resource ID.')
            vnet_config_def["infrastructureSubnetId"] = infrastructure_subnet_resource_id

        if app_subnet_resource_id is not None:
            if not infrastructure_subnet_resource_id:
                raise ValidationError('Infrastructure subnet resource ID needs to be supplied with app subnet resource ID.')
            vnet_config_def["runtimeSubnetId"] = app_subnet_resource_id

        if docker_bridge_cidr is not None:
            vnet_config_def["dockerBridgeCidr"] = docker_bridge_cidr

        if platform_reserved_cidr is not None:
            vnet_config_def["platformReservedCidr"] = platform_reserved_cidr

        if platform_reserved_dns_ip is not None:
            vnet_config_def["platformReservedDnsIP"] = platform_reserved_dns_ip

        managed_env_def["properties"]["vnetConfiguration"] = vnet_config_def

    if internal_only:
        if not infrastructure_subnet_resource_id or not app_subnet_resource_id:
            raise ValidationError('Infrastructure subnet resource ID and App subnet resource ID need to be supplied for internal only environments.')
        managed_env_def["properties"]["internalLoadBalancerEnabled"] = True

    try:
        r = ManagedEnvironmentClient.create(
            cmd=cmd, resource_group_name=resource_group_name, name=name, managed_environment_envelope=managed_env_def, no_wait=no_wait)

        if "properties" in r and "provisioningState" in r["properties"] and r["properties"]["provisioningState"].lower() == "waiting" and not no_wait:
            logger.warning('Containerapp environment creation in progress. Please monitor the creation using `az containerapp env show -n {} -g {}`'.format(name, resource_group_name))

        return r
    except Exception as e:
        handle_raw_exception(e)


def update_managed_environment(cmd,
                            name,
                            resource_group_name,
                            tags=None,
                            no_wait=False):
    raise CLIError('Containerapp env update is not yet supported.')

    _validate_subscription_registered(cmd, "Microsoft.App")

    managed_env_def = ManagedEnvironment
    managed_env_def["tags"] = tags

    try:
        r = ManagedEnvironmentClient.update(
            cmd=cmd, resource_group_name=resource_group_name, name=name, managed_environment_envelope=managed_env_def, no_wait=no_wait)

        if "properties" in r and "provisioningState" in r["properties"] and r["properties"]["provisioningState"].lower() == "waiting" and not no_wait:
            logger.warning('Containerapp environment update in progress. Please monitor the creation using `az containerapp env show -n {} -g {}`'.format(name, resource_group_name))

        return r
    except Exception as e:
        handle_raw_exception(e)


def show_managed_environment(cmd, name, resource_group_name):
    _validate_subscription_registered(cmd, "Microsoft.App")

    try:
        return ManagedEnvironmentClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except CLIError as e:
        handle_raw_exception(e)


def list_managed_environments(cmd, resource_group_name=None):
    _validate_subscription_registered(cmd, "Microsoft.App")

    try:
        managed_envs = []
        if resource_group_name is None:
            managed_envs = ManagedEnvironmentClient.list_by_subscription(cmd=cmd)
        else:
            managed_envs = ManagedEnvironmentClient.list_by_resource_group(cmd=cmd, resource_group_name=resource_group_name)

        return managed_envs
    except CLIError as e:
        handle_raw_exception(e)


def delete_managed_environment(cmd, name, resource_group_name, no_wait=False):
    _validate_subscription_registered(cmd, "Microsoft.App")

    try:
        r = ManagedEnvironmentClient.delete(cmd=cmd, name=name, resource_group_name=resource_group_name, no_wait=no_wait)
        if not r and not no_wait:
            logger.warning('Containerapp environment successfully deleted')
        return r
    except CLIError as e:
        handle_raw_exception(e)
