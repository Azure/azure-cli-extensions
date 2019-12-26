# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def create_aladdin(cmd, resource_group_name, aladdin_name, location=None, tags=None):
    raise CLIError('TODO: Implement `aladdin create`')


def list_aladdin(cmd, resource_group_name=None):
    raise CLIError('TODO: Implement `aladdin list`')


def update_aladdin(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance