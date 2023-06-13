from typing import Dict, Any

from azure.cli.core.commands import AzCliCommand

from ._clients import ContainerAppClient
from ._utils import (_get_azext_module, GA_CONTAINERAPP_EXTENSION_NAME)


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
        azext_default_decorator = _get_azext_module(
            GA_CONTAINERAPP_EXTENSION_NAME, "azext_containerapp.containerapp_decorator")
        ga_containerapp_create_decorator = azext_default_decorator.ContainerAppCreateDecorator(
            cmd=cmd,
            client=ContainerAppClient,
            raw_parameters=raw_parameters,
            models=models
        )
        self.ga_containerapp_create_decorator = ga_containerapp_create_decorator

    def register_provider(self):
        self.ga_containerapp_create_decorator.register_provider()

    def validate_arguments(self):
        self.ga_containerapp_create_decorator.validate_arguments()

    def construct_containerapp(self):
        containerapp_def = self.ga_containerapp_create_decorator.construct_containerapp()
        return containerapp_def

    def create_containerapp(self, containerapp_def):
        return self.ga_containerapp_create_decorator.create_containerapp(containerapp_def)

    def construct_containerapp_for_post_process(self, containerapp_def, r):
        return self.ga_containerapp_create_decorator.construct_containerapp_for_post_process(containerapp_def, r)

    def post_process_containerapp(self, containerapp_def, r):
        return self.ga_containerapp_create_decorator.post_process_containerapp(containerapp_def)

