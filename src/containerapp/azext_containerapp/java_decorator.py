# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Any, Dict

from azure.cli.command_modules.containerapp._utils import safe_get
from azure.cli.core.commands import AzCliCommand
from azure.cli.core.azclierror import ValidationError, ResourceNotFoundError
from azure.cli.command_modules.containerapp.base_resource import BaseResource
from knack.log import get_logger

from azure.cli.command_modules.containerapp._utils import _get_existing_secrets

from ._models import JavaLoggerSetting

from ._client_factory import handle_raw_exception

logger = get_logger(__name__)


class JavaLoggerDecorator(BaseResource):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)

    def get_argument_logger_name(self):
        return self.get_param("logger_name")

    def get_argument_logger_level(self):
        return self.get_param("logger_level")

    def get_argument_enable_java_agent(self):
        return self.get_param("enable_java_agent")

    def get_argument_all(self):
        return self.get_param("all")

    def _get_containerapp(self, cmd, resource_group_name, name):
        containerapp_def = None
        try:
            containerapp_def = self.client.show(cmd=cmd,
                                                resource_group_name=resource_group_name,
                                                name=name)
        except:
            pass
        if not containerapp_def:
            raise ResourceNotFoundError("The containerapp '{}' does not exist".format(name))

        _get_existing_secrets(cmd, resource_group_name, name, containerapp_def)

        return containerapp_def

    def _check_java_agent_enabled(self, containerapp_def):
        if 'configuration' not in containerapp_def['properties']:
            return False
        if 'runtime' not in containerapp_def['properties']['configuration']:
            return False
        if 'java' not in containerapp_def['properties']['configuration']['runtime']:
            return False
        if 'javaAgent' not in containerapp_def['properties']['configuration']['runtime']['java']:
            return False

        return safe_get(containerapp_def['properties']['configuration']['runtime']['java']['javaAgent'], "enabled",
                        default=False) == True

    def _list_java_loggers(self, containerapp_def):
        if 'logging' not in containerapp_def['properties']['configuration']['runtime']['java']['javaAgent']:
            return []

        if 'loggerSettings' not in containerapp_def['properties']['configuration']['runtime']['java']['javaAgent'][
            'logging']:
            return []

        return containerapp_def['properties']['configuration']['runtime']['java']['javaAgent']['logging'][
            'loggerSettings']

    def _construct_loggers(self, containerapp_def, loggers):
        if 'logging' not in containerapp_def['properties']['configuration']['runtime']['java']['javaAgent']:
            containerapp_def['properties']['configuration']['runtime']['java']['javaAgent']['logging'] = {}

        if 'loggerSettings' not in containerapp_def['properties']['configuration']['runtime']['java']['javaAgent'][
            'logging']:
            containerapp_def['properties']['configuration']['runtime']['java']['javaAgent']['logging']['loggerSettings'] = {}

        containerapp_def['properties']['configuration']['runtime']['java']['javaAgent']['logging'][
            'loggerSettings'] = loggers

    def create_or_update_logger(self):
        containerapp_def = self._get_containerapp(self.cmd, self.get_argument_resource_group_name(),
                                                  self.get_argument_name())

        if not self._check_java_agent_enabled(containerapp_def):
            raise ValidationError(
                "The containerapp '{}' does not enable java agent, "
                "please run `az containerapp java --name {} --resource-group {} --enable-java-agent true` to enable java agent".format(
                    self.get_argument_name(), self.get_argument_name(), self.get_argument_resource_group_name()))

        loggers = self._list_java_loggers(containerapp_def)

        exist_loggers = [logger["logger"].lower() for logger in loggers]

        if self.get_argument_logger_name().lower() not in exist_loggers: # create
            new_logger = JavaLoggerSetting
            new_logger["logger"] = self.get_argument_logger_name()
            new_logger["level"] = self.get_argument_logger_level()
            loggers.append(new_logger)
        else: # update
            for logger in loggers:
                if logger["logger"] == self.get_argument_logger_name():
                    logger["level"] = self.get_argument_logger_level()

        self._construct_loggers(containerapp_def, loggers)

        try:
            r = self.client.create_or_update(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                name=self.get_argument_name(), container_app_envelope=containerapp_def,
                no_wait=self.get_argument_no_wait())
            return r["properties"]['configuration']['runtime']['java']['javaAgent']['logging']['loggerSettings']
        except Exception as e:
            handle_raw_exception(e)

    def show_logger(self):
        containerapp_def = self._get_containerapp(self.cmd, self.get_argument_resource_group_name(),
                                                  self.get_argument_name())

        if not self._check_java_agent_enabled(containerapp_def):
            raise ValidationError(
                "The containerapp '{}' does not enable java agent, "
                "please run `az containerapp java --name {} --resource-group {} --enable-java-agent true` to enable java agent".format(
                    self.get_argument_name(), self.get_argument_name(), self.get_argument_resource_group_name()))

        if self.get_argument_all() is None:
            loggers = self._list_java_loggers(containerapp_def)
            for logger in loggers:
                if logger["logger"] == self.get_argument_logger_name():
                    return logger
            raise ValidationError(
                f"logger {self.get_argument_logger_name().lower()} does not exists, please use the exist logger name")
        else:
            return self._list_java_loggers(containerapp_def)

    def delete_logger(self):
        containerapp_def = self._get_containerapp(self.cmd, self.get_argument_resource_group_name(),
                                                  self.get_argument_name())

        if not self._check_java_agent_enabled(containerapp_def):
            raise ValidationError(
                "The containerapp '{}' does not enable java agent, please run `az containerapp java --enable-java-agent true` to enable java agent".format(
                    self.get_argument_name()))

        if self.get_argument_all() is not None:
            new_loggers = []
        else:
            loggers = self._list_java_loggers(containerapp_def)
            exist_loggers = [logger["logger"].lower() for logger in loggers]
            if self.get_argument_logger_name().lower() not in exist_loggers:
                raise ValidationError(
                    f"logger {self.get_argument_logger_name().lower()} does not exists, please use the exist logger name")
            new_loggers = list(filter(lambda logger: logger["logger"] != self.get_argument_logger_name(), loggers))

        self._construct_loggers(containerapp_def, new_loggers)

        try:
            r = self.client.create_or_update(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                name=self.get_argument_name(), container_app_envelope=containerapp_def,
                no_wait=self.get_argument_no_wait())
            if 'loggerSettings' in r["properties"]['configuration']['runtime']['java']['javaAgent']['logging']:
                return r["properties"]['configuration']['runtime']['java']['javaAgent']['logging']['loggerSettings']
            else: # no logger settings
                return []
        except Exception as e:
            handle_raw_exception(e)