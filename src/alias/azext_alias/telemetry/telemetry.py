# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import datetime

from knack.log import get_logger

from azure.cli.core import telemetry as telemetry_core
from azure.cli.core.telemetry import _remove_cmd_chars, _remove_symbols, _get_stack_trace
from azure.cli.core._environment import get_config_dir
from azext_alias import VERSION as alias_extension_version


EXTENSION_NAME = 'azure-cli-alias-extension'
ALIAS_EXTENSION_PREFIX = 'Context.Default.Extension.Alias.'

logger = get_logger(__name__)

# pylint: disable=too-many-instance-attributes
class AliasExtensionTelemetrySession(object):

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.exceptions = []
        # Only show collided aliases when self.full_command_table_loaded is true
        self.collided_aliases = []
        self.execution_time = None
        self.full_command_table_loaded = False
        self.aliases_hit = []
        self.number_of_aliases_registered = 0

    def generate_payload(self):
        """
        Generate a list of telemetry events as payload
        """
        events = []
        transformation_task = self._get_alias_transformation_properties()
        transformation_task.update(self._get_based_properties())
        events.append(transformation_task)

        for exception in self.exceptions:
            properties = {
                'Reserved.DataModel.Fault.TypeString': exception.__class__.__name__,
                'Reserved.DataModel.Fault.Exception.Message': self.get_exception_message(exception),
                'Reserved.DataModel.Fault.Exception.StackTrace': _get_stack_trace(),
            }
            self.set_custom_properties(properties, 'ActionType', 'Exception')
            events.append(properties)

        return events

    def _get_alias_transformation_properties(self):
        properties = dict()
        self.set_custom_properties(properties, 'StartTime', str(self.start_time))
        self.set_custom_properties(properties, 'EndTime', str(self.end_time))
        self.set_custom_properties(properties, 'Version', alias_extension_version)
        self.set_custom_properties(properties, 'ExecutionTimeMs', self.execution_time)
        self.set_custom_properties(properties, 'FullCommandTableLoaded', str(self.full_command_table_loaded))
        self.set_custom_properties(properties, 'CollidedAliases', ','.join(self.collided_aliases))
        self.set_custom_properties(properties, 'AliasesHit', ','.join(self.aliases_hit))
        self.set_custom_properties(properties, 'NumberOfAliasRegistered', self.number_of_aliases_registered)
        self.set_custom_properties(properties, 'ActionType', 'Transformation')

        return properties

    def add_exception(self, exception):
        self.exceptions.append(exception)

    def add_alias_hit(self, alias_used):
        self.aliases_hit.append(alias_used)

    @classmethod
    def set_custom_properties(cls, prop, name, value):
        if name and value is not None:
            # 512 characters limit for strings
            prop['{}{}'.format(ALIAS_EXTENSION_PREFIX, name)] = value[:512] if isinstance(value, str) else value

    @classmethod
    def get_exception_message(cls, exception):
        exception_message = str(exception).replace(get_config_dir(), '.azure')
        return _remove_cmd_chars(_remove_symbols(exception_message))

    @classmethod
    def _get_based_properties(cls):
        return {
            'Reserved.ChannelUsed': 'AI'
        }


_session = AliasExtensionTelemetrySession()


def start():
    _session.start_time = datetime.datetime.now()


def set_execution_time(elapsed_time):
    _session.execution_time = elapsed_time


def set_full_command_table_loaded():
    _session.full_command_table_loaded = True


def set_collided_aliases(collided_aliases):
    _session.collided_aliases = collided_aliases


def set_exception(exception):
    _session.add_exception(exception)


def set_alias_hit(alias_used):
    _session.add_alias_hit(alias_used)


def set_number_of_aliases_registered(num_aliases):
    _session.number_of_aliases_registered = num_aliases


def conclude():
    _session.end_time = datetime.datetime.now()
    for properties in _session.generate_payload():
        telemetry_core.add_extension_event(EXTENSION_NAME, properties)
