# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def create_scheduled_query(cmd, resource_group_name, scheduled_query_name, location=None, tags=None):
    raise CLIError('TODO: Implement `scheduled_query create`')


def list_scheduled_query(cmd, resource_group_name=None):
    raise CLIError('TODO: Implement `scheduled_query list`')


def update_scheduled_query(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance