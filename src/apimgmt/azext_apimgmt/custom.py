# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def create_apimgmt(cmd, resource_group_name, apimgmt_name, location=None, tags=None):
    raise CLIError('TODO: Implement `apimgmt create`')


def list_apimgmt(cmd, resource_group_name=None):
    raise CLIError('TODO: Implement `apimgmt list`')


def update_apimgmt(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance