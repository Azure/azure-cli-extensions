# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def create_fleet(cmd, resource_group_name, fleet_name, location=None, tags=None):
    raise CLIError('TODO: Implement `fleet create`')


def list_fleet(cmd, resource_group_name=None):
    raise CLIError('TODO: Implement `fleet list`')


def update_fleet(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance