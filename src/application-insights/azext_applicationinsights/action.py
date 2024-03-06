# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access
# pylint: disable=raise-missing-from
# pylint: disable=line-too-long
import argparse
from collections import defaultdict

from azure.cli.core.azclierror import ArgumentUsageError


class AddLocations(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super().__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            err_msg = f'usage error: {option_string} [KEY=VALUE ...]'
            raise ArgumentUsageError(err_msg)
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]

            if kl == 'id':
                d['location'] = v[0]

            else:
                err_msg = f'Unsupported Key {k} is provided for parameter locations. All possible keys are: Id'
                raise ArgumentUsageError(err_msg)

        return d


class AddContentValidation(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.content_validation = action

    def get_action(self, values, option_string):
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            err_msg = f'usage error: {option_string} [KEY=VALUE ...]'
            raise ArgumentUsageError(err_msg)
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]

            if kl == 'content-match':
                d['content_match'] = v[0]

            elif kl == 'ignore-case':
                d['ignore_case'] = v[0]

            elif kl == 'pass-if-text-found':
                d['pass_if_text_found'] = v[0]

            else:
                err_msg = f'Unsupported Key {k} is provided for parameter content-validation. All possible keys are: content-match, ignore-case, pass-if-text-found'
                raise ArgumentUsageError(err_msg)

        return d


class AddHeaders(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super().__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            err_msg = f'usage error: {option_string} [KEY=VALUE ...]'
            raise ArgumentUsageError(err_msg)
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]

            if kl == 'key':
                d['header_field_name'] = v[0]

            elif kl == 'value':
                d['header_field_value'] = v[0]

            else:
                err_msg = f'Unsupported Key {k} is provided for parameter headers. All possible keys are: key, value'
                raise ArgumentUsageError(err_msg)

        return d
