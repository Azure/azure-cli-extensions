from typing import Dict, Any
from knack.log import get_logger

from azure.cli.core.commands import AzCliCommand
from azure.cli.core.azclierror import ValidationError, RequiredArgumentMissingError
from msrestazure.tools import parse_resource_id

from ._clients import ContainerAppClient, ManagedEnvironmentClient, ConnectedEnvironmentClient
from ._utils import (_get_azext_module, GA_CONTAINERAPP_EXTENSION_NAME)

logger = get_logger(__name__)


class BaseContainerAppDecorator:
    def __init__(
        self, cmd: AzCliCommand, client: ContainerAppClient, raw_parameters: Dict, models: str
    ):
        self.raw_param = raw_parameters
        self.cmd = cmd
        self.client = client
        self.models = models

    def register_provider(self):
        raise NotImplementedError()

    def validate_arguments(self):
        raise NotImplementedError()

    def construct_containerapp(self):
        raise NotImplementedError()

    def create_containerapp(self, containerapp_def):
        raise NotImplementedError()

    def construct_containerapp_for_post_process(self, containerapp_def, r):
        raise NotImplementedError()

    def post_process_containerapp(self, containerapp_def, r):
        raise NotImplementedError()

    def get_param(self, key) -> Any:
        return self.raw_param.get(key)

    def set_param(self, key, value):
        self.raw_param[key] = value


class ContainerAppPreviewCreateDecorator(BaseContainerAppDecorator):
    def __init__(
        self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models:str
    ):
        super().__init__(cmd, client, raw_parameters, models)
        azext_default_utils = _get_azext_module(
            GA_CONTAINERAPP_EXTENSION_NAME, "azext_containerapp._utils")
        self.azext_default_utils = azext_default_utils

        azext_default_decorator = _get_azext_module(
            GA_CONTAINERAPP_EXTENSION_NAME, "azext_containerapp.containerapp_decorator")
        ga_containerapp_create_decorator = azext_default_decorator.ContainerAppCreateDecorator(
            cmd=cmd,
            client=ContainerAppClient,
            raw_parameters=raw_parameters,
            models=models
        )
        self.ga_containerapp_create_decorator = ga_containerapp_create_decorator
        self.ga_containerapp_create_decorator.environment_client = self.get_environment_client()

    def register_provider(self):
        self.ga_containerapp_create_decorator.register_provider()

    def validate_arguments(self):
        self.ga_containerapp_create_decorator.validate_arguments()

    def construct_containerapp(self):
        containerapp_def = self.ga_containerapp_create_decorator.construct_containerapp()
        containerapp_def = self.set_up_extended_location(containerapp_def)
        return containerapp_def

    def create_containerapp(self, containerapp_def):
        return self.ga_containerapp_create_decorator.create_containerapp(containerapp_def)

    def construct_containerapp_for_post_process(self, containerapp_def, r):
        return self.ga_containerapp_create_decorator.construct_containerapp_for_post_process(containerapp_def, r)

    def post_process_containerapp(self, containerapp_def, r):
        return self.ga_containerapp_create_decorator.post_process_containerapp(containerapp_def, r)

    def set_up_extended_location(self, containerapp_def):
        parsed_env = parse_resource_id(self.get_env())  # custom_location check here perhaps
        env_name = parsed_env['name']
        env_rg = parsed_env['resource_group']
        env_info = self.get_environment_client().show(cmd=self.cmd, resource_group_name=env_rg, name=env_name)
        if self.get_environment_type() == "connected":
            if not containerapp_def.get('extendedLocation'):
                containerapp_def["extendedLocation"] = env_info["extendedLocation"]
        return containerapp_def

    def get_environment_client(self):
        if self.get_yaml():
            yaml_containerapp = self.get_yaml_containerapp()
            if type(yaml_containerapp) != dict:  # pylint: disable=unidiomatic-typecheck
                raise ValidationError(
                    'Invalid YAML provided. Please see https://aka.ms/azure-container-apps-yaml for a valid containerapps YAML spec.')
            env = self.azext_default_utils.safe_get(yaml_containerapp, "properties", "environmentId")
            if not env:
                raise RequiredArgumentMissingError(
                    'environmentId is required. This can be retrieved using the `az containerapp env show -g MyResourceGroup -n MyContainerappEnvironment --query id` command. Please see https://aka.ms/azure-container-apps-yaml for a valid containerapps YAML spec.')
        else:
            env = self.get_env()
        environment_type = self.get_environment_type()
        parsed_env = parse_resource_id(env)  # custom_location check here perhaps

        # Validate environment type
        if parsed_env['resource_type'] == "connectedEnvironments":
            if environment_type == "managed":
                logger.warning(
                    "User passed a connectedEnvironment resource id but did not specify --environment-type connected. Using environment type connected.")
                environment_type = "connected"
        else:
            if environment_type == "connected":
                logger.warning(
                    "User passed a managedEnvironment resource id but specified --environment-type connected. Using environment type managed.")

        self.set_environment_type(environment_type)
        # Validate environment exists + grab location and/or custom_location
        try:
            if environment_type == "managed":
                return ManagedEnvironmentClient
            else:
                return ConnectedEnvironmentClient
        except:
            pass

    def get_yaml_containerapp(self):
        load_file = self.azext_default_utils.load_yaml_file(self.get_yaml())
        return self.azext_default_utils.process_loaded_yaml(load_file)

    def get_environment_type(self):
        return self.get_param("environment_type")

    def set_environment_type(self, environment_type):
        self.set_param("environment_type", environment_type)

    def get_env(self):
        return self.get_param("env")

    def get_yaml(self):
        return self.get_param("yaml")
