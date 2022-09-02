# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def create_nginx(cmd, resource_group_name, nginx_name, location=None, tags=None):
    raise CLIError('TODO: Implement `nginx create`')


def list_nginx(cmd, resource_group_name=None):
    raise CLIError('TODO: Implement `nginx list`')


def update_nginx(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance