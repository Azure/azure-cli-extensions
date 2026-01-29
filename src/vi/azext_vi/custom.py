# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
import json
from rich import print_json

def create_vi(cmd, resource_group_name=None, vi_name=None, location=None, tags=None):
     raise CLIError('TODO: Implement `vi list`')


def list_cameras(client, resource_group_name=None):
    response = client.cameras.list(resource_group_name=resource_group_name)
    cameras = response.get('results')
    print_json(data=cameras)
#     return cameras


def list_vi(cmd, resource_group_name=None, vi_name=None, location=None, tags=None):
     raise CLIError('TODO: Implement `vi list`')


def show_vi(cmd, resource_group_name=None, vi_name=None, location=None, tags=None):
     raise CLIError('TODO: Implement `vi list`')


def troubleshoot_vi(cmd, resource_group_name=None, vi_name=None, location=None, tags=None):
     raise CLIError('TODO: Implement `vi list`')


def list_vi(cmd, resource_group_name=None):
    raise CLIError('TODO: Implement `vi list`')


def update_vi(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance