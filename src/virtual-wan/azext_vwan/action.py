# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access
# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods
import argparse
from knack.util import CLIError
from .profiles import CUSTOM_VHUB_ROUTE_TABLE


class RadiusServerAddAction(argparse._AppendAction):

    def __call__(self, parser, namespace, values, keys=None, option_string=None):
        RadiusServer = namespace._cmd.get_models('RadiusServer', resource_type=CUSTOM_VHUB_ROUTE_TABLE)
        kwargs = {}
        for item in values:
            try:
                key, value = item.split('=', 1)
                kwargs['radius_server_' + key] = value
            except ValueError:
                raise CLIError('usage error: {} address=VALUE, score=VALUE, secret=VALUE'.format(option_string))
        action = RadiusServer(**kwargs)
        super(RadiusServerAddAction, self).__call__(parser, namespace, action, option_string)
