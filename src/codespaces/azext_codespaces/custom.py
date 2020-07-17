# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import webbrowser
from knack.util import CLIError
from knack.log import get_logger
from knack.prompting import prompt_y_n
from . import _non_arm_apis as cs_api
from . import _config as cs_config
from .vendored_sdks.codespaces.models import (
    CodespacesPlan,
    CodespacesPlanProperties,
    VnetProperties,
    CodespacesPlanUpdateParametersProperties)

logger = get_logger(__name__)


def _determine_codespace_id(client, resource_group_name, plan_name, token, codespace_name, cli_ctx=None):
    if not cli_ctx:
        raise ValueError("cli_ctx kwarg must be set.")
    plan = client.get(resource_group_name=resource_group_name, plan_name=plan_name)
    codespaces = cs_api.list_codespaces(token.access_token, plan.id, cli_ctx=cli_ctx)
    codespace_id = next((c['id'] for c in codespaces if c['friendlyName'] == codespace_name), None)
    if codespace_id:
        return codespace_id
    raise CLIError(f"Unable to find codespace '{codespace_name}' in plan {plan.id}")


# pylint: disable=unused-argument
def list_plans(cmd, client, resource_group_name=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()


def create_plan(cmd,
                client,
                resource_group_name,
                plan_name,
                location=None,
                tags=None,
                subnet_id=None,
                default_sku_name=None,
                default_autoshutdown_delay=None):
    vnet_props = VnetProperties(subnet_id=subnet_id) if subnet_id else None
    plan_props = CodespacesPlanProperties(
        default_auto_suspend_delay_minutes=default_autoshutdown_delay,
        default_codespace_sku=default_sku_name,
        vnet_properties=vnet_props)
    codespaces_plan = CodespacesPlan(location=location, properties=plan_props, tags=tags)
    return client.create(resource_group_name, plan_name, codespaces_plan)


def update_plan(cmd,
                client,
                plan_name,
                resource_group_name=None,
                default_sku_name=None,
                default_autoshutdown_delay=None):
    codespaces_plan_update_parameters = CodespacesPlanUpdateParametersProperties(
        default_auto_suspend_delay_minutes=default_autoshutdown_delay,
        default_codespace_sku=default_sku_name)
    return client.update(resource_group_name,
                         plan_name,
                         codespaces_plan_update_parameters)


def list_available_locations(cmd):
    return cs_api.list_locations(cli_ctx=cmd.cli_ctx)


def get_location_details(cmd, location_name):
    return cs_api.get_location_details(location_name, cli_ctx=cmd.cli_ctx)


def list_codespaces(cmd, client, plan_name, resource_group_name=None, list_all=None):
    plan = client.get(resource_group_name=resource_group_name, plan_name=plan_name)
    if list_all:
        token = client.read_all_codespaces_action(resource_group_name=resource_group_name, plan_name=plan_name)
    else:
        token = client.write_codespaces_action(resource_group_name=resource_group_name, plan_name=plan_name)
    return cs_api.list_codespaces(token.access_token, plan.id, cli_ctx=cmd.cli_ctx)


def create_codespace(cmd,
                     client,
                     plan_name,
                     friendly_name,
                     resource_group_name=None,
                     sku_name=None,
                     autoshutdown_delay=None,
                     git_repo=None,
                     git_user_name=None,
                     git_user_email=None,
                     dotfiles_repo=None,
                     dotfiles_path=None,
                     dotfiles_command=None):
    plan = client.get(resource_group_name=resource_group_name, plan_name=plan_name)
    token = client.write_codespaces_action(resource_group_name=resource_group_name, plan_name=plan_name)
    # Use plan defaults if needed and available
    missing_args = []
    sku_name = sku_name or plan.properties.default_codespace_sku
    if not sku_name:
        logger.warning("No default instance type specified for plan and no instance type specified in command.")
        missing_args.append("--instance-type")
    autoshutdown_delay = autoshutdown_delay or plan.properties.default_auto_suspend_delay_minutes
    if not autoshutdown_delay:
        logger.warning("No default shutdown delay specified for plan and no shutdown delay specified in command.")
        missing_args.append("--suspend-after")
    if missing_args:
        raise CLIError(f"usage error: please specify {' '.join(missing_args)}")
    # Construct create parameters
    create_data = {}
    create_data['planId'] = plan.id
    create_data['friendlyName'] = friendly_name
    create_data['autoShutdownDelayMinutes'] = autoshutdown_delay
    create_data['type'] = "cloudEnvironment"
    create_data['experimentalFeatures'] = {'customContainers': True}
    create_data["skuName"] = sku_name
    if git_repo:
        if not git_user_name or not git_user_email:
            raise CLIError("usage error: must specify --git-user-name --git-user-email")
        create_data["seed"] = {
            "type": "git",
            "moniker": git_repo,
            "gitConfig": {"userName": git_user_name, "userEmail": git_user_email}
        }
    if dotfiles_repo:
        create_data["personalization"] = {"dotfilesRepository": dotfiles_repo}
        if dotfiles_path:
            create_data["personalization"]["dotfilesTargetPath"] = dotfiles_path
        if dotfiles_command:
            create_data["personalization"]["dotfilesInstallCommand"] = dotfiles_command
    # Create codespace
    return cs_api.create_codespace(token.access_token, create_data, cli_ctx=cmd.cli_ctx)


def get_codespace(cmd, client, plan_name, resource_group_name=None, codespace_id=None, codespace_name=None):
    token = client.write_codespaces_action(resource_group_name=resource_group_name, plan_name=plan_name)
    if codespace_name:
        codespace_id = _determine_codespace_id(
            client, resource_group_name, plan_name, token, codespace_name, cli_ctx=cmd.cli_ctx)
    return cs_api.get_codespace(token.access_token, codespace_id, cli_ctx=cmd.cli_ctx)


def delete_codespace(cmd, client, plan_name, resource_group_name=None, codespace_id=None, codespace_name=None):
    token = client.write_codespaces_action(resource_group_name=resource_group_name, plan_name=plan_name)
    if codespace_name:
        codespace_id = _determine_codespace_id(
            client, resource_group_name, plan_name, token, codespace_name, cli_ctx=cmd.cli_ctx)
    cs_api.delete_codespace(token.access_token, codespace_id, cli_ctx=cmd.cli_ctx)


def resume_codespace(cmd, client, plan_name, resource_group_name=None, codespace_id=None, codespace_name=None):
    token = client.write_codespaces_action(resource_group_name=resource_group_name, plan_name=plan_name)
    if codespace_name:
        codespace_id = _determine_codespace_id(
            client, resource_group_name, plan_name, token, codespace_name, cli_ctx=cmd.cli_ctx)
    return cs_api.start_codespace(token.access_token, codespace_id, cli_ctx=cmd.cli_ctx)


def suspend_codespace(cmd, client, plan_name, resource_group_name=None, codespace_id=None, codespace_name=None):
    token = client.write_codespaces_action(resource_group_name=resource_group_name, plan_name=plan_name)
    if codespace_name:
        codespace_id = _determine_codespace_id(
            client, resource_group_name, plan_name, token, codespace_name, cli_ctx=cmd.cli_ctx)
    return cs_api.shutdown_codespace(token.access_token, codespace_id, cli_ctx=cmd.cli_ctx)


def update_codespace(cmd,
                     client,
                     plan_name,
                     resource_group_name=None,
                     codespace_id=None,
                     codespace_name=None,
                     sku_name=None,
                     autoshutdown_delay=None):
    token = client.write_codespaces_action(resource_group_name=resource_group_name, plan_name=plan_name)
    if codespace_name:
        codespace_id = _determine_codespace_id(
            client, resource_group_name, plan_name, token, codespace_name, cli_ctx=cmd.cli_ctx)
    data = {}
    codespace = cs_api.get_codespace(token.access_token, codespace_id, cli_ctx=cmd.cli_ctx)
    if codespace['state'] != 'Shutdown':
        raise CLIError("Codespace must be in state 'Shutdown'. "
                       f"Cannot update a Codespace in state '{codespace['state']}'.")
    if sku_name:
        data['skuName'] = sku_name
    if autoshutdown_delay:
        data['autoShutdownDelayMinutes'] = autoshutdown_delay
    return cs_api.update_codespace(token.access_token, codespace_id, data, cli_ctx=cmd.cli_ctx)


def open_codespace(cmd, client, plan_name, resource_group_name=None, codespace_id=None,
                   codespace_name=None, do_not_prompt=None):
    token = client.write_codespaces_action(resource_group_name=resource_group_name, plan_name=plan_name)
    if codespace_name:
        codespace_id = _determine_codespace_id(
            client, resource_group_name, plan_name, token, codespace_name, cli_ctx=cmd.cli_ctx)
    codespace = cs_api.get_codespace(token.access_token, codespace_id, cli_ctx=cmd.cli_ctx)
    if not do_not_prompt and codespace['state'] != 'Available':
        msg = f"Current state of the codespace is '{codespace['state']}'." \
            " Continuing will cause the environment to be resumed.\nDo you want to continue?"
        user_confirmed = prompt_y_n(msg)
        if not user_confirmed:
            raise CLIError("Operation cancelled.")
    domain = cs_config.get_service_domain(cmd.cli_ctx)
    url = f"https://{domain}/environment/{codespace['id']}"
    logger.warning("Opening: %s", url)
    success = webbrowser.open_new_tab(url)
    if not success:
        raise CLIError("Unable to open browser")


def set_config(cmd, config_rp_api_version='', config_service_domain='', config_clear=False):
    if config_clear and any([config_rp_api_version, config_service_domain]):
        raise CLIError("If you wish to clear config, do not specify other values.")
    cs_config.set_rp_api_version(cmd.cli_ctx, config_rp_api_version)
    cs_config.set_service_domain(cmd.cli_ctx, config_service_domain)


def show_config(cmd):
    return cs_config.get_current_config(cmd.cli_ctx)


def list_plan_secrets(cmd, client, plan_name, resource_group_name=None):
    plan = client.get(resource_group_name=resource_group_name, plan_name=plan_name)
    token = client.write_codespaces_action(resource_group_name=resource_group_name, plan_name=plan_name)
    return cs_api.list_secrets(token.access_token, plan.id, cli_ctx=cmd.cli_ctx)


def update_plan_secrets(cmd, client, plan_name, secret_id,
                        secret_name=None, secret_value=None, secret_note=None,
                        secret_filters=None, resource_group_name=None):
    plan = client.get(resource_group_name=resource_group_name, plan_name=plan_name)
    token = client.write_codespaces_action(resource_group_name=resource_group_name, plan_name=plan_name)
    data = {}
    data['secretName'] = secret_name
    data['value'] = secret_value
    data['notes'] = secret_note
    data['scope'] = cs_api.SecretScope.USER.value
    data['filters'] = secret_filters
    return cs_api.update_secret(token.access_token, plan.id, secret_id, data, cli_ctx=cmd.cli_ctx)


def create_plan_secret(cmd, client, plan_name,
                       secret_name, secret_value, secret_note=None,
                       secret_filters=None, resource_group_name=None):
    plan = client.get(resource_group_name=resource_group_name, plan_name=plan_name)
    token = client.write_codespaces_action(resource_group_name=resource_group_name, plan_name=plan_name)
    data = {}
    data['secretName'] = secret_name
    data['value'] = secret_value
    data['notes'] = secret_note
    data['type'] = cs_api.SecretType.ENVIRONMENT_VARIABLE.value
    data['scope'] = cs_api.SecretScope.USER.value
    data['filters'] = secret_filters
    return cs_api.create_secret(token.access_token, plan.id, data, cli_ctx=cmd.cli_ctx)


def delete_plan_secret(cmd, client, plan_name, secret_id, resource_group_name=None):
    plan = client.get(resource_group_name=resource_group_name, plan_name=plan_name)
    token = client.write_codespaces_action(resource_group_name=resource_group_name, plan_name=plan_name)
    cs_api.delete_secret(token.access_token, plan.id, secret_id, cs_api.SecretScope.USER.value, cli_ctx=cmd.cli_ctx)
