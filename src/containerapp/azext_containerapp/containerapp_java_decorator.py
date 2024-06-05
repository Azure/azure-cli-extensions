# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, broad-except, logging-format-interpolation
from knack.log import get_logger
from knack.util import CLIError
from typing import Any, Dict

from azure.cli.command_modules.containerapp._utils import safe_get, safe_set
from azure.cli.core.commands import AzCliCommand
from azure.cli.core.azclierror import ValidationError, ResourceNotFoundError
from azure.cli.command_modules.containerapp.base_resource import BaseResource
from azure.cli.command_modules.containerapp._utils import _get_existing_secrets

from ._client_factory import handle_raw_exception, handle_non_404_status_code_exception
from ._models import JavaLoggerSetting

logger = get_logger(__name__)


class ContainerappJavaLoggerDecorator(BaseResource):

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.containerapp_def = None
        try:
            self.containerapp_def = self.client.show(
                cmd=cmd,
                resource_group_name=raw_parameters.get("resource_group_name"),
                name=raw_parameters.get("name"))
        except Exception as e:
            handle_non_404_status_code_exception(e)

        if not self.containerapp_def:
            raise ResourceNotFoundError("The containerapp '{}' does not exist".format(raw_parameters.get("name")))

        _get_existing_secrets(cmd, raw_parameters.get("resource_group_name"), raw_parameters.get("name"), self.containerapp_def)

    def validate_arguments(self):
        if self.get_argument_all() is None and self.get_argument_logger_name() is None:
            raise CLIError(
                'Either of --logger-name/--all needs to be specified.')

        if self.get_argument_all() is not None and self.get_argument_logger_name() is not None:
            raise CLIError(
                'Both --logger-name and --all cannot be specified together.')

        if not safe_get(self.containerapp_def['properties'], "configuration", "runtime", "java", "javaAgent", "enabled", default=False):
            raise ValidationError(
                "The containerapp '{}' does not enable java agent, "
                "please run `az containerapp update --name {} --resource-group {} --enable-java-agent true` to enable java agent".format(
                    self.get_argument_name(), self.get_argument_name(), self.get_argument_resource_group_name()))

    def show(self):
        loggers = safe_get(self.containerapp_def['properties'], 'configuration', 'runtime', 'java', 'javaAgent',
                           'logging', 'loggerSettings', default=[])
        if self.get_argument_all() is None:  # pylint: disable=no-else-raise
            for java_logger in loggers:
                if java_logger["logger"] == self.get_argument_logger_name():
                    return java_logger
            raise ValidationError(
                f"logger {self.get_argument_logger_name().lower()} does not exists, please use the exist logger name")
        else:
            return loggers

    def get_argument_logger_name(self):
        return self.get_param("logger_name")

    def get_argument_logger_level(self):
        return self.get_param("logger_level")

    def get_argument_all(self):
        return self.get_param("all")


class ContainerappJavaLoggerSetDecorator(ContainerappJavaLoggerDecorator):
    # pylint: disable=useless-super-delegation
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def construct_payload(self):
        loggers = safe_get(self.containerapp_def['properties'], 'configuration', 'runtime', 'java', 'javaAgent', 'logging', 'loggerSettings', default=[])
        exist_loggers = [java_logger["logger"].lower() for java_logger in loggers]
        if self.get_argument_logger_name().lower() not in exist_loggers:  # create
            new_logger = JavaLoggerSetting
            new_logger["logger"] = self.get_argument_logger_name()
            new_logger["level"] = self.get_argument_logger_level()
            loggers.append(new_logger)
        else:  # update
            for java_logger in loggers:
                if java_logger["logger"] == self.get_argument_logger_name():
                    java_logger["level"] = self.get_argument_logger_level()
        safe_set(self.containerapp_def['properties'], 'configuration', 'runtime', 'java', 'javaAgent', 'logging', 'loggerSettings', value=loggers)

    def create_or_update(self):
        try:
            r = self.client.create_or_update(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                name=self.get_argument_name(), container_app_envelope=self.containerapp_def,
                no_wait=self.get_argument_no_wait())
            return safe_get(r, 'properties', 'configuration', 'runtime', 'java', 'javaAgent', 'logging', 'loggerSettings')
        except Exception as e:
            handle_raw_exception(e)


class ContainerappJavaLoggerDeleteDecorator(ContainerappJavaLoggerDecorator):
    # pylint: disable=useless-super-delegation
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def construct_payload(self):
        if self.get_argument_all() is not None:
            new_loggers = []
        else:
            loggers = safe_get(self.containerapp_def['properties'], 'configuration', 'runtime', 'java', 'javaAgent', 'logging', 'loggerSettings', default=[])
            exist_loggers = [java_logger["logger"].lower() for java_logger in loggers]
            if self.get_argument_logger_name().lower() not in exist_loggers:
                raise ValidationError(
                    f"logger {self.get_argument_logger_name().lower()} does not exists, please use the exist logger name")
            new_loggers = list(filter(lambda logger: logger["logger"] != self.get_argument_logger_name(), loggers))

        safe_set(self.containerapp_def['properties'], 'configuration', 'runtime', 'java', 'javaAgent', 'logging',
                 'loggerSettings', value=new_loggers)

    def delete(self):
        try:
            r = self.client.create_or_update(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                name=self.get_argument_name(), container_app_envelope=self.containerapp_def,
                no_wait=self.get_argument_no_wait())
            return safe_get(r, 'properties', 'configuration', 'runtime', 'java', 'javaAgent', 'logging', 'loggerSettings', default=[])
        except Exception as e:
            handle_raw_exception(e)
