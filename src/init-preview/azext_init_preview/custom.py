# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def create_init-preview(cmd, resource_group_name, init-preview_name, location=None, tags=None):
    raise CLIError('TODO: Implement `init-preview create`')


def list_init-preview(cmd, resource_group_name=None):
    raise CLIError('TODO: Implement `init-preview list`')


def update_init-preview(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance