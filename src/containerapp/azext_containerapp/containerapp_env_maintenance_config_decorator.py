# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, broad-except, logging-format-interpolation

from copy import deepcopy
from knack.log import get_logger
from typing import Any, Dict

from azure.cli.core.azclierror import (ValidationError)
from azure.cli.core.commands import AzCliCommand
from azure.cli.command_modules.containerapp.base_resource import BaseResource

from ._models import MaintenanceConfiguration as MaintenanceConfigurationModel
from ._client_factory import handle_raw_exception, handle_non_404_status_code_exception

logger = get_logger(__name__)


class ContainerappEnvMaintenanceConfigDecorator(BaseResource):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.maintenance_config_def = deepcopy(MaintenanceConfigurationModel)
        self.existing_maintenance_config_def = None

    def get_argument_environment_name(self):
        return self.get_param('env_name')

    def get_argument_resource_group_name(self):
        return self.get_param('resource_group_name')

    def get_argument_weekday(self):
        return self.get_param('weekday')

    def get_argument_start_hour_utc(self):
        return self.get_param('start_hour_utc')

    def get_argument_duration(self):
        return self.get_param('duration')


class ContainerAppEnvMaintenanceConfigPreviewDecorator(ContainerappEnvMaintenanceConfigDecorator):
    def validate_arguments(self):
        if self.get_argument_start_hour_utc() is not None:
            if not (0 <= int(self.get_argument_start_hour_utc()) <= 23):
                raise ValidationError("Start hour must be an integer from 0 to 23")

        if self.get_argument_duration() is not None:
            if not (8 <= int(self.get_argument_duration()) <= 24):
                raise ValidationError("Duration must be an integer from 8 to 24")

        if self.get_argument_weekday() is not None:
            if self.get_argument_weekday().lower() not in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                raise ValidationError("Weekday must be a day of the week")

    def construct_payload(self, forUpdate=False):
        if forUpdate:
            self.existing_maintenance_config_def = self.client.list(
                cmd=self.cmd,
                resource_group_name=self.get_argument_resource_group_name(),
                environment_name=self.get_argument_environment_name())

            self.maintenance_config_def = deepcopy(self.existing_maintenance_config_def)

        if self.get_argument_start_hour_utc() is not None:
            self.maintenance_config_def["properties"]["scheduledEntries"][0]["startHourUtc"] = self.get_argument_start_hour_utc()
        if self.get_argument_duration() is not None:
            self.maintenance_config_def["properties"]["scheduledEntries"][0]["durationHours"] = self.get_argument_duration()
        if self.get_argument_weekday() is not None:
            self.maintenance_config_def["properties"]["scheduledEntries"][0]["weekDay"] = self.get_argument_weekday()

    def create_or_update(self):
        try:
            return self.client.create_or_update(
                cmd=self.cmd,
                resource_group_name=self.get_argument_resource_group_name(),
                environment_name=self.get_argument_environment_name(),
                maintenance_config_envelope=self.maintenance_config_def)
        except Exception as e:
            handle_raw_exception(e)

    def remove(self):
        try:
            return self.client.remove(
                cmd=self.cmd,
                resource_group_name=self.get_argument_resource_group_name(),
                environment_name=self.get_argument_environment_name())
        except Exception as e:
            handle_raw_exception(e)

    def list(self):
        try:
            return self.client.list(
                cmd=self.cmd,
                resource_group_name=self.get_argument_resource_group_name(),
                environment_name=self.get_argument_environment_name())
        except Exception as e:
            handle_non_404_status_code_exception(e)
            return ""
