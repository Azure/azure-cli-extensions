# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def create_containerapp(cmd, resource_group_name, containerapp_name, location=None, tags=None):
    raise CLIError('TODO: Implement `containerapp create`')


def list_containerapp(cmd, resource_group_name=None):
    raise CLIError('TODO: Implement `containerapp list`')


def update_containerapp(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance