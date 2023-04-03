# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def create_centauri(cmd, resource_group_name, centauri_name, location=None, tags=None):
    raise CLIError('TODO: Implement `centauri create`')


def list_centauri(cmd, resource_group_name=None):
    raise CLIError('TODO: Implement `centauri list`')


def update_centauri(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance