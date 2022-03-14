# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.command_modules.appservice.custom import (_get_acr_cred)
from azure.cli.core.azclierror import (RequiredArgumentMissingError, ResourceNotFoundError, ValidationError)
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import sdk_no_wait
from knack.util import CLIError
from knack.log import get_logger
from urllib.parse import urlparse

from msrestazure.tools import parse_resource_id, is_valid_resource_id
from msrest.exceptions import DeserializationError
from azure.cli.command_modules.appservice.custom import _get_acr_cred
from urllib.parse import urlparse

from ._client_factory import handle_raw_exception
from ._clients import ManagedEnvironmentClient, ContainerAppClient, GitHubActionClient
from ._sdk_models import *
from ._github_oauth import get_github_access_token
from ._models import (
    ManagedEnvironment as ManagedEnvironmentModel,
    VnetConfiguration as VnetConfigurationModel,
    AppLogsConfiguration as AppLogsConfigurationModel,
    LogAnalyticsConfiguration as LogAnalyticsConfigurationModel,
    Ingress as IngressModel,
    Configuration as ConfigurationModel,
    Template as TemplateModel,
    RegistryCredentials as RegistryCredentialsModel,
    ContainerApp as ContainerAppModel,
    Dapr as DaprModel,
    ContainerResources as ContainerResourcesModel,
    Scale as ScaleModel,
    Container as ContainerModel, GitHubActionConfiguration, RegistryInfo as RegistryInfoModel, AzureCredentials as AzureCredentialsModel, SourceControl as SourceControlModel)
from ._utils import (_validate_subscription_registered, _get_location_from_resource_group, _ensure_location_allowed,
                    parse_secret_flags, store_as_secret_and_return_secret_ref, parse_list_of_strings, parse_env_var_flags,
                    _generate_log_analytics_if_not_provided, _get_existing_secrets, _convert_object_from_snake_to_camel_case,
                    _object_to_dict, _add_or_update_secrets, _remove_additional_attributes, _remove_readonly_attributes,
                    _add_or_update_env_vars, _add_or_update_tags, update_nested_dictionary, _update_traffic_Weights,
                    _get_app_from_revision, raise_missing_token_suggestion, _infer_acr_credentials, _remove_registry_secret, _remove_secret)

logger = get_logger(__name__)


# These properties should be under the "properties" attribute. Move the properties under "properties" attribute
def process_loaded_yaml(yaml_containerapp):
    if not yaml_containerapp.get('properties'):
        yaml_containerapp['properties'] = {}

    nested_properties = ["provisioningState", "managedEnvironmentId", "latestRevisionName", "latestRevisionFqdn", "customDomainVerificationId", "configuration", "template", "outboundIPAddresses"]
    for nested_property in nested_properties:
        tmp = yaml_containerapp.get(nested_property)
        if tmp:
            yaml_containerapp['properties'][nested_property] = tmp
            del yaml_containerapp[nested_property]

    return yaml_containerapp


def load_yaml_file(file_name):
    import yaml
    import errno

    try:
        with open(file_name) as stream:
            return yaml.safe_load(stream)
    except (IOError, OSError) as ex:
        if getattr(ex, 'errno', 0) == errno.ENOENT:
            raise CLIError('{} does not exist'.format(file_name))
        raise
    except (yaml.parser.ParserError, UnicodeDecodeError) as ex:
        raise CLIError('Error parsing {} ({})'.format(file_name, str(ex)))


def create_deserializer():
    from msrest import Deserializer
    import sys, inspect

    sdkClasses = inspect.getmembers(sys.modules["azext_containerapp._sdk_models"])
    deserializer = {}

    for sdkClass in sdkClasses:
        deserializer[sdkClass[0]] = sdkClass[1]

    return Deserializer(deserializer)


def update_containerapp_yaml(cmd, name, resource_group_name, file_name, from_revision=None, no_wait=False):
    yaml_containerapp = process_loaded_yaml(load_yaml_file(file_name))
    if type(yaml_containerapp) != dict:
        raise ValidationError('Invalid YAML provided. Please see https://docs.microsoft.com/azure/container-apps/azure-resource-manager-api-spec#examples for a valid containerapps YAML spec.')

    if not yaml_containerapp.get('name'):
        yaml_containerapp['name'] = name
    elif yaml_containerapp.get('name').lower() != name.lower():
        logger.warning('The app name provided in the --yaml file "{}" does not match the one provided in the --name flag "{}". The one provided in the --yaml file will be used.'.format(
            yaml_containerapp.get('name'), name))
    name = yaml_containerapp.get('name')

    if not yaml_containerapp.get('type'):
        yaml_containerapp['type'] = 'Microsoft.App/containerApps'
    elif yaml_containerapp.get('type').lower() != "microsoft.app/containerapps":
        raise ValidationError('Containerapp type must be \"Microsoft.App/ContainerApps\"')

    current_containerapp_def = None
    containerapp_def = None
    try:
        current_containerapp_def = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except Exception as ex:
        pass

    if not current_containerapp_def:
        raise ValidationError("The containerapp '{}' does not exist".format(name))

    # Change which revision we update from
    if from_revision:
        try:
            r = ContainerAppClient.show_revision(cmd=cmd, resource_group_name=resource_group_name, container_app_name=name, name=from_revision)
        except CLIError as e:
            handle_raw_exception(e)
        current_containerapp_def["properties"]["template"] = r["properties"]["template"]

    # Deserialize the yaml into a ContainerApp object. Need this since we're not using SDK
    try:
        deserializer = create_deserializer()

        containerapp_def = deserializer('ContainerApp', yaml_containerapp)
    except DeserializationError as ex:
        raise ValidationError('Invalid YAML provided. Please see https://docs.microsoft.com/azure/container-apps/azure-resource-manager-api-spec#examples for a valid containerapps YAML spec.')

    # Remove tags before converting from snake case to camel case, then re-add tags. We don't want to change the case of the tags. Need this since we're not using SDK
    tags = None
    if yaml_containerapp.get('tags'):
        tags = yaml_containerapp.get('tags')
        del yaml_containerapp['tags']

    containerapp_def = _convert_object_from_snake_to_camel_case(_object_to_dict(containerapp_def))
    containerapp_def['tags'] = tags

    # After deserializing, some properties may need to be moved under the "properties" attribute. Need this since we're not using SDK
    containerapp_def = process_loaded_yaml(containerapp_def)

    _get_existing_secrets(cmd, resource_group_name, name, current_containerapp_def)

    update_nested_dictionary(current_containerapp_def, containerapp_def)

    # Remove "additionalProperties" and read-only attributes that are introduced in the deserialization. Need this since we're not using SDK
    _remove_additional_attributes(current_containerapp_def)
    _remove_readonly_attributes(current_containerapp_def)

    '''
    # Not sure if update should replace items that are a list, or do createOrUpdate. This commented out section is the implementation for createOrUpdate.
    # (If a property is a list, do createOrUpdate, rather than just replace with new list)

    if 'properties' in containerapp_def and 'template' in containerapp_def['properties']:
        # Containers
        if 'containers' in containerapp_def['properties']['template'] and containerapp_def['properties']['template']['containers']:
            for new_container in containerapp_def['properties']['template']['containers']:
                if "name" not in new_container or not new_container["name"]:
                    raise ValidationError("The container name is not specified.")

                # Check if updating existing container
                updating_existing_container = False
                for existing_container in current_containerapp_def["properties"]["template"]["containers"]:
                    if existing_container['name'].lower() == new_container['name'].lower():
                        updating_existing_container = True

                        if 'image' in new_container and new_container['image']:
                            existing_container['image'] = new_container['image']
                        if 'env' in new_container and new_container['env']:
                            if 'env' not in existing_container or not existing_container['env']:
                                existing_container['env'] = []
                            _add_or_update_env_vars(existing_container['env'], new_container['env'])
                        if 'command' in new_container and new_container['command']:
                            existing_container['command'] = new_container['command']
                        if 'args' in new_container and new_container['args']:
                            existing_container['args'] = new_container['args']
                        if 'resources' in new_container and new_container['resources']:
                            if 'cpu' in new_container['resources'] and new_container['resources']['cpu'] is not None:
                                existing_container['resources']['cpu'] = new_container['resources']['cpu']
                            if 'memory' in new_container['resources'] and new_container['resources']['memory'] is not None:
                                existing_container['resources']['memory'] = new_container['resources']['memory']

                # If not updating existing container, add as new container
                if not updating_existing_container:
                    current_containerapp_def["properties"]["template"]["containers"].append(new_container)

    # Traffic Weights

    # Secrets

    # Registries

    # Scale rules

    # Source Controls

    '''
    try:
        r = ContainerAppClient.create_or_update(
            cmd=cmd, resource_group_name=resource_group_name, name=name, container_app_envelope=current_containerapp_def, no_wait=no_wait)

        if "properties" in r and "provisioningState" in r["properties"] and r["properties"]["provisioningState"].lower() == "waiting" and not no_wait:
            logger.warning('Containerapp creation in progress. Please monitor the creation using `az containerapp show -n {} -g {}`'.format(
                name, resource_group_name
            ))

        return r
    except Exception as e:
        handle_raw_exception(e)


def create_containerapp_yaml(cmd, name, resource_group_name, file_name, no_wait=False):
    yaml_containerapp = process_loaded_yaml(load_yaml_file(file_name))
    if type(yaml_containerapp) != dict:
        raise ValidationError('Invalid YAML provided. Please see https://docs.microsoft.com/azure/container-apps/azure-resource-manager-api-spec#examples for a valid containerapps YAML spec.')

    if not yaml_containerapp.get('name'):
        yaml_containerapp['name'] = name
    elif yaml_containerapp.get('name').lower() != name.lower():
        logger.warning('The app name provided in the --yaml file "{}" does not match the one provided in the --name flag "{}". The one provided in the --yaml file will be used.'.format(
            yaml_containerapp.get('name'), name))
    name = yaml_containerapp.get('name')

    if not yaml_containerapp.get('type'):
        yaml_containerapp['type'] = 'Microsoft.App/containerApps'
    elif yaml_containerapp.get('type').lower() != "microsoft.app/containerapps":
        raise ValidationError('Containerapp type must be \"Microsoft.App/ContainerApps\"')

    # Deserialize the yaml into a ContainerApp object. Need this since we're not using SDK
    containerapp_def = None
    try:
        deserializer = create_deserializer()

        containerapp_def = deserializer('ContainerApp', yaml_containerapp)
    except DeserializationError as ex:
        raise ValidationError('Invalid YAML provided. Please see https://docs.microsoft.com/azure/container-apps/azure-resource-manager-api-spec#examples for a valid containerapps YAML spec.')

    # Remove tags before converting from snake case to camel case, then re-add tags. We don't want to change the case of the tags. Need this since we're not using SDK
    tags = None
    if yaml_containerapp.get('tags'):
        tags = yaml_containerapp.get('tags')
        del yaml_containerapp['tags']

    containerapp_def = _convert_object_from_snake_to_camel_case(_object_to_dict(containerapp_def))
    containerapp_def['tags'] = tags

    # After deserializing, some properties may need to be moved under the "properties" attribute. Need this since we're not using SDK
    containerapp_def = process_loaded_yaml(containerapp_def)

    # Remove "additionalProperties" and read-only attributes that are introduced in the deserialization. Need this since we're not using SDK
    _remove_additional_attributes(containerapp_def)
    _remove_readonly_attributes(containerapp_def)

    # Validate managed environment
    if not containerapp_def["properties"].get('managedEnvironmentId'):
        raise RequiredArgumentMissingError('managedEnvironmentId is required. Please see https://docs.microsoft.com/azure/container-apps/azure-resource-manager-api-spec#examples for a valid containerapps YAML spec.')

    env_id = containerapp_def["properties"]['managedEnvironmentId']
    env_name = None
    env_rg = None
    env_info = None

    if (is_valid_resource_id(env_id)):
        parsed_managed_env = parse_resource_id(env_id)
        env_name = parsed_managed_env['name']
        env_rg = parsed_managed_env['resource_group']
    else:
        raise ValidationError('Invalid managedEnvironmentId specified. Environment not found')

    try:
        env_info = ManagedEnvironmentClient.show(cmd=cmd, resource_group_name=env_rg, name=env_name)
    except:
        pass

    if not env_info:
        raise ValidationError("The environment '{}' in resource group '{}' was not found".format(env_name, env_rg))

    # Validate location
    if not containerapp_def.get('location'):
        containerapp_def['location'] = env_info['location']

    try:
        r = ContainerAppClient.create_or_update(
            cmd=cmd, resource_group_name=resource_group_name, name=name, container_app_envelope=containerapp_def, no_wait=no_wait)

        if "properties" in r and "provisioningState" in r["properties"] and r["properties"]["provisioningState"].lower() == "waiting" and not no_wait:
            logger.warning('Containerapp creation in progress. Please monitor the creation using `az containerapp show -n {} -g {}`'.format(
                name, resource_group_name
            ))

        return r
    except Exception as e:
        handle_raw_exception(e)


def create_containerapp(cmd,
                        name,
                        resource_group_name,
                        yaml=None,
                        image=None,
                        image_name=None,
                        managed_env=None,
                        min_replicas=None,
                        max_replicas=None,
                        target_port=None,
                        transport="auto",
                        ingress=None,
                        revisions_mode="single",
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
                        revision_suffix=None,
                        startup_command=None,
                        args=None,
                        tags=None,
                        no_wait=False):
    _validate_subscription_registered(cmd, "Microsoft.App")

    if yaml:
        if image or managed_env or min_replicas or max_replicas or target_port or ingress or\
            revisions_mode or secrets or env_vars or cpu or memory or registry_server or\
            registry_user or registry_pass or dapr_enabled or dapr_app_port or dapr_app_id or\
            location or startup_command or args or tags:
            logger.warning('Additional flags were passed along with --yaml. These flags will be ignored, and the configuration defined in the yaml will be used instead')
        return create_containerapp_yaml(cmd=cmd, name=name, resource_group_name=resource_group_name, file_name=yaml, no_wait=no_wait)

    if not image:
        image = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"

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

    location = managed_env_info["location"]
    _ensure_location_allowed(cmd, location, "Microsoft.App", "containerApps")

    external_ingress = None
    if ingress is not None:
        if ingress.lower() == "internal":
            external_ingress = False
        elif ingress.lower() == "external":
            external_ingress = True

    ingress_def = None
    if target_port is not None and ingress is not None:
        ingress_def = IngressModel
        ingress_def["external"] = external_ingress
        ingress_def["targetPort"] = target_port
        ingress_def["transport"] = transport

    secrets_def = None
    if secrets is not None:
        secrets_def = parse_secret_flags(secrets)

    # If ACR image and registry_server is not supplied, infer it
    if image and '.azurecr.io' in image:
        if not registry_server:
            registry_server = image.split('/')[0]

    registries_def = None
    if registry_server is not None:
        registries_def = RegistryCredentialsModel

        # Infer credentials if not supplied and its azurecr
        if not registry_user or not registry_pass:
            registry_user, registry_pass = _infer_acr_credentials(cmd, registry_server)

        registries_def["server"] = registry_server
        registries_def["username"] = registry_user

        if secrets_def is None:
            secrets_def = []
        registries_def["passwordSecretRef"] = store_as_secret_and_return_secret_ref(secrets_def, registry_user, registry_server, registry_pass)

    config_def = ConfigurationModel
    config_def["secrets"] = secrets_def
    config_def["activeRevisionsMode"] = revisions_mode
    config_def["ingress"] = ingress_def
    config_def["registries"] = [registries_def] if registries_def is not None else None

    scale_def = None
    if min_replicas is not None or max_replicas is not None:
        scale_def = ScaleModel
        scale_def["minReplicas"] = min_replicas
        scale_def["maxReplicas"] = max_replicas

    resources_def = None
    if cpu is not None or memory is not None:
        resources_def = ContainerResourcesModel
        resources_def["cpu"] = cpu
        resources_def["memory"] = memory

    container_def = ContainerModel
    container_def["name"] = image_name if image_name else name
    container_def["image"] = image
    if env_vars is not None:
        container_def["env"] = parse_env_var_flags(env_vars)
    if startup_command is not None:
        container_def["command"] = startup_command
    if args is not None:
        container_def["args"] = args
    if resources_def is not None:
        container_def["resources"] = resources_def

    dapr_def = None
    if dapr_enabled:
        dapr_def = DaprModel
        dapr_def["daprEnabled"] = True
        dapr_def["appId"] = dapr_app_id
        dapr_def["appPort"] = dapr_app_port
        dapr_def["appProtocol"] = dapr_app_protocol

    template_def = TemplateModel
    template_def["containers"] = [container_def]
    template_def["scale"] = scale_def
    template_def["dapr"] = dapr_def

    if revision_suffix is not None:
        template_def["revisionSuffix"] = revision_suffix

    containerapp_def = ContainerAppModel
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
                        image=None,
                        image_name=None,
                        min_replicas=None,
                        max_replicas=None,
                        ingress=None,
                        target_port=None,
                        transport=None,
                        traffic_weights=None,
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
        if image or min_replicas or max_replicas or target_port or ingress or\
            revisions_mode or secrets or env_vars or cpu or memory or registry_server or\
            registry_user or registry_pass or dapr_enabled or dapr_app_port or dapr_app_id or\
            startup_command or args or tags:
            logger.warning('Additional flags were passed along with --yaml. These flags will be ignored, and the configuration defined in the yaml will be used instead')
        return update_containerapp_yaml(cmd=cmd, name=name, resource_group_name=resource_group_name, file_name=yaml, no_wait=no_wait)

    containerapp_def = None
    try:
        containerapp_def = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if not containerapp_def:
        raise CLIError("The containerapp '{}' does not exist".format(name))

    # If ACR image and registry_server is not supplied, infer it
    if image and '.azurecr.io' in image:
        if not registry_server:
            registry_server = image.split('/')[0]

    update_map = {}
    update_map['secrets'] = secrets is not None
    update_map['ingress'] = ingress or target_port or transport or traffic_weights
    update_map['registries'] = registry_server or registry_user or registry_pass
    update_map['scale'] = min_replicas or max_replicas
    update_map['container'] = image or image_name or env_vars is not None or cpu or memory or startup_command is not None or args is not None
    update_map['dapr'] = dapr_enabled or dapr_app_port or dapr_app_id or dapr_app_protocol
    update_map['configuration'] = update_map['secrets'] or update_map['ingress'] or update_map['registries'] or revisions_mode is not None

    if tags:
        _add_or_update_tags(containerapp_def, tags)

    if revision_suffix is not None:
        containerapp_def["properties"]["template"]["revisionSuffix"] = revision_suffix

    # Containers
    if update_map["container"]:
        if not image_name:
            if len(containerapp_def["properties"]["template"]["containers"]) == 1:
                image_name = containerapp_def["properties"]["template"]["containers"][0]["name"]
            else:
                raise ValidationError("Usage error: --image-name is required when adding or updating a container")

        # Check if updating existing container
        updating_existing_container = False
        for c in containerapp_def["properties"]["template"]["containers"]:
            if c["name"].lower() == image_name.lower():
                updating_existing_container = True

                if image is not None:
                    c["image"] = image
                if env_vars is not None:
                    if isinstance(env_vars, list) and not env_vars:
                        c["env"] = []
                    else:
                        if "env" not in c or not c["env"]:
                            c["env"] = []
                        _add_or_update_env_vars(c["env"], parse_env_var_flags(env_vars))
                if startup_command is not None:
                    if isinstance(startup_command, list) and not startup_command:
                        c["command"] = None
                    else:
                        c["command"] = startup_command
                if args is not None:
                    if isinstance(args, list) and not args:
                        c["args"] = None
                    else:
                        c["args"] = args
                if cpu is not None or memory is not None:
                    if "resources" in c and c["resources"]:
                        if cpu is not None:
                            c["resources"]["cpu"] = cpu
                        if memory is not None:
                            c["resources"]["memory"] = memory
                    else:
                        c["resources"] = {
                            "cpu": cpu,
                            "memory": memory
                        }

        # If not updating existing container, add as new container
        if not updating_existing_container:
            if image is None:
                raise ValidationError("Usage error: --image is required when adding a new container")

            resources_def = None
            if cpu is not None or memory is not None:
                resources_def = ContainerResourcesModel
                resources_def["cpu"] = cpu
                resources_def["memory"] = memory

            container_def = ContainerModel
            container_def["name"] = image_name
            container_def["image"] = image
            if env_vars is not None:
                container_def["env"] = parse_env_var_flags(env_vars)
            if startup_command is not None:
                if isinstance(startup_command, list) and not startup_command:
                    container_def["command"] = None
                else:
                    container_def["command"] = startup_command
            if args is not None:
                if isinstance(args, list) and not args:
                    container_def["args"] = None
                else:
                    container_def["args"] = args
            if resources_def is not None:
                container_def["resources"] = resources_def

            containerapp_def["properties"]["template"]["containers"].append(container_def)

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
        if "ingress" not in containerapp_def["properties"]["configuration"]:
            containerapp_def["properties"]["configuration"]["ingress"] = {}

        external_ingress = None
        if ingress is not None:
            if ingress.lower() == "internal":
                external_ingress = False
            elif ingress.lower() == "external":
                external_ingress = True

        if external_ingress is not None:
            containerapp_def["properties"]["configuration"]["ingress"]["external"] = external_ingress

        if target_port is not None:
            containerapp_def["properties"]["configuration"]["ingress"]["targetPort"] = target_port

        if transport is not None:
            containerapp_def["properties"]["configuration"]["ingress"]["transport"] = transport

        if traffic_weights is not None:
            _update_traffic_Weights(containerapp_def, traffic_weights)

    _get_existing_secrets(cmd, resource_group_name, name, containerapp_def)

    if secrets is not None:
        _add_or_update_secrets(containerapp_def, parse_secret_flags(secrets))

    if update_map["registries"]:
        registries_def = None
        registry = None

        if "registries" not in containerapp_def["properties"]["configuration"]:
            containerapp_def["properties"]["configuration"]["registries"] = []

        registries_def = containerapp_def["properties"]["configuration"]["registries"]

        if not registry_server:
            raise ValidationError("Usage error: --registry-server is required when adding or updating a registry")

        # Infer credentials if not supplied and its azurecr
        if not registry_user or not registry_pass:
            registry_user, registry_pass = _infer_acr_credentials(cmd, registry_server)

        # Check if updating existing registry
        updating_existing_registry = False
        for r in registries_def:
            if r['server'].lower() == registry_server.lower():
                updating_existing_registry = True

                if registry_user:
                    r["username"] = registry_user
                if registry_pass:
                    r["passwordSecretRef"] = store_as_secret_and_return_secret_ref(
                        containerapp_def["properties"]["configuration"]["secrets"],
                        r["username"],
                        r["server"],
                        registry_pass,
                        update_existing_secret=True)

        # If not updating existing registry, add as new registry
        if not updating_existing_registry:
            if not(registry_server is not None and registry_user is not None and registry_pass is not None):
                raise ValidationError("Usage error: --registry-server, --registry-password and --registry-username are required when adding a registry")

            registry = RegistryCredentialsModel
            registry["server"] = registry_server
            registry["username"] = registry_user
            registry["passwordSecretRef"] = store_as_secret_and_return_secret_ref(
                containerapp_def["properties"]["configuration"]["secrets"],
                registry_user,
                registry_server,
                registry_pass,
                update_existing_secret=True)

            registries_def.append(registry)
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

    if "scale" not in containerapp_def["properties"]["template"]:
        containerapp_def["properties"]["template"]["scale"] = {}

    if min_replicas is not None:
        containerapp_def["properties"]["template"]["scale"]["minReplicas"] = min_replicas

    if max_replicas is not None:
        containerapp_def["properties"]["template"]["scale"]["maxReplicas"] = max_replicas

    _get_existing_secrets(cmd, resource_group_name, name, containerapp_def)

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
        return ContainerAppClient.delete(cmd=cmd, name=name, resource_group_name=resource_group_name, no_wait=no_wait)
    except CLIError as e:
        handle_raw_exception(e)


