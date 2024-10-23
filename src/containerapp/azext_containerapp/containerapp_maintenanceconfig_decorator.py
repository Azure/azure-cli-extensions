# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, broad-except, logging-format-interpolation


from knack.log import get_logger
from typing import Any, Dict

from azure.cli.core.commands import AzCliCommand
from azure.cli.command_modules.containerapp.base_resource import BaseResource

from ._models import MaintenanceConfiguration as MaintenanceConfigurationModel
from ._client_factory import handle_raw_exception

logger = get_logger(__name__)


class MaintenanceConfigDecorator(BaseResource):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.maintenance_config_def = MaintenanceConfigurationModel

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


class MaintenanceConfigPreviewDecorator(MaintenanceConfigDecorator):
    def construct_payload(self):
        self.maintenance_config_def["properties"]["scheduledEntries"][0]["startHourUtc"] = self.get_argument_start_hour_utc()
        self.maintenance_config_def["properties"]["scheduledEntries"][0]["durationHours"] = self.get_argument_duration()
        self.maintenance_config_def["properties"]["scheduledEntries"][0]["weekDay"] = self.get_argument_weekday()

    def add(self):
        try:
            return self.client.add(
                cmd=self.cmd,
                resource_group_name=self.get_argument_resource_group_name(),
                environment_name=self.get_argument_environment_name(),
                maintenance_config_envelope=self.maintenance_config_def,
                no_wait=self.get_argument_no_wait())
        except Exception as e:
            handle_raw_exception(e)

    def update(self):
        try:
            return self.client.update(
                cmd=self.cmd,
                resource_group_name=self.get_argument_resource_group_name(),
                environment_name=self.get_argument_environment_name(),
                maintenance_config_envelope=self.maintenance_config_def,
                no_wait=self.get_argument_no_wait())
        except Exception as e:
            handle_raw_exception(e)

    def delete(self):
        try:
            return self.client.delete(
                cmd=self.cmd,
                resource_group_name=self.get_argument_resource_group_name(),
                environment_name=self.get_argument_environment_name(),
                no_wait=self.get_argument_no_wait())
        except Exception as e:
            handle_raw_exception(e)

    def show(self):
        try:
            return self.client.show(
                cmd=self.cmd,
                resource_group_name=self.get_argument_resource_group_name(),
                environment_name=self.get_argument_environment_name())
        except Exception as e:
            handle_raw_exception(e)
