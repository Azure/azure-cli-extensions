# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.util import sdk_no_wait
from knack.log import get_logger
from azure.cli.core.commands.client_factory import get_subscription_id
from .vendored_sdks.appplatform.v2024_05_01_preview import models
from .dev_tool_portal import (is_updatable as is_dev_tool_portal_updatable,
                              try_get as get_dev_tool_portal,
                              create_or_update as create_or_update_dev_tool_portal,
                              _get_desired_state as get_dev_tool_portal_desired_state)
from ._utils import (wait_till_end)
from .vendored_sdks.appplatform.v2024_05_01_preview.models._app_platform_management_client_enums import (CustomizedAcceleratorType)

DEFAULT_NAME = "default"
logger = get_logger(__name__)


def application_accelerator_show(cmd, client, resource_group, service):
    return client.application_accelerators.get(resource_group, service, DEFAULT_NAME)


def application_accelerator_create(cmd, client, resource_group, service, no_wait=False):
    properties = models.ApplicationAcceleratorProperties(
    )
    application_accelerator_resource = models.ApplicationAcceleratorResource(properties=properties)
    poller = client.application_accelerators.begin_create_or_update(resource_group, service, DEFAULT_NAME, application_accelerator_resource)
    dev_tool_portal_poller = _get_enable_dev_tool_portal_poller(cmd, client, service, resource_group)
    pollers = [x for x in [poller, dev_tool_portal_poller] if x is not None]
    if not no_wait:
        wait_till_end(cmd, *pollers)
    return poller


def application_accelerator_delete(cmd, client, resource_group, service, no_wait=False):
    poller = client.application_accelerators.begin_delete(resource_group, service, DEFAULT_NAME)
    dev_tool_portal_poller = _get_disable_dev_tool_portal_poller(cmd, client, service, resource_group)
    pollers = [x for x in [poller, dev_tool_portal_poller] if x is not None]
    if not no_wait:
        wait_till_end(cmd, *pollers)
    return poller


def _get_enable_dev_tool_portal_poller(cmd, client, service, resource_group):
    dev_tool_portal = get_dev_tool_portal(cmd, client, service, resource_group)
    if not dev_tool_portal:
        logger.warning('- View Application Accelerator through Dev Tool portal. '
                       'Create Dev Tool Portal by running '
                       '"az spring dev-tool create --service {} --resource-group {} --assign-endpoint"'
                       .format(service, resource_group))
        return None
    if not is_dev_tool_portal_updatable(dev_tool_portal):
        return None
    return _get_update_dev_tool_portal_poller(cmd, client, service, resource_group,
                                              dev_tool_portal, True)


def _get_disable_dev_tool_portal_poller(cmd, client, service, resource_group):
    dev_tool_portal = get_dev_tool_portal(cmd, client, service, resource_group)
    if not dev_tool_portal or not is_dev_tool_portal_updatable(dev_tool_portal):
        return None
    return _get_update_dev_tool_portal_poller(cmd, client, service, resource_group,
                                              dev_tool_portal, False)


def _get_update_dev_tool_portal_poller(cmd, client, service, resource_group, dev_tool_portal,
                                       enable_application_accelerator):
    desired_state = get_dev_tool_portal_desired_state(enable_application_accelerator)
    if dev_tool_portal.properties.features.application_accelerator.state == desired_state:
        return None
    return create_or_update_dev_tool_portal(cmd, client, service, resource_group, dev_tool_portal,
                                            enable_application_accelerator=enable_application_accelerator)


def customized_accelerator_list(cmd, client, resource_group, service):
    return client.customized_accelerators.list(resource_group, service, DEFAULT_NAME)


def customized_accelerator_show(cmd, client, resource_group, service, name):
    return client.customized_accelerators.get(resource_group, service, DEFAULT_NAME, name)


def customized_accelerator_sync_cert(cmd, client, resource_group, service, name, no_wait=False):
    customized_accelerator_resource = client.customized_accelerators.get(resource_group, service, DEFAULT_NAME, name)
    return sdk_no_wait(no_wait, client.customized_accelerators.begin_create_or_update, resource_group, service, DEFAULT_NAME, name, customized_accelerator_resource)


def customized_accelerator_upsert(cmd, client, resource_group, service, name,
                                  display_name,
                                  git_url,
                                  description=None,
                                  type=None,
                                  icon_url=None,
                                  accelerator_tags=None,
                                  git_interval=None,
                                  git_branch=None,
                                  git_commit=None,
                                  git_tag=None,
                                  git_sub_path=None,
                                  ca_cert_name=None,
                                  username=None,
                                  password=None,
                                  private_key=None,
                                  host_key=None,
                                  host_key_algorithm=None,
                                  no_wait=False):
    auth_setting = None

    if type is None:
        type = CustomizedAcceleratorType.ACCELERATOR

    caCertResourceId = None
    if ca_cert_name:
        subscription = get_subscription_id(cmd.cli_ctx)
        caCertResourceId = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.AppPlatform/Spring/{}/certificates/{}".format(subscription, resource_group, service, ca_cert_name)

    if username and password:
        auth_setting = models.AcceleratorBasicAuthSetting(
            ca_cert_resource_id=caCertResourceId,
            username=username,
            password=password
        )
    elif private_key and host_key and host_key_algorithm:
        auth_setting = models.AcceleratorSshSetting(
            private_key=private_key.replace('\\n', '\n'),
            host_key=host_key,
            host_key_algorithm=host_key_algorithm
        )
    else:
        auth_setting = models.AcceleratorPublicSetting(
            ca_cert_resource_id=caCertResourceId
        )
    git_repository = models.AcceleratorGitRepository(
        auth_setting=auth_setting,
        url=git_url,
        interval_in_seconds=git_interval,
        branch=git_branch,
        commit=git_commit,
        git_tag=git_tag,
        sub_path=git_sub_path,
    )
    properties = models.CustomizedAcceleratorProperties(
        display_name=display_name,
        description=description,
        icon_url=icon_url,
        accelerator_tags=accelerator_tags,
        accelerator_type=type,
        git_repository=git_repository
    )
    customized_accelerator_resource = models.CustomizedAcceleratorResource(properties=properties)
    return sdk_no_wait(no_wait, client.customized_accelerators.begin_create_or_update, resource_group, service, DEFAULT_NAME, name, customized_accelerator_resource)


def customized_accelerator_delete(cmd, client, resource_group, service, name, no_wait=False):
    return sdk_no_wait(no_wait, client.customized_accelerators.begin_delete, resource_group, service, DEFAULT_NAME, name)


def predefined_accelerator_list(cmd, client, resource_group, service):
    return client.predefined_accelerators.list(resource_group, service, DEFAULT_NAME)


def predefined_accelerator_show(cmd, client, resource_group, service, name):
    return client.predefined_accelerators.get(resource_group, service, DEFAULT_NAME, name)


def predefined_accelerator_disable(cmd, client, resource_group, service, name, no_wait=False):
    return sdk_no_wait(no_wait, client.predefined_accelerators.begin_disable, resource_group, service, DEFAULT_NAME, name)


def predefined_accelerator_enable(cmd, client, resource_group, service, name, no_wait=False):
    return sdk_no_wait(no_wait, client.predefined_accelerators.begin_enable, resource_group, service, DEFAULT_NAME, name)