def create_managed_environment(cmd,
                              name,
                              resource_group_name,
                              logs_customer_id=None,
                              logs_key=None,
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
    _ensure_location_allowed(cmd, location, "Microsoft.App", "managedEnvironments")

    # Microsoft.ContainerService RP registration is required for vnet enabled environments
    if infrastructure_subnet_resource_id is not None or app_subnet_resource_id is not None:
        if (is_valid_resource_id(app_subnet_resource_id)):
            parsed_app_subnet_resource_id = parse_resource_id(app_subnet_resource_id)
            subnet_subscription = parsed_app_subnet_resource_id["subscription"]
            _validate_subscription_registered(cmd, "Microsoft.ContainerService", subnet_subscription)
        else:
            raise ValidationError('Subnet resource ID is invalid.')

    if logs_customer_id is None or logs_key is None:
        logs_customer_id, logs_key = _generate_log_analytics_if_not_provided(cmd, logs_customer_id, logs_key, location, resource_group_name)

    log_analytics_config_def = LogAnalyticsConfigurationModel
    log_analytics_config_def["customerId"] = logs_customer_id
    log_analytics_config_def["sharedKey"] = logs_key

    app_logs_config_def = AppLogsConfigurationModel
    app_logs_config_def["destination"] = "log-analytics"
    app_logs_config_def["logAnalyticsConfiguration"] = log_analytics_config_def

    managed_env_def = ManagedEnvironmentModel
    managed_env_def["location"] = location
    managed_env_def["properties"]["internalLoadBalancerEnabled"] = False
    managed_env_def["properties"]["appLogsConfiguration"] = app_logs_config_def
    managed_env_def["tags"] = tags

    if instrumentation_key is not None:
        managed_env_def["properties"]["daprAIInstrumentationKey"] = instrumentation_key

    if infrastructure_subnet_resource_id or app_subnet_resource_id or docker_bridge_cidr or platform_reserved_cidr or platform_reserved_dns_ip:
        vnet_config_def = VnetConfigurationModel

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

    managed_env_def = ManagedEnvironmentModel
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
        return ManagedEnvironmentClient.delete(cmd=cmd, name=name, resource_group_name=resource_group_name, no_wait=no_wait)
    except CLIError as e:
        handle_raw_exception(e)


def create_or_update_github_action(cmd,
                                   name,
                                   resource_group_name,
                                   repo_url,
                                   registry_url=None,
                                   registry_username=None,
                                   registry_password=None,
                                   branch=None,
                                   token=None,
                                   login_with_github=False,
                                   docker_file_path=None,
                                   service_principal_client_id=None,
                                   service_principal_client_secret=None,
                                   service_principal_tenant_id=None):
    if not token and not login_with_github:
        raise_missing_token_suggestion()
    elif not token:
        scopes = ["admin:repo_hook", "repo", "workflow"]
        token = get_github_access_token(cmd, scopes)
    elif token and login_with_github:
        logger.warning("Both token and --login-with-github flag are provided. Will use provided token")

    try:
        # Verify github repo
        from github import Github, GithubException
        from github.GithubException import BadCredentialsException, UnknownObjectException

        repo = None
        repo = repo_url.split('/')
        if len(repo) >= 2:
            repo = '/'.join(repo[-2:])
        
        if repo:
            g = Github(token)
            github_repo = None
            try:
                github_repo = g.get_repo(repo)
                if not github_repo.permissions.push or not github_repo.permissions.maintain:
                    raise CLIError("The token does not have appropriate access rights to repository {}.".format(repo))
                try:
                    github_repo.get_branch(branch=branch)
                except GithubException as e:
                    error_msg = "Encountered GitHub error when accessing {} branch in {} repo.".format(branch, repo)
                    if e.data and e.data['message']:
                        error_msg += " Error: {}".format(e.data['message'])
                    raise CLIError(error_msg)
                logger.warning('Verified GitHub repo and branch')
            except BadCredentialsException:
                raise CLIError("Could not authenticate to the repository. Please create a Personal Access Token and use "
                            "the --token argument. Run 'az webapp deployment github-actions add --help' "
                            "for more information.")
            except GithubException as e:
                error_msg = "Encountered GitHub error when accessing {} repo".format(repo)
                if e.data and e.data['message']:
                    error_msg += " Error: {}".format(e.data['message'])
                raise CLIError(error_msg)
    except CLIError as clierror:
        raise clierror
    except Exception as ex:
        # If exception due to github package missing, etc just continue without validating the repo and rely on api validation
        pass

    source_control_info = None

    try:
        #source_control_info = client.get_source_control_info(resource_group_name, name).properties
        source_control_info = GitHubActionClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)

    except Exception as ex:
        if not service_principal_client_id or not service_principal_client_secret or not service_principal_tenant_id:
            raise RequiredArgumentMissingError('Service principal client ID, secret and tenant ID are required to add github actions for the first time. Please create one using the command \"az ad sp create-for-rbac --name \{name\} --role contributor --scopes /subscriptions/\{subscription\}/resourceGroups/\{resourceGroup\} --sdk-auth\"')
        source_control_info = SourceControlModel

    source_control_info["properties"]["repoUrl"] = repo_url

    if branch:
        source_control_info["properties"]["branch"] = branch
    if not source_control_info["properties"]["branch"]:
        source_control_info["properties"]["branch"] = "main"

    azure_credentials = None

    if service_principal_client_id or service_principal_client_secret or service_principal_tenant_id:
        azure_credentials = AzureCredentialsModel
        azure_credentials["clientId"] = service_principal_client_id
        azure_credentials["clientSecret"] = service_principal_client_secret
        azure_credentials["tenantId"] = service_principal_tenant_id
        azure_credentials["subscriptionId"] = get_subscription_id(cmd.cli_ctx)

    # Registry
    if not registry_username or not registry_password:
        # If registry is Azure Container Registry, we can try inferring credentials
        if not registry_url or '.azurecr.io' not in registry_url:
            raise RequiredArgumentMissingError('Registry url is required if using Azure Container Registry, otherwise Registry username and password are required if using Dockerhub')
        logger.warning('No credential was provided to access Azure Container Registry. Trying to look up...')
        parsed = urlparse(registry_url)
        registry_name = (parsed.netloc if parsed.scheme else parsed.path).split('.')[0]

        try:
            registry_username, registry_password = _get_acr_cred(cmd.cli_ctx, registry_name)
        except Exception as ex:
            raise RequiredArgumentMissingError('Failed to retrieve credentials for container registry. Please provide the registry username and password')

    registry_info = RegistryInfoModel
    registry_info["registryUrl"] = registry_url
    registry_info["registryUserName"] = registry_username
    registry_info["registryPassword"] = registry_password

    github_action_configuration = GitHubActionConfiguration
    github_action_configuration["registryInfo"] = registry_info
    github_action_configuration["azureCredentials"] = azure_credentials
    github_action_configuration["dockerfilePath"] = docker_file_path

    source_control_info["properties"]["githubActionConfiguration"] = github_action_configuration

    headers = ["x-ms-github-auxiliary={}".format(token)]

    try: 
        r = GitHubActionClient.create_or_update(cmd = cmd, resource_group_name=resource_group_name, name=name, github_action_envelope=source_control_info, headers = headers)
        return r
    except Exception as e:
        handle_raw_exception(e)
    
        
def show_github_action(cmd, name, resource_group_name):
    try:
        return GitHubActionClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except Exception as e:
        handle_raw_exception(e)


def delete_github_action(cmd, name, resource_group_name, token=None, login_with_github=False):
    # Check if there is an existing source control to delete
    try: 
        github_action_config = GitHubActionClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except Exception as e:
        handle_raw_exception(e)

    repo_url = github_action_config["properties"]["repoUrl"]

    if not token and not login_with_github:
        raise_missing_token_suggestion()
    elif not token:
        scopes = ["admin:repo_hook", "repo", "workflow"]
        token = get_github_access_token(cmd, scopes)
    elif token and login_with_github:
        logger.warning("Both token and --login-with-github flag are provided. Will use provided token")

    # Check if PAT can access repo
    try:
        # Verify github repo
        from github import Github, GithubException
        from github.GithubException import BadCredentialsException, UnknownObjectException

        repo = None
        repo = repo_url.split('/')
        if len(repo) >= 2:
            repo = '/'.join(repo[-2:])
        
        if repo:
            g = Github(token)
            github_repo = None
            try:
                github_repo = g.get_repo(repo)
                if not github_repo.permissions.push or not github_repo.permissions.maintain:
                    raise CLIError("The token does not have appropriate access rights to repository {}.".format(repo))
            except BadCredentialsException:
                raise CLIError("Could not authenticate to the repository. Please create a Personal Access Token and use "
                            "the --token argument. Run 'az webapp deployment github-actions add --help' "
                            "for more information.")
            except GithubException as e:
                error_msg = "Encountered GitHub error when accessing {} repo".format(repo)
                if e.data and e.data['message']:
                    error_msg += " Error: {}".format(e.data['message'])
                raise CLIError(error_msg)
    except CLIError as clierror:
        raise clierror
    except Exception as ex:
        # If exception due to github package missing, etc just continue without validating the repo and rely on api validation
        pass
        
    headers = ["x-ms-github-auxiliary={}".format(token)]

    try:
        return GitHubActionClient.delete(cmd=cmd, resource_group_name=resource_group_name, name=name, headers=headers)
    except Exception as e:
        handle_raw_exception(e)


