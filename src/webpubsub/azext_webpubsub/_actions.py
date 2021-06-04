# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

import argparse
from azure.cli.core.azclierror import InvalidArgumentValueError
from knack.log import get_logger
from .vendored_sdks.azure_mgmt_webpubsub.models import EventHandlerTemplate

logger = get_logger(__name__)


# pylint: disable=protected-access, too-few-public-methods
class EventHandlerTemplateUpdateAction(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        kwargs = {}
        for item in values:
            try:
                key, value = item.split('=', 1)
                kwargs[key.replace('-', '_')] = value
            except ValueError:
                raise InvalidArgumentValueError('usage error: {} KEY=VALUE [KEY=VALUE ...]'.format(option_string))
        value = EventHandlerTemplate(**kwargs)
        super().__call__(parser, namespace, value, option_string)
