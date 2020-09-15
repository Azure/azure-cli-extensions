# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
from knack.util import CLIError
from collections import defaultdict


# pylint: disable=protected-access, too-few-public-methods
class AddConfigurationSettings(argparse._AppendAction):

    def __call__(self, parser, namespace, values, option_string=None):
        settings = {}
        for item in values:
            try:
                key, value = item.split('=', 1)
                settings[key] = value
            except ValueError:
                raise CLIError('Usage error: {} configuration_setting_key=configuration_setting_value'.
                               format(option_string))
        super(AddConfigurationSettings, self).__call__(parser, namespace, settings, option_string)


# pylint: disable=protected-access, too-few-public-methods
class AddConfigurationProtectedSettings(argparse._AppendAction):

    def __call__(self, parser, namespace, values, option_string=None):
        prot_settings = {}
        for item in values:
            try:
                key, value = item.split('=', 1)
                prot_settings[key] = value
            except ValueError:
                raise CLIError('Usage error: {} configuration_protected_setting_key='
                               'configuration_protected_setting_value'.format(option_string))
        super(AddConfigurationProtectedSettings, self).__call__(parser, namespace, prot_settings, option_string)