def list_revisions(cmd, name, resource_group_name):
    try:
        return ContainerAppClient.list_revisions(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except CLIError as e:
        handle_raw_exception(e)


def show_revision(cmd, resource_group_name, revision_name, name=None):
    if not name:
        name = _get_app_from_revision(revision_name)

    try:
        return ContainerAppClient.show_revision(cmd=cmd, resource_group_name=resource_group_name, container_app_name=name, name=revision_name)
    except CLIError as e:
        handle_raw_exception(e)


def restart_revision(cmd, resource_group_name, revision_name, name=None):
    if not name:
        name = _get_app_from_revision(revision_name)

    try:
        return ContainerAppClient.restart_revision(cmd=cmd, resource_group_name=resource_group_name, container_app_name=name, name=revision_name)
    except CLIError as e:
        handle_raw_exception(e)


def activate_revision(cmd, resource_group_name, revision_name, name=None):
    if not name:
        name = _get_app_from_revision(revision_name)

    try:
        return ContainerAppClient.activate_revision(cmd=cmd, resource_group_name=resource_group_name, container_app_name=name, name=revision_name)
    except CLIError as e:
        handle_raw_exception(e)

def deactivate_revision(cmd, resource_group_name, revision_name, name=None):
    if not name:
        name = _get_app_from_revision(revision_name)

    try:
        return ContainerAppClient.deactivate_revision(cmd=cmd, resource_group_name=resource_group_name, container_app_name=name, name=revision_name)
    except CLIError as e:
        handle_raw_exception(e)

def copy_revision(cmd,
                        name,
                        resource_group_name,
                        from_revision=None,
                        #label=None,
                        yaml=None,
                        image=None,
                        image_name=None,
                        min_replicas=None,
                        max_replicas=None,
                        env_vars=None,
                        cpu=None,
                        memory=None,
                        revision_suffix=None,
                        startup_command=None,
                        traffic_weights=None,
                        args=None,
                        tags=None,
                        no_wait=False):
    _validate_subscription_registered(cmd, "Microsoft.App")

    if not from_revision:
        from_revision = containerapp_def["properties"]["latestRevisionName"]

    if yaml:
        if image or min_replicas or max_replicas or\
            env_vars or cpu or memory or \
            startup_command or args or tags:
            logger.warning('Additional flags were passed along with --yaml. These flags will be ignored, and the configuration defined in the yaml will be used instead')
        return update_containerapp_yaml(cmd=cmd, name=name, resource_group_name=resource_group_name, file_name=yaml, from_revision=from_revision, no_wait=no_wait)

    containerapp_def = None
    try:
        containerapp_def = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if not containerapp_def:
        raise CLIError("The containerapp '{}' does not exist".format(name))

    try:
        r = ContainerAppClient.show_revision(cmd=cmd, resource_group_name=resource_group_name, container_app_name=name, name=from_revision)
    except CLIError as e:
        # Error handle the case where revision not found?
        handle_raw_exception(e)

    containerapp_def["properties"]["template"] = r["properties"]["template"]

    update_map = {}
    update_map['ingress'] = traffic_weights
    update_map['scale'] = min_replicas or max_replicas
    update_map['container'] = image or image_name or env_vars or cpu or memory or startup_command is not None or args is not None
    update_map['configuration'] =  update_map['ingress']

    if tags:
        _add_or_update_tags(containerapp_def, tags)

    if revision_suffix is not None:
        containerapp_def["properties"]["template"]["revisionSuffix"] = revision_suffix

    # Containers
    if update_map["container"]:
        if not image_name:
            if len(containerapp_def["properties"]["template"]["containers"]) == 1:
                image_name = containerapp_def["properties"]["template"]["containers"][0]["name"]
            else:
                raise ValidationError("Usage error: --image-name is required when adding or updating a container")

        # Check if updating existing container
        updating_existing_container = False
        for c in containerapp_def["properties"]["template"]["containers"]:
            if c["name"].lower() == image_name.lower():
                updating_existing_container = True

                if image is not None:
                    c["image"] = image
                if env_vars is not None:
                    if "env" not in c or not c["env"]:
                        c["env"] = []
                    _add_or_update_env_vars(c["env"], parse_env_var_flags(env_vars))
                if startup_command is not None:
                    if isinstance(startup_command, list) and not startup_command:
                        c["command"] = None
                    else:
                        c["command"] = startup_command
                if args is not None:
                    if isinstance(args, list) and not args:
                        c["args"] = None
                    else:
                        c["args"] = args
                if cpu is not None or memory is not None:
                    if "resources" in c and c["resources"]:
                        if cpu is not None:
                            c["resources"]["cpu"] = cpu
                        if memory is not None:
                            c["resources"]["memory"] = memory
                    else:
                        c["resources"] = {
                            "cpu": cpu,
                            "memory": memory
                        }

        # If not updating existing container, add as new container
        if not updating_existing_container:
            if image is None:
                raise ValidationError("Usage error: --image is required when adding a new container")

            resources_def = None
            if cpu is not None or memory is not None:
                resources_def = ContainerResourcesModel
                resources_def["cpu"] = cpu
                resources_def["memory"] = memory

            container_def = ContainerModel
            container_def["name"] = image_name
            container_def["image"] = image
            if env_vars is not None:
                container_def["env"] = parse_env_var_flags(env_vars)
            if startup_command is not None:
                if isinstance(startup_command, list) and not startup_command:
                    container_def["command"] = None
                else:
                    container_def["command"] = startup_command
            if args is not None:
                if isinstance(args, list) and not args:
                    container_def["args"] = None
                else:
                    container_def["args"] = args
            if resources_def is not None:
                container_def["resources"] = resources_def

            containerapp_def["properties"]["template"]["containers"].append(container_def)

    # Scale
    if update_map["scale"]:
        if "scale" not in containerapp_def["properties"]["template"]:
            containerapp_def["properties"]["template"]["scale"] = {}
        if min_replicas is not None:
            containerapp_def["properties"]["template"]["scale"]["minReplicas"] = min_replicas
        if max_replicas is not None:
            containerapp_def["properties"]["template"]["scale"]["maxReplicas"] = max_replicas

    # Configuration
    if update_map["ingress"]:
        if "ingress" not in containerapp_def["properties"]["configuration"]:
            containerapp_def["properties"]["configuration"]["ingress"] = {}

        if traffic_weights is not None:
            _update_traffic_Weights(containerapp_def, traffic_weights)

    _get_existing_secrets(cmd, resource_group_name, name, containerapp_def)

    try:
        r = ContainerAppClient.create_or_update(
            cmd=cmd, resource_group_name=resource_group_name, name=name, container_app_envelope=containerapp_def, no_wait=no_wait)

        if "properties" in r and "provisioningState" in r["properties"] and r["properties"]["provisioningState"].lower() == "waiting" and not no_wait:
            logger.warning('Containerapp update in progress. Please monitor the update using `az containerapp show -n {} -g {}`'.format(name, resource_group_name))

        return r
    except Exception as e:
        handle_raw_exception(e)

def set_revision_mode(cmd, resource_group_name, name, mode, no_wait=False):
    _validate_subscription_registered(cmd, "Microsoft.App")

    containerapp_def = None
    try:
        containerapp_def = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if not containerapp_def:
        raise CLIError("The containerapp '{}' does not exist".format(name))

    containerapp_def["properties"]["configuration"]["activeRevisionsMode"] = mode.lower()

    _get_existing_secrets(cmd, resource_group_name, name, containerapp_def)

    try:
        r = ContainerAppClient.create_or_update(
            cmd=cmd, resource_group_name=resource_group_name, name=name, container_app_envelope=containerapp_def, no_wait=no_wait)
        return r["properties"]["configuration"]["activeRevisionsMode"]
    except Exception as e: 
        handle_raw_exception(e)

def show_ingress(cmd, name, resource_group_name):
    _validate_subscription_registered(cmd, "Microsoft.App")

    containerapp_def = None
    try:
        containerapp_def = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if not containerapp_def:
        raise CLIError("The containerapp '{}' does not exist".format(name))

    try:
        return containerapp_def["properties"]["configuration"]["ingress"]
    except:
        raise CLIError("The containerapp '{}' does not have ingress enabled.".format(name))

def enable_ingress(cmd, name, resource_group_name, type, target_port, transport, allow_insecure=False, no_wait=False):
    _validate_subscription_registered(cmd, "Microsoft.App")

    containerapp_def = None
    try:
        containerapp_def = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if not containerapp_def:
        raise CLIError("The containerapp '{}' does not exist".format(name))

    external_ingress = None
    if type is not None:
        if type.lower() == "internal":
            external_ingress = False
        elif type.lower() == "external":
            external_ingress = True

    ingress_def = None
    if target_port is not None and type is not None:
        ingress_def = IngressModel
        ingress_def["external"] = external_ingress
        ingress_def["targetPort"] = target_port
        ingress_def["transport"] = transport
        ingress_def["allowInsecure"] = allow_insecure
 
    containerapp_def["properties"]["configuration"]["ingress"] = ingress_def

    _get_existing_secrets(cmd, resource_group_name, name, containerapp_def)

    try:
        r = ContainerAppClient.create_or_update(
            cmd=cmd, resource_group_name=resource_group_name, name=name, container_app_envelope=containerapp_def, no_wait=no_wait)
        return r["properties"]["configuration"]["ingress"]
    except Exception as e: 
        handle_raw_exception(e)

def disable_ingress(cmd, name, resource_group_name, no_wait=False):
    _validate_subscription_registered(cmd, "Microsoft.App")

    containerapp_def = None
    try:
        containerapp_def = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if not containerapp_def:
        raise CLIError("The containerapp '{}' does not exist".format(name))

    containerapp_def["properties"]["configuration"]["ingress"] = None

    _get_existing_secrets(cmd, resource_group_name, name, containerapp_def)

    try:
        r = ContainerAppClient.create_or_update(
            cmd=cmd, resource_group_name=resource_group_name, name=name, container_app_envelope=containerapp_def, no_wait=no_wait)
        logger.warning("Ingress has been disabled successfully.")
        return 
    except Exception as e: 
        handle_raw_exception(e)

def set_ingress_traffic(cmd, name, resource_group_name, traffic_weights, no_wait=False):
    _validate_subscription_registered(cmd, "Microsoft.App")

    containerapp_def = None
    try:
        containerapp_def = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if not containerapp_def:
        raise CLIError("The containerapp '{}' does not exist".format(name))

    try:
        containerapp_def["properties"]["configuration"]["ingress"]
    except: 
        raise CLIError("Ingress must be enabled to set ingress traffic. Try running `az containerapp ingress -h` for more info.")

    if traffic_weights is not None:
         _update_traffic_Weights(containerapp_def, traffic_weights)

    _get_existing_secrets(cmd, resource_group_name, name, containerapp_def)

    try:
        r = ContainerAppClient.create_or_update(
            cmd=cmd, resource_group_name=resource_group_name, name=name, container_app_envelope=containerapp_def, no_wait=no_wait)
        return r["properties"]["configuration"]["ingress"]["traffic"]
    except Exception as e: 
        handle_raw_exception(e)

def show_ingress_traffic(cmd, name, resource_group_name):
    _validate_subscription_registered(cmd, "Microsoft.App")

    containerapp_def = None
    try:
        containerapp_def = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if not containerapp_def:
        raise CLIError("The containerapp '{}' does not exist".format(name))

    try:
        return containerapp_def["properties"]["configuration"]["ingress"]["traffic"]
    except: 
        raise CLIError("Ingress must be enabled to show ingress traffic. Try running `az containerapp ingress -h` for more info.")

def show_registry(cmd, name, resource_group_name, server):
    _validate_subscription_registered(cmd, "Microsoft.App")

    containerapp_def = None
    try:
        containerapp_def = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if not containerapp_def:
        raise CLIError("The containerapp '{}' does not exist".format(name))

    try:
        containerapp_def["properties"]["configuration"]["registries"]
    except: 
        raise CLIError("The containerapp {} has no assigned registries.".format(name))

    registries_def = containerapp_def["properties"]["configuration"]["registries"]

    for r in registries_def:
        if r['server'].lower() == server.lower():
            return r
    raise CLIError("The containerapp {} does not have specified registry assigned.".format(name))

def list_registry(cmd, name, resource_group_name):
    _validate_subscription_registered(cmd, "Microsoft.App")

    containerapp_def = None
    try:
        containerapp_def = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if not containerapp_def:
        raise CLIError("The containerapp '{}' does not exist".format(name))

    try:
        return containerapp_def["properties"]["configuration"]["registries"]
    except: 
        raise CLIError("The containerapp {} has no assigned registries.".format(name))

def set_registry(cmd, name, resource_group_name, server, username=None, password=None, no_wait=False):
    _validate_subscription_registered(cmd, "Microsoft.App")

    containerapp_def = None
    try:
        containerapp_def = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if not containerapp_def:
        raise CLIError("The containerapp '{}' does not exist".format(name))

    _get_existing_secrets(cmd, resource_group_name, name, containerapp_def)

    registries_def = None
    registry = None

    if "registries" not in containerapp_def["properties"]["configuration"]:
        containerapp_def["properties"]["configuration"]["registries"] = []

    registries_def = containerapp_def["properties"]["configuration"]["registries"]

    if not username or not password:
        # If registry is Azure Container Registry, we can try inferring credentials
        if '.azurecr.io' not in server:
            raise RequiredArgumentMissingError('Registry username and password are required if you are not using Azure Container Registry.')
        logger.warning('No credential was provided to access Azure Container Registry. Trying to look up...')
        parsed = urlparse(server)
        registry_name = (parsed.netloc if parsed.scheme else parsed.path).split('.')[0]

        try:
            username, password = _get_acr_cred(cmd.cli_ctx, registry_name)
        except Exception as ex:
            raise RequiredArgumentMissingError('Failed to retrieve credentials for container registry. Please provide the registry username and password')

    # Check if updating existing registry
    updating_existing_registry = False
    for r in registries_def:
        if r['server'].lower() == server.lower():
            logger.warning("Updating existing registry.")
            updating_existing_registry = True
            if username:
                r["username"] = username
            if password:
                r["passwordSecretRef"] = store_as_secret_and_return_secret_ref(
                    containerapp_def["properties"]["configuration"]["secrets"],
                    r["username"],
                    r["server"],
                    password,
                    update_existing_secret=True)

    # If not updating existing registry, add as new registry
    if not updating_existing_registry:
        registry = RegistryCredentialsModel
        registry["server"] = server
        registry["username"] = username
        registry["passwordSecretRef"] = store_as_secret_and_return_secret_ref(
            containerapp_def["properties"]["configuration"]["secrets"],
            username,
            server,
            password,
            update_existing_secret=True)
            # Should this be false? ^

        registries_def.append(registry)
   
    try:
        r = ContainerAppClient.create_or_update(
            cmd=cmd, resource_group_name=resource_group_name, name=name, container_app_envelope=containerapp_def, no_wait=no_wait)

        return r["properties"]["configuration"]["registries"]
    except Exception as e:
        handle_raw_exception(e)

def delete_registry(cmd, name, resource_group_name, server, no_wait=False):
    _validate_subscription_registered(cmd, "Microsoft.App")

    containerapp_def = None
    try:
        containerapp_def = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if not containerapp_def:
        raise CLIError("The containerapp '{}' does not exist".format(name))

    _get_existing_secrets(cmd, resource_group_name, name, containerapp_def)

    registries_def = None
    registry = None

    try:
        containerapp_def["properties"]["configuration"]["registries"]
    except: 
        raise CLIError("The containerapp {} has no assigned registries.".format(name))

    registries_def = containerapp_def["properties"]["configuration"]["registries"]

    wasRemoved = False
    for i in range(0, len(registries_def)):
        r = registries_def[i]
        if r['server'].lower() == server.lower():
            registries_def.pop(i)
            _remove_registry_secret(containerapp_def=containerapp_def, server=server, username=r["username"])
            wasRemoved = True
            break

    if not wasRemoved:
        raise CLIError("Containerapp does not have registry server {} assigned.".format(server))

    if len(containerapp_def["properties"]["configuration"]["registries"]) == 0:
        containerapp_def["properties"]["configuration"].pop("registries")

    try:
        r = ContainerAppClient.create_or_update(
            cmd=cmd, resource_group_name=resource_group_name, name=name, container_app_envelope=containerapp_def, no_wait=no_wait)
        logger.warning("Registry successfully removed.")
        return r["properties"]["configuration"]["registries"]
    # No registries to return, so return nothing
    except Exception as e:
        return

def list_secrets(cmd, name, resource_group_name):
    _validate_subscription_registered(cmd, "Microsoft.App")

    containerapp_def = None
    try:
        containerapp_def = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if not containerapp_def:
        raise CLIError("The containerapp '{}' does not exist".format(name))

    try:
        return ContainerAppClient.list_secrets(cmd=cmd, resource_group_name=resource_group_name, name=name)["value"]
    except: 
        raise CLIError("The containerapp {} has no assigned secrets.".format(name))

def show_secret(cmd, name, resource_group_name, secret_name):
    _validate_subscription_registered(cmd, "Microsoft.App")

    containerapp_def = None
    try:
        containerapp_def = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if not containerapp_def:
        raise CLIError("The containerapp '{}' does not exist".format(name))

    r = ContainerAppClient.list_secrets(cmd=cmd, resource_group_name=resource_group_name, name=name)
    for secret in r["value"]:
        if secret["name"].lower() == secret_name.lower():
            return secret
    raise CLIError("The containerapp {} does not have a secret assigned with name {}.".format(name, secret_name))

def delete_secrets(cmd, name, resource_group_name, secret_names, no_wait = False):
    _validate_subscription_registered(cmd, "Microsoft.App")

    containerapp_def = None
    try:
        containerapp_def = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if not containerapp_def:
        raise CLIError("The containerapp '{}' does not exist".format(name))

    _get_existing_secrets(cmd, resource_group_name, name, containerapp_def)

    for secret_name in secret_names:
        wasRemoved = False
        for secret in containerapp_def["properties"]["configuration"]["secrets"]:
            if secret["name"].lower() == secret_name.lower():
                _remove_secret(containerapp_def, secret_name=secret["name"])
                wasRemoved = True
                break
        if not wasRemoved:
            raise CLIError("The containerapp {} does not have a secret assigned with name {}.".format(name, secret_name))
    try:
        r = ContainerAppClient.create_or_update(
            cmd=cmd, resource_group_name=resource_group_name, name=name, container_app_envelope=containerapp_def, no_wait=no_wait)
        logger.warning("Secret(s) successfully removed.")
        try:
            return r["properties"]["configuration"]["secrets"]
        # No secrets to return
        except:
            pass
    except Exception as e:
        handle_raw_exception(e)

def set_secrets(cmd, name, resource_group_name, secrets, 
                #secrets=None,
                #yaml=None, 
                no_wait = False):
    _validate_subscription_registered(cmd, "Microsoft.App")

    # if not yaml and not secrets:
    #     raise RequiredArgumentMissingError('Usage error: --secrets is required if not using --yaml')

    # if not secrets:
    #     secrets = []
    
    # if yaml:
    #     yaml_secrets = load_yaml_file(yaml).split(' ')
    #     try:
    #         parse_secret_flags(yaml_secrets)
    #     except:
    #         raise CLIError("YAML secrets must be a list of secrets in key=value format, delimited by new line.")
    #     for secret in yaml_secrets:
    #         secrets.append(secret.strip())

    containerapp_def = None
    try:
        containerapp_def = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if not containerapp_def:
        raise CLIError("The containerapp '{}' does not exist".format(name))

    _get_existing_secrets(cmd, resource_group_name, name, containerapp_def)
    _add_or_update_secrets(containerapp_def, parse_secret_flags(secrets))

    try:
        r = ContainerAppClient.create_or_update(
            cmd=cmd, resource_group_name=resource_group_name, name=name, container_app_envelope=containerapp_def, no_wait=no_wait)
        return r["properties"]["configuration"]["secrets"]
    except Exception as e:
        handle_raw_exception(e)


