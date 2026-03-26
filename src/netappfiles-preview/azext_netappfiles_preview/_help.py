# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

# pylint: disable=line-too-long


helps['netappfiles'] = """
    type: group
    short-summary: Manage Azure NetApp Files (ANF) Resources.
"""
helps.pop('netappfiles volume create', None)

helps.pop('netappfiles volume update', None)
