# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

import argparse
from azure.cli.core.azclierror import InvalidArgumentValueError
from knack.log import get_logger
from .vendored_sdks.azure_mgmt_webpubsub.models import EventHandler, UpstreamAuthSettings, ManagedIdentitySettings, IPRule

logger = get_logger(__name__)


# pylint: disable=protected-access, too-few-public-methods
class EventHandlerTemplateUpdateAction(argparse._AppendAction):
    # --event-handler urlTemplate="" user_event_pattern="" system_event="" system_event="" auth_type="" auth_resource=""
    def __call__(self, parser, namespace, values, option_string=None):
        kwargs = {}
        auth_type = None
        auth_resource = None
        system_events = []
        for item in values:
            try:
                key, value = item.split('=', 1)

                if key == 'system-event':
                    system_events.append(value)
                    continue
                if key == 'auth-type':
                    auth_type = value
                    continue
                if key == 'auth-resource':
                    auth_resource = value
                    continue

                kwargs[key.replace('-', '_')] = value
            except ValueError:
                raise InvalidArgumentValueError('usage error: {} KEY=VALUE [KEY=VALUE ...]'.format(option_string))
        if auth_type is not None:
            kwargs['auth'] = UpstreamAuthSettings(
                type=auth_type, managed_identity=ManagedIdentitySettings(resource=auth_resource))
        if system_events:
            kwargs['system_events'] = system_events
        value = EventHandler(**kwargs)
        super().__call__(parser, namespace, value, option_string)


class IPRuleTemplateUpdateAction(argparse._AppendAction):
    # --ip-rule value="" action=""
    def __call__(self, parser, namespace, values, option_string=None):
        ipRuleValue = None
        ipRuleAction = None
        for item in values:
            try:
                key, value = item.split('=', 1)
                if key == 'value':
                    ipRuleValue = value
                elif key == 'action':
                    ipRuleAction = value
                else:
                    raise InvalidArgumentValueError('usage error: {} KEY=VALUE [KEY=VALUE ...]'.format(option_string))
            except ValueError:
                raise InvalidArgumentValueError('usage error: {} KEY=VALUE [KEY=VALUE ...]'.format(option_string))
        if ipRuleValue is None or ipRuleAction is None:
            raise InvalidArgumentValueError('usage error: {} KEY=VALUE [KEY=VALUE ...]'.format(option_string))
        value = IPRule(value=ipRuleValue, action=ipRuleAction)
        super().__call__(parser, namespace, value, option_string)
