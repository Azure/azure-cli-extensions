# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.util import sdk_no_wait
from knack.util import CLIError


# def create_compute-preview(cmd, resource_group_name, compute-preview_name, location=None, tags=None):
#     raise CLIError('TODO: Implement `compute-preview create`')
#
#
# def list_compute-preview(cmd, resource_group_name=None):
#     raise CLIError('TODO: Implement `compute-preview list`')
#
#
# def update_compute-preview(cmd, instance, tags=None):
#     with cmd.update_context(instance) as c:
#         c.set_param('tags', tags)
#     return instance


def create_publish(cmd, client, resource_group_name, shared_vm_extension_name, label=None, description=None,
                   company_name=None, eula=None, privacy=None, homepage=None, location=None, tags=None,
                   no_wait=False):
    body = {}
    if location is not None:
        body['location'] = location
    if tags is not None:
        body['tags'] = tags
    if label is not None:
        body['label'] = label
    if description is not None:
        body['description'] = description
    if company_name is not None:
        body['company_name'] = company_name
    if privacy is not None:
        body['privacy_uri'] = privacy
    if homepage is not None:
        body['homepage_uri'] = homepage
    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, shared_vm_extension_name, body)


def update_publish(instance, client, resource_group_name):
    return instance


def create_publish_version(cmd, client, resource_group_name, shared_vm_extension_name, shared_vm_extension_version_name,
                           location=None, tags=None, no_wait=False):
    body = {}
    if location is not None:
        body['location'] = location
    if tags is not None:
        body['tags'] = tags
    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name,shared_vm_extension_name,
                       shared_vm_extension_version_name, body)


def update_publish_version(instance, client, resource_group_name):
    return instance
