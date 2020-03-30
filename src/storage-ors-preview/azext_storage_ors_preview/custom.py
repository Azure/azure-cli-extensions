# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def create_storage-ors-preview(cmd, resource_group_name, storage-ors-preview_name, location=None, tags=None):
    raise CLIError('TODO: Implement `storage-ors-preview create`')


def list_storage-ors-preview(cmd, resource_group_name=None):
    raise CLIError('TODO: Implement `storage-ors-preview list`')


def update_storage-ors-preview(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance