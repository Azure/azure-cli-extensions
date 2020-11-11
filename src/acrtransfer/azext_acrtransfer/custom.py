# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def create_acrtransfer(cmd, client, resource_group_name, registry_name, location=None, tags=None):
    raise CLIError('TODO: Implement `acrtransfer create`')


def list_acrtransfer(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `acrtransfer list`')

def delete_acrtransfer(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `acrtransfer list`')

def get_acrtransfer(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `acrtransfer list`')

def update_acrtransfer(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance