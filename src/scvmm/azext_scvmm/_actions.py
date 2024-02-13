# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access,too-few-public-methods

"""
This file contains actions for parsing complex arguments.
"""

import argparse
from .scvmm_utils import create_dictionary_from_arg_string


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
