# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import webbrowser
from knack.util import CLIError
from knack.log import get_logger
from knack.prompting import prompt_y_n
from azext_codespaces import _non_arm_apis as cf_api
from .vendored_sdks.vsonline.models import VSOnlinePlan, VSOnlinePlanProperties

logger = get_logger(__name__)

CODESPACE_IN_BROWSER_PREFIX = "https://online.visualstudio.com/environment"


def _determine_codespace_id(client, resource_group_name, plan_name, token, codespace_name):
    plan = client.get(resource_group_name=resource_group_name, plan_name=plan_name)
    codespaces = cf_api.list_codespaces(token.access_token, plan.id)
    codespace_id = next((c['id'] for c in codespaces if c['friendlyName'] == codespace_name), None)
    if codespace_id:
        return codespace_id
    raise CLIError(f"Unable to find codespace '{codespace_name}' in plan {plan.id}")


# pylint: disable=unused-argument
def list_plans(cmd, client, resource_group_name=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()


def create_plan(cmd, client, resource_group_name, plan_name, location=None, tags=None):
    import jwt  # pylint: disable=import-error
    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cmd.cli_ctx)
    creds, _, __ = profile.get_raw_token()
    tokenType = creds[0]
    accessToken = creds[1]
    if tokenType != "Bearer":
        logger.debug("Got unexpected token type: %s", tokenType)
        raise CLIError("Unable to create plan. Use --debug for details.")
    decoded_token = jwt.decode(accessToken, verify=False, algorithms=['RS256'])
    tid = decoded_token.get('tid')
    oid = decoded_token.get('oid')
    if not tid or not oid:
        logger.debug("Unable to determine 'tid' and 'oid' from token claims: %s", decoded_token)
        raise CLIError("Unable to create plan. Use --debug for details.")
    user_id = f"{tid}_{oid}"
    plan_props = VSOnlinePlanProperties(user_id=user_id)
    vsonline_plan = VSOnlinePlan(location=location, properties=plan_props, tags=tags)
    return client.create(resource_group_name, plan_name, vsonline_plan)


def list_available_locations():
    return cf_api.list_locations()


def get_location_details(location_name):
    return cf_api.get_location_details(location_name)


# pylint: disable=unused-argument
def list_codespaces(cmd, client, plan_name, resource_group_name=None):
    plan = client.get(resource_group_name=resource_group_name, plan_name=plan_name)
    token = client.read_all_environments_action(resource_group_name=resource_group_name, plan_name=plan_name)
    return cf_api.list_codespaces(token.access_token, plan.id)


# pylint: disable=unused-argument
def create_codespace(cmd,
                     client,
                     plan_name,
                     friendly_name,
                     resource_group_name=None,
                     sku_name='standardLinux',
                     autoshutdown_delay=30,
                     git_repo=None,
                     git_user_name=None,
                     git_user_email=None,
                     dotfiles_repo=None,
                     dotfiles_path=None,
                     dotfiles_command=None):
    plan = client.get(resource_group_name=resource_group_name, plan_name=plan_name)
    token = client.write_environments_action(resource_group_name=resource_group_name, plan_name=plan_name)
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
    return cf_api.create_codespace(token.access_token, create_data)


# pylint: disable=unused-argument
def get_codespace(cmd, client, plan_name, resource_group_name=None, codespace_id=None, codespace_name=None):
    token = client.read_all_environments_action(resource_group_name=resource_group_name, plan_name=plan_name)
    if codespace_name:
        codespace_id = _determine_codespace_id(client, resource_group_name, plan_name, token, codespace_name)
    return cf_api.get_codespace(token.access_token, codespace_id)


# pylint: disable=unused-argument
def delete_codespace(cmd, client, plan_name, resource_group_name=None, codespace_id=None, codespace_name=None):
    token = client.write_environments_action(resource_group_name=resource_group_name, plan_name=plan_name)
    if codespace_name:
        codespace_id = _determine_codespace_id(client, resource_group_name, plan_name, token, codespace_name)
    cf_api.delete_codespace(token.access_token, codespace_id)


# pylint: disable=unused-argument
def resume_codespace(cmd, client, plan_name, resource_group_name=None, codespace_id=None, codespace_name=None):
    token = client.write_environments_action(resource_group_name=resource_group_name, plan_name=plan_name)
    if codespace_name:
        codespace_id = _determine_codespace_id(client, resource_group_name, plan_name, token, codespace_name)
    return cf_api.start_codespace(token.access_token, codespace_id)


# pylint: disable=unused-argument
def suspend_codespace(cmd, client, plan_name, resource_group_name=None, codespace_id=None, codespace_name=None):
    token = client.write_environments_action(resource_group_name=resource_group_name, plan_name=plan_name)
    if codespace_name:
        codespace_id = _determine_codespace_id(client, resource_group_name, plan_name, token, codespace_name)
    return cf_api.shutdown_codespace(token.access_token, codespace_id)


# pylint: disable=unused-argument
def open_codespace(cmd, client, plan_name, resource_group_name=None, codespace_id=None,
                   codespace_name=None, do_not_prompt=None):
    token = client.read_all_environments_action(resource_group_name=resource_group_name, plan_name=plan_name)
    if codespace_name:
        codespace_id = _determine_codespace_id(client, resource_group_name, plan_name, token, codespace_name)
    codespace = cf_api.get_codespace(token.access_token, codespace_id)
    if not do_not_prompt and codespace['state'] != 'Available':
        msg = f"Current state of the codespace is '{codespace['state']}'." \
            " Continuing will cause the environment to be resumed. Do you want to continue?"
        user_confirmed = prompt_y_n(msg)
        if not user_confirmed:
            raise CLIError("Operation cancelled.")
    url = f"{CODESPACE_IN_BROWSER_PREFIX}/{codespace['id']}"
    logger.warning("Opening: %s", url)
    success = webbrowser.open_new_tab(url)
    if not success:
        raise CLIError("Unable to open browser")
