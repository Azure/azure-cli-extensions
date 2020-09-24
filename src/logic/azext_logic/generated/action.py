# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access

import argparse
from knack.util import CLIError


class AddIntegrationAccount(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.integration_account = action

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError(
                'usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'id':
                d['id'] = v
        return d


class AddIntegrationServiceEnvironment(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.integration_service_environment = action

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError(
                'usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'id':
                d['id'] = v
        return d


class AddKeyVault(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.key_vault = action

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError(
                'usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'name':
                d['name'] = v
            elif kl == 'id':
                d['id'] = v
        return d
