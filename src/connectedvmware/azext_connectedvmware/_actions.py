# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable= protected-access, too-few-public-methods, raise-missing-from, no-self-use, consider-using-f-string

"""
This file contains actions for parsing complex arguments.
"""

import argparse
from collections import defaultdict
from azure.cli.core.azclierror import InvalidArgumentValueError
from azext_connectedvmware.vmware_utils import create_dictionary_from_arg_string


class VmNicAddAction(argparse._AppendAction):
    """
    Action for parsing the nic arguments.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        nic_params_dict = create_dictionary_from_arg_string(values, option_string)
        if namespace.nics:
            namespace.nics.append(nic_params_dict)
        else:
            namespace.nics = [nic_params_dict]


class VmDiskAddAction(argparse._AppendAction):
    """
    Action for parsing the disk arguments.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        disk_params_dict = create_dictionary_from_arg_string(values, option_string)
        if namespace.disks:
            namespace.disks.append(disk_params_dict)
        else:
            namespace.disks = [disk_params_dict]


class AddStatus(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.status = action

    def get_action(self, values, option_string):
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            raise InvalidArgumentValueError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]

            if kl == 'code':
                d['code'] = v[0]

            elif kl == 'level':
                d['level'] = v[0]

            elif kl == 'display-status':
                d['display_status'] = v[0]

            elif kl == 'message':
                d['message'] = v[0]

            elif kl == 'time':
                d['time'] = v[0]

            else:
                raise InvalidArgumentValueError(
                    'Unsupported Key {} is provided for parameter status. All possible keys are: code, level,'
                    ' display-status, message, time'.format(k)
                )

        return d
