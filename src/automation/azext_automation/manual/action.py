# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=protected-access

import argparse
from collections import defaultdict
from knack.util import CLIError


class AddPropertiesParameters(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.properties_parameters = action

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            v = properties[k]
            d[k] = v[0]
        return d
