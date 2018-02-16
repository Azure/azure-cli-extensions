# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core._profile import Profile


def _register_rp(cli_ctx, subscription_id=None):
    rp = "Microsoft.Management"
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.cli.core.profiles import ResourceType
    import time
    rcf = get_mgmt_service_client(
        cli_ctx,
        ResourceType.MGMT_RESOURCE_RESOURCES,
        subscription_id)
    rcf.providers.register(rp)
    while True:
        time.sleep(10)
        rp_info = rcf.providers.get(rp)
        if rp_info.registration_state == 'Registered':
            break


def _get_subscription_id_from_subscription(cli_ctx, subscription):  # pylint: disable=inconsistent-return-statements
    profile = Profile(cli_ctx=cli_ctx)
    subscriptions_list = profile.load_cached_subscriptions()
    for sub in subscriptions_list:
        if sub['id'] == subscription or sub['name'] == subscription:
            return sub['id']
    from azure.cli.core.util import CLIError
    raise CLIError("Subscription not found in the current context.")


def cli_managementgroups_group_list(cmd, client):
    _register_rp(cmd.cli_ctx)
    return client.list()


def cli_managementgroups_group_show(
        cmd,
        client,
        group_name,
        expand=False,
        recurse=False):
    _register_rp(cmd.cli_ctx)
    if expand:
        return client.get(group_name, "children", recurse)
    return client.get(group_name)


def cli_managementgroups_group_create(
        cmd,
        client,
        group_name,
        display_name=None,
        parent_id=None):
    _register_rp(cmd.cli_ctx)
    return client.create_or_update(
        group_name, "no-cache", display_name, parent_id)


def cli_managementgroups_group_update_custom_func(
        instance,
        display_name=None,
        parent_id=None):
    instance["display_name"] = display_name
    instance["parent_id"] = parent_id
    return instance


def cli_managementgroups_group_update_get():
    update_parameters = {'display_name': None, 'parent_id': None}
    return update_parameters


def cli_managementgroups_group_update_set(
        cmd, client, group_name, parameters=None):
    _register_rp(cmd.cli_ctx)
    return client.update(
        group_name,
        "no_cache",
        parameters["display_name"],
        parameters["parent_id"])


def cli_managementgroups_group_delete(cmd, client, group_name):
    _register_rp(cmd.cli_ctx)
    return client.delete(group_name)


def cli_managementgroups_subscription_add(
        cmd, client, group_name, subscription):
    subscription_id = _get_subscription_id_from_subscription(
        cmd.cli_ctx, subscription)
    _register_rp(cmd.cli_ctx)
    _register_rp(cmd.cli_ctx, subscription_id)
    return client.create(group_name, subscription_id)


def cli_managementgroups_subscription_remove(
        cmd, client, group_name, subscription):
    subscription_id = _get_subscription_id_from_subscription(
        cmd.cli_ctx, subscription)
    _register_rp(cmd.cli_ctx)
    _register_rp(cmd.cli_ctx, subscription_id)
    return client.delete(group_name, subscription_id)
