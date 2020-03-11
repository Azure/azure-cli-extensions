# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def create_connect_2020(cmd, client, resource_group_name, cluster_name, location=None, tags=None):
    raise CLIError('TODO: Implement `connect_2020 create`')


def list_connect_2020(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `connect_2020 list`')


def update_connect_2020(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance