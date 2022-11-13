# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.util import sdk_no_wait
from .vendored_sdks.appplatform.v2022_11_01_preview import models

DEFAULT_NAME = "default"

def customized_accelerator_list(cmd, client, resource_group, service):
    return client.customized_accelerators.list(resource_group, service, DEFAULT_NAME)


def customized_accelerator_show(cmd, client, resource_group, service, name):
    return client.customized_accelerators.get(resource_group, service, DEFAULT_NAME, name)


def customized_accelerator_upsert(cmd, client, resource_group, service, name,
                            display_name,
                            git_url,
                            description=None,
                            icon_url=None,
                            accelerator_tags=None,
                            git_interval_in_seconds=None,
                            git_branch=None,
                            git_commit=None,
                            git_tag=None,
                            username=None,
                            password=None,
                            private_key=None,
                            host_key=None,
                            host_key_algorithm=None,
                            no_wait=False):
    auth_setting=None
    if username and password:
        auth_setting = models.AcceleratorBasicAuthSetting(
            username=username,
            password=password
        )
    elif private_key and host_key and host_key_algorithm:
        auth_setting = models.AcceleratorSshSetting(
            private_key=private_key,
            host_key=host_key,
            host_key_algorithm=host_key_algorithm
        )
    else:
        auth_setting = models.AcceleratorPublicSetting(
        )
    git_repository = models.AcceleratorGitRepository(
        auth_setting=auth_setting,
        url=git_url,
        interval_in_seconds=git_interval_in_seconds,
        branch=git_branch,
        commit=git_commit,
        git_tag=git_tag
    )
    properties = models.CustomizedAcceleratorProperties(
        display_name=display_name,
        description=description,
        icon_url=icon_url,
        accelerator_tags=accelerator_tags,
        git_repository=git_repository
    )
    customized_accelerator_resource = models.CustomizedAcceleratorResource(properties=properties)
    return sdk_no_wait(no_wait, client.customized_accelerators.begin_create_or_update, resource_group, service, DEFAULT_NAME, name, customized_accelerator_resource)


def customized_accelerator_delete(cmd, client, resource_group, service, name, no_wait=False):
    return sdk_no_wait(no_wait, client.customized_accelerators.begin_delete, resource_group, service, DEFAULT_NAME, name)