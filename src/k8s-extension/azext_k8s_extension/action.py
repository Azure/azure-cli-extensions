# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
from azure.cli.core.azclierror import ArgumentUsageError


# pylint: disable=protected-access, too-few-public-methods
class AddConfigurationSettings(argparse._AppendAction):

    def __call__(self, parser, namespace, values, option_string=None):
        settings = {}
        for item in values:
            try:
                key, value = item.split('=', 1)
                settings[key] = value
            except ValueError as ex:
                raise ArgumentUsageError('Usage error: {} configuration_setting_key=configuration_setting_value'.
                                         format(option_string)) from ex
        super().__call__(parser, namespace, settings, option_string)


# pylint: disable=protected-access, too-few-public-methods
class AddConfigurationProtectedSettings(argparse._AppendAction):

    def __call__(self, parser, namespace, values, option_string=None):
        prot_settings = {}
        for item in values:
            try:
                key, value = item.split('=', 1)
                prot_settings[key] = value
            except ValueError as ex:
                raise ArgumentUsageError('Usage error: {} configuration_protected_setting_key='
                                         'configuration_protected_setting_value'.format(option_string)) from ex
        super().__call__(parser, namespace, prot_settings, option_string)

class AddPlanInfo(argparse._AppendAction):

    def __call__(self, parser, namespace, values, option_string=None):
        plan_details = dict({})
        keysExpected = {'name', 'publisher', 'product'}
        for item in values:
            try:
                key, value = item.split('=', 1)
                if key not in keysExpected:
                    raise ArgumentUsageError('Usage error: unknown property: {} used in plan info'.format(key)) 
                plan_details[key] = value
            except ValueError as ex:
                raise ArgumentUsageError('Usage error: {} plan_info_key=plan_info_value'.
                                         format(option_string)) from ex
        for key in keysExpected:
            if key not in plan_details:
                raise ArgumentUsageError('Usage error: Missing required plan info property: {}'.format(key))
 
        super().__call__(parser, namespace, plan_details, option_string)