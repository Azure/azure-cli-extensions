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

from ._client_factory import handle_raw_exception, handle_non_404_status_code_exception

logger = get_logger(__name__)


class ContainerappJavaLoggerDecorator(BaseResource):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.containerapp_def = None
        try:
            self.containerapp_def = self.client.show(cmd=cmd,
                                                resource_group_name=raw_parameters.get("resource_group_name"),
                                                name=raw_parameters.get("name"))
        except Exception as e:
            handle_non_404_status_code_exception(e)

        if not self.containerapp_def:
            raise ResourceNotFoundError("The containerapp '{}' does not exist".format(raw_parameters.get("name")))

        _get_existing_secrets(cmd, raw_parameters.get("resource_group_name"), raw_parameters.get("name"), self.containerapp_def)

    def get_argument_logger_name(self):
        return self.get_param("logger_name")

    def get_argument_logger_level(self):
        return self.get_param("logger_level")

    def get_argument_enable_java_agent(self):
        return self.get_param("enable_java_agent")

    def get_argument_all(self):
        return self.get_param("all")
    
    def _list_java_loggers(self):
        if 'logging' not in self.containerapp_def['properties']['configuration']['runtime']['java']['javaAgent']:
            return []

        if 'loggerSettings' not in self.containerapp_def['properties']['configuration']['runtime']['java']['javaAgent'][
            'logging']:
            return []

        return self.containerapp_def['properties']['configuration']['runtime']['java']['javaAgent']['logging'][
            'loggerSettings']

    def _construct_payload(self, loggers):
        if 'logging' not in self.containerapp_def['properties']['configuration']['runtime']['java']['javaAgent']:
            self.containerapp_def['properties']['configuration']['runtime']['java']['javaAgent']['logging'] = {}

        if 'loggerSettings' not in self.containerapp_def['properties']['configuration']['runtime']['java']['javaAgent'][
            'logging']:
            self.containerapp_def['properties']['configuration']['runtime']['java']['javaAgent']['logging']['loggerSettings'] = {}

        self.containerapp_def['properties']['configuration']['runtime']['java']['javaAgent']['logging'][
            'loggerSettings'] = loggers

    def validate_enabled_java_agent(self):
        if 'configuration' not in self.containerapp_def['properties']:
            return False
        if 'runtime' not in self.containerapp_def['properties']['configuration']:
            return False
        if 'java' not in self.containerapp_def['properties']['configuration']['runtime']:
            return False
        if 'javaAgent' not in self.containerapp_def['properties']['configuration']['runtime']['java']:
            return False

        return safe_get(self.containerapp_def['properties']['configuration']['runtime']['java']['javaAgent'], "enabled",
                        default=False) == True

    def create_or_update(self):

        loggers = self._list_java_loggers()

        exist_loggers = [logger["logger"].lower() for logger in loggers]

        if self.get_argument_logger_name().lower() not in exist_loggers:  # create
            new_logger = JavaLoggerSetting
            new_logger["logger"] = self.get_argument_logger_name()
            new_logger["level"] = self.get_argument_logger_level()
            loggers.append(new_logger)
        else:  # update
            for logger in loggers:
                if logger["logger"] == self.get_argument_logger_name():
                    logger["level"] = self.get_argument_logger_level()

        self._construct_payload(loggers)

        try:
            r = self.client.create_or_update(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                name=self.get_argument_name(), container_app_envelope=self.containerapp_def,
                no_wait=self.get_argument_no_wait())
            return r["properties"]['configuration']['runtime']['java']['javaAgent']['logging']['loggerSettings']
        except Exception as e:
            handle_raw_exception(e)

    def show(self):
        if self.get_argument_all() is None:
            loggers = self._list_java_loggers()
            for logger in loggers:
                if logger["logger"] == self.get_argument_logger_name():
                    return logger
            raise ValidationError(
                f"logger {self.get_argument_logger_name().lower()} does not exists, please use the exist logger name")
        else:
            return self._list_java_loggers()

    def delete(self):
        if self.get_argument_all() is not None:
            new_loggers = []
        else:
            loggers = self._list_java_loggers()
            exist_loggers = [logger["logger"].lower() for logger in loggers]
            if self.get_argument_logger_name().lower() not in exist_loggers:
                raise ValidationError(
                    f"logger {self.get_argument_logger_name().lower()} does not exists, please use the exist logger name")
            new_loggers = list(filter(lambda logger: logger["logger"] != self.get_argument_logger_name(), loggers))

        self._construct_payload(new_loggers)

        try:
            r = self.client.create_or_update(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                name=self.get_argument_name(), container_app_envelope=self.containerapp_def,
                no_wait=self.get_argument_no_wait())
            if 'loggerSettings' in r["properties"]['configuration']['runtime']['java']['javaAgent']['logging']:
                return r["properties"]['configuration']['runtime']['java']['javaAgent']['logging']['loggerSettings']
            else: # no logger settings
                return []
        except Exception as e:
            handle_raw_exception(e)