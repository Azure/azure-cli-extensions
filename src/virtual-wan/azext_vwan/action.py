# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access
# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods
import argparse
from azure.cli.core.azclierror import ArgumentUsageError


class RadiusServerAddAction(argparse._AppendAction):

    def __call__(self, parser, namespace, values, keys=None, option_string=None):
        RadiusServer = namespace._cmd.get_models('RadiusServer')
        kwargs = {}
        for item in values:
            try:
                key, value = item.split('=', 1)
                kwargs['radius_server_' + key] = value
            except ValueError as exc:
                raise ArgumentUsageError(f"usage error: {option_string} address=VALUE, score=VALUE, secret=VALUE") from exc
        action = RadiusServer(**kwargs)
        super().__call__(parser, namespace, action, option_string)
