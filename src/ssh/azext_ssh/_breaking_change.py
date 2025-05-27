# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.breaking_change import register_other_breaking_change

register_other_breaking_change(
    'ssh arc',
    'On May 21st 2025, any ssh arc commands on versions <2.0.4 will no longer work. '
    'Please upgrade to az ssh version >=2.0.4',
    target_version='2.0.4')
register_other_breaking_change(
    'ssh config',
    'On May 21st 2025, any ssh commands connecting to ARC machines on versions <2.0.4 will no longer work. '
    'Please upgrade to az ssh version >=2.0.4',
    target_version='2.0.4')
register_other_breaking_change(
    'ssh vm',
    'On May 21st 2025, any ssh commands connecting to ARC machines on versions <2.0.4 will no longer work. '
    'Please upgrade to az ssh version >=2.0.4',
    target_version='2.0.4')
