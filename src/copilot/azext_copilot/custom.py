# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def create_copilot(cmd, resource_group_name, copilot_name, location=None, tags=None):
    raise CLIError('TODO: Implement `copilot create`')


def list_copilot(cmd, resource_group_name=None):
    raise CLIError('TODO: Implement `copilot list`')


def update_copilot(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance