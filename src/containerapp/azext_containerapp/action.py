# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
from collections import defaultdict
from azure.cli.core.azclierror import ValidationError


class AddCustomizedKeys(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.customized_keys = action

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k] = v
            properties = dict(properties)
            return properties
        except ValueError:
            raise ValidationError('Usage error: {} [DesiredKey=DefaultKey ...]'.format(option_string))
