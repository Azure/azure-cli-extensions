# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
from knack.util import CLIError


# pylint: disable=protected-access, too-few-public-methods
class ResourceGroupAssignAddAction(argparse._AppendAction):

    def __call__(self, parser, namespace, values, option_string=None):
        rg = {}
        for item in values:
            try:
                key, value = item.split('=', 1)
                rg[key] = value
            except ValueError:
                raise CLIError('Usage error: {} artifact_name=VALUE name=VALUE location=VALUE'.format(option_string))
        if 'artifact_name' not in rg:
            raise CLIError('{} must provide value for artifact_name in the format of artifact_name=VALUE'
                           .format(option_string))
        super(ResourceGroupAssignAddAction, self).__call__(parser, namespace, rg, option_string)
