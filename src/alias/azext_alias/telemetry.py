# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import sys
import datetime
import traceback

from knack.log import get_logger

import azure.cli.core.decorators as decorators
from azure.cli.core import telemetry as telemetry_core
from azure.cli.core._environment import get_config_dir
from azext_alias.version import VERSION

EXTENSION_NAME = 'alias'
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
        self.set_custom_properties(properties, 'Version', VERSION)
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


@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def start():
    _session.start_time = datetime.datetime.now()


@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def set_execution_time(elapsed_time):
    _session.execution_time = elapsed_time


@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def set_full_command_table_loaded():
    _session.full_command_table_loaded = True


@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def set_collided_aliases(collided_aliases):
    _session.collided_aliases = collided_aliases


@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def set_exception(exception):
    _session.add_exception(exception)


@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def set_alias_hit(alias_used):
    _session.add_alias_hit(alias_used)


@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def set_number_of_aliases_registered(num_aliases):
    _session.number_of_aliases_registered = num_aliases


@decorators.suppress_all_exceptions(raise_in_diagnostics=True)
def conclude():
    if not _session.aliases_hit:
        return

    _session.end_time = datetime.datetime.now()
    for properties in _session.generate_payload():
        telemetry_core.add_extension_event(EXTENSION_NAME, properties)


@decorators.suppress_all_exceptions(fallback_return='')
def _get_stack_trace():
    def _get_root_path():
        dir_path = os.path.dirname(os.path.realpath(__file__))
        head, tail = os.path.split(dir_path)
        while tail and tail != 'azext_alias':
            head, tail = os.path.split(head)
        return head

    def _remove_root_paths(s):
        root = _get_root_path()
        frames = [p.replace(root, '') for p in s]
        return str(frames)

    _, _, ex_traceback = sys.exc_info()
    trace = traceback.format_tb(ex_traceback)
    return _remove_cmd_chars(_remove_symbols(_remove_root_paths(trace)))


def _remove_cmd_chars(s):
    if isinstance(s, str):
        return s.replace("'", '_').replace('"', '_').replace('\r\n', ' ').replace('\n', ' ')
    return s


def _remove_symbols(s):
    if isinstance(s, str):
        for c in '$%^&|':
            s = s.replace(c, '_')
    return s
