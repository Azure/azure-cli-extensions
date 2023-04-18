# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def create_aosm(cmd, resource_group_name, aosm_name, location=None, tags=None):
    raise CLIError('TODO: Implement `aosm create`')


def list_aosm(cmd, resource_group_name=None):
    raise CLIError('TODO: Implement `aosm list`')


def update_aosm(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance
