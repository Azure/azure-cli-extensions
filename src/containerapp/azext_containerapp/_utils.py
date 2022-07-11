# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, consider-using-f-string, no-else-return, duplicate-string-formatting-argument, expression-not-assigned, too-many-locals, logging-fstring-interpolation

import time
import json
import platform

from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from azure.cli.core.azclierror import (ValidationError, RequiredArgumentMissingError, CLIInternalError,
                                       ResourceNotFoundError, FileOperationError, CLIError)
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.command_modules.appservice.utils import _normalize_location
from azure.cli.command_modules.network._client_factory import network_client_factory

from knack.log import get_logger
from msrestazure.tools import parse_resource_id, is_valid_resource_id, resource_id

from ._clients import ContainerAppClient, ManagedEnvironmentClient
from ._client_factory import handle_raw_exception, providers_client_factory, cf_resource_groups, log_analytics_client_factory, log_analytics_shared_key_client_factory
from ._constants import (MAXIMUM_CONTAINER_APP_NAME_LENGTH, SHORT_POLLING_INTERVAL_SECS, LONG_POLLING_INTERVAL_SECS,
                         LOG_ANALYTICS_RP, CONTAINER_APPS_RP, CHECK_CERTIFICATE_NAME_AVAILABILITY_TYPE, ACR_IMAGE_SUFFIX)
from ._models import (ContainerAppCustomDomainEnvelope as ContainerAppCustomDomainEnvelopeModel)

logger = get_logger(__name__)


def register_provider_if_needed(cmd, rp_name):
    if not _is_resource_provider_registered(cmd, rp_name):
        _register_resource_provider(cmd, rp_name)


def validate_container_app_name(name):
    if name and len(name) > MAXIMUM_CONTAINER_APP_NAME_LENGTH:
        raise ValidationError(f"Container App names cannot be longer than {MAXIMUM_CONTAINER_APP_NAME_LENGTH}. "
                              f"Please shorten {name}")


def retry_until_success(operation, err_txt, retry_limit, *args, **kwargs):
    while True:
        try:
            return operation(*args, **kwargs)
        except Exception as e:
            retry_limit -= 1
            if retry_limit <= 0:
                raise CLIInternalError(err_txt) from e
            time.sleep(5)
            logger.info(f"Encountered error: {e}. Retrying...")


def get_vnet_location(cmd, subnet_resource_id):
    parsed_rid = parse_resource_id(subnet_resource_id)
    vnet_client = network_client_factory(cmd.cli_ctx)
    location = vnet_client.virtual_networks.get(resource_group_name=parsed_rid.get("resource_group"),
                                                virtual_network_name=parsed_rid.get("name")).location
    return _normalize_location(cmd, location)


def _create_application(client, display_name):
    from azure.cli.command_modules.role.custom import GraphError
    body = {"displayName": display_name, "keyCredentials": []}

    try:
        result = client.application_create(body)
    except GraphError as ex:
        if 'insufficient privileges' in str(ex).lower():
            link = 'https://docs.microsoft.com/azure/azure-resource-manager/resource-group-create-service-principal-portal'  # pylint: disable=line-too-long
            raise ValidationError("Directory permission is needed for the current user to register the application. "
                                  "For how to configure, please refer '{}'. Original error: {}".format(link, ex)) from ex
        raise
    return result


def _create_service_principal(client, app_id):
    return client.service_principal_create({"appId": app_id, "accountEnabled": True})


def _create_role_assignment(cli_ctx, role, assignee, scope=None):
    import uuid
    from azure.cli.core.profiles import ResourceType, get_sdk, supported_api_version
    from azure.cli.core.commands.client_factory import get_mgmt_service_client

    auth_client = get_mgmt_service_client(cli_ctx, ResourceType.MGMT_AUTHORIZATION)
    assignments_client = auth_client.role_assignments
    definitions_client = auth_client.role_definitions

    assignment_name = uuid.uuid4()
    role_defs = list(definitions_client.list(scope, "roleName eq '{}'".format(role)))
    role_id = role_defs[0].id

    api_version = supported_api_version(cli_ctx, resource_type=ResourceType.MGMT_AUTHORIZATION, max_api='2015-07-01')
    RoleAssignmentCreateParameters = get_sdk(cli_ctx, ResourceType.MGMT_AUTHORIZATION,
                                             'RoleAssignmentProperties' if api_version else 'RoleAssignmentCreateParameters',
                                             mod='models', operation_group='role_assignments')
    parameters = RoleAssignmentCreateParameters(role_definition_id=role_id, principal_id=assignee)
    parameters.principal_type = "ServicePrincipal"
    return assignments_client.create(scope, assignment_name, parameters)


def create_service_principal_for_github_action(cmd, scopes=None, role="contributor"):
    from azure.cli.command_modules.role import graph_client_factory

    SP_CREATION_ERR_TXT = "Failed to create service principal."
    RETRY_LIMIT = 36

    client = graph_client_factory(cmd.cli_ctx)
    now = datetime.utcnow()
    app_display_name = 'azure-cli-' + now.strftime('%Y-%m-%d-%H-%M-%S')
    app = retry_until_success(_create_application, SP_CREATION_ERR_TXT, RETRY_LIMIT, client, display_name=app_display_name)
    sp = retry_until_success(_create_service_principal, SP_CREATION_ERR_TXT, RETRY_LIMIT, client, app_id=app["appId"])
    for scope in scopes:
        retry_until_success(_create_role_assignment, SP_CREATION_ERR_TXT, RETRY_LIMIT, cmd.cli_ctx, role=role, assignee=sp["id"], scope=scope)
    service_principal = retry_until_success(client.service_principal_get, SP_CREATION_ERR_TXT, RETRY_LIMIT, sp["id"])

    body = {
        "passwordCredential": {
            "displayName": None,
            "startDateTime": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "endDateTime": (now + relativedelta(years=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        }
    }
    add_password_result = retry_until_success(client.service_principal_add_password, SP_CREATION_ERR_TXT, RETRY_LIMIT, service_principal["id"], body)

    return {
        'appId': service_principal['appId'],
        'password': add_password_result['secretText'],
        'tenant': client.tenant
    }


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        pass
    return False


def get_github_repo(token, repo):
    from github import Github

    g = Github(token)
    return g.get_repo(repo)


def get_workflow(github_repo, name):  # pylint: disable=inconsistent-return-statements
    workflows = list(github_repo.get_workflows())
    workflows.sort(key=lambda r: r.created_at, reverse=True)  # sort by latest first
    for wf in workflows:
        if wf.path.startswith(f".github/workflows/{name}") and "Trigger auto deployment for" in wf.name:
            return wf


def trigger_workflow(token, repo, name, branch):
    wf = get_workflow(get_github_repo(token, repo), name)
    logger.warning(f"Triggering Github Action: {wf.path}")
    wf.create_dispatch(branch)


# pylint:disable=unused-argument
def await_github_action(cmd, token, repo, branch, name, resource_group_name, timeout_secs=1200):
    from .custom import show_github_action
    from ._clients import PollingAnimation

    start = datetime.utcnow()
    animation = PollingAnimation()
    animation.tick()

    github_repo = get_github_repo(token, repo)

    gh_action_status = "InProgress"
    while gh_action_status == "InProgress":
        time.sleep(SHORT_POLLING_INTERVAL_SECS)
        animation.tick()
        gh_action_status = safe_get(show_github_action(cmd, name, resource_group_name), "properties", "operationState")
        if (datetime.utcnow() - start).seconds >= timeout_secs:
            raise CLIInternalError("Timed out while waiting for the Github action to be created.")
        animation.flush()
    if gh_action_status == "Failed":
        raise CLIInternalError("The Github Action creation failed.")  # TODO ask backend team for a status url / message

    workflow = None
    while workflow is None:
        animation.tick()
        time.sleep(SHORT_POLLING_INTERVAL_SECS)
        workflow = get_workflow(github_repo, name)
        animation.flush()

        if (datetime.utcnow() - start).seconds >= timeout_secs:
            raise CLIInternalError("Timed out while waiting for the Github action to start.")

    runs = workflow.get_runs()
    while runs is None or not [r for r in runs if r.status in ('queued', 'in_progress')]:
        time.sleep(SHORT_POLLING_INTERVAL_SECS)
        runs = workflow.get_runs()
        if (datetime.utcnow() - start).seconds >= timeout_secs:
            raise CLIInternalError("Timed out while waiting for the Github action to be started.")
    runs = [r for r in runs if r.status in ('queued', 'in_progress')]
    runs.sort(key=lambda r: r.created_at, reverse=True)
    run = runs[0]  # run with the latest created_at date that's either in progress or queued
    logger.warning(f"Github action run: https://github.com/{repo}/actions/runs/{run.id}")
    logger.warning("Waiting for deployment to complete...")
    run_id = run.id
    status = run.status
    while status in ('queued', 'in_progress'):
        time.sleep(LONG_POLLING_INTERVAL_SECS)
        animation.tick()
        status = github_repo.get_workflow_run(run_id).status
        animation.flush()
        if (datetime.utcnow() - start).seconds >= timeout_secs:
            raise CLIInternalError("Timed out while waiting for the Github action to complete.")

    animation.flush()  # needed to clear the animation from the terminal
    run = github_repo.get_workflow_run(run_id)
    if run.status != "completed" or run.conclusion != "success":
        raise ValidationError("Github action build or deployment failed. "
                              f"Please see https://github.com/{repo}/actions/runs/{run.id} for more details")


def repo_url_to_name(repo_url):
    repo = None
    repo = [s for s in repo_url.split('/') if s]
    if len(repo) >= 2:
        repo = '/'.join(repo[-2:])
    return repo


def _get_location_from_resource_group(cli_ctx, resource_group_name):
    client = cf_resource_groups(cli_ctx)
    group = client.get(resource_group_name)
    return group.location


def _register_resource_provider(cmd, resource_provider):
    from azure.mgmt.resource.resources.models import ProviderRegistrationRequest, ProviderConsentDefinition

    logger.warning(f"Registering resource provider {resource_provider} ...")
    properties = ProviderRegistrationRequest(third_party_provider_consent=ProviderConsentDefinition(consent_to_authorization=True))

    client = providers_client_factory(cmd.cli_ctx)
    try:
        client.register(resource_provider, properties=properties)
        # wait for registration to finish
        timeout_secs = 120
        registration = _is_resource_provider_registered(cmd, resource_provider)
        start = datetime.utcnow()
        while not registration:
            registration = _is_resource_provider_registered(cmd, resource_provider)
            time.sleep(SHORT_POLLING_INTERVAL_SECS)
            if (datetime.utcnow() - start).seconds >= timeout_secs:
                raise CLIInternalError(f"Timed out while waiting for the {resource_provider} resource provider to be registered.")

    except Exception as e:
        msg = ("This operation requires requires registering the resource provider {0}. "
               "We were unable to perform that registration on your behalf: "
               "Server responded with error message -- {1} . "
               "Please check with your admin on permissions, "
               "or try running registration manually with: az provider register --wait --namespace {0}")
        raise ValidationError(resource_provider, msg.format(e.args)) from e


def _is_resource_provider_registered(cmd, resource_provider, subscription_id=None):
    registered = None
    if not subscription_id:
        subscription_id = get_subscription_id(cmd.cli_ctx)
    try:
        providers_client = providers_client_factory(cmd.cli_ctx, subscription_id)
        registration_state = getattr(providers_client.get(resource_provider), 'registration_state', "NotRegistered")

        registered = (registration_state and registration_state.lower() == 'registered')
    except Exception:  # pylint: disable=broad-except
        pass
    return registered


def _validate_subscription_registered(cmd, resource_provider, subscription_id=None):
    if not subscription_id:
        subscription_id = get_subscription_id(cmd.cli_ctx)
    registered = _is_resource_provider_registered(cmd, resource_provider, subscription_id)
    if registered is False:
        raise ValidationError(f'Subscription {subscription_id} is not registered for the {resource_provider} '
                              f'resource provider. Please run "az provider register -n {resource_provider} --wait" '
                              'to register your subscription.')


def _ensure_location_allowed(cmd, location, resource_provider, resource_type):
    providers_client = None
    try:
        providers_client = providers_client_factory(cmd.cli_ctx, get_subscription_id(cmd.cli_ctx))
    except Exception as ex:
        handle_raw_exception(ex)

    if providers_client is not None:
        try:
            resource_types = getattr(providers_client.get(resource_provider), 'resource_types', [])
        except Exception as ex:
            handle_raw_exception(ex)

        res_locations = []
        for res in resource_types:
            if res and getattr(res, 'resource_type', "") == resource_type:
                res_locations = getattr(res, 'locations', [])

        res_locations = [res_loc.lower().replace(" ", "").replace("(", "").replace(")", "") for res_loc in res_locations if res_loc.strip()]

        location_formatted = location.lower().replace(" ", "")
        if location_formatted not in res_locations:
            raise ValidationError(f"Location '{location}' is not currently supported. To get list of supported locations, run `az provider show -n {resource_provider} --query \"resourceTypes[?resourceType=='{resource_type}'].locations\"`")


def parse_env_var_flags(env_list, is_update_containerapp=False):
    env_pairs = {}

    for pair in env_list:
        key_val = pair.split('=', 1)
        if len(key_val) != 2:
            if is_update_containerapp:
                raise ValidationError("Environment variables must be in the format \"<key>=<value> <key>=secretref:<value> ...\".")
            raise ValidationError("Environment variables must be in the format \"<key>=<value> <key>=secretref:<value> ...\".")
        if key_val[0] in env_pairs:
            raise ValidationError("Duplicate environment variable {env} found, environment variable names must be unique.".format(env=key_val[0]))
        value = key_val[1].split('secretref:')
        env_pairs[key_val[0]] = value

    env_var_def = []
    for key, value in env_pairs.items():
        if len(value) == 2:
            env_var_def.append({
                "name": key,
                "secretRef": value[1]
            })
        else:
            env_var_def.append({
                "name": key,
                "value": value[0]
            })

    return env_var_def


def parse_secret_flags(secret_list):
    secret_pairs = {}

    for pair in secret_list:
        key_val = pair.split('=', 1)
        if len(key_val) != 2:
            raise ValidationError("Secrets must be in format \"<key>=<value> <key>=<value> ...\".")
        if key_val[0] in secret_pairs:
            raise ValidationError("Duplicate secret \"{secret}\" found, secret names must be unique.".format(secret=key_val[0]))
        secret_pairs[key_val[0]] = key_val[1]

    secret_var_def = []
    for key, value in secret_pairs.items():
        secret_var_def.append({
            "name": key,
            "value": value
        })

    return secret_var_def


def _update_revision_env_secretrefs(containers, name):
    for container in containers:
        if "env" in container:
            for var in container["env"]:
                if "secretRef" in var:
                    var["secretRef"] = var["secretRef"].replace("{}-".format(name), "")


def _update_revision_env_secretrefs(containers, name):
    for container in containers:
        if "env" in container:
            for var in container["env"]:
                if "secretRef" in var:
                    var["secretRef"] = var["secretRef"].replace("{}-".format(name), "")


def store_as_secret_and_return_secret_ref(secrets_list, registry_user, registry_server, registry_pass, update_existing_secret=False, disable_warnings=False):
    if registry_pass.startswith("secretref:"):
        # If user passed in registry password using a secret

        registry_pass = registry_pass.split("secretref:")
        if len(registry_pass) <= 1:
            raise ValidationError("Invalid registry password secret. Value must be a non-empty value starting with \'secretref:\'.")
        registry_pass = registry_pass[1:]
        registry_pass = ''.join(registry_pass)

        if not any(secret for secret in secrets_list if secret['name'].lower() == registry_pass.lower()):
            raise ValidationError("Registry password secret with name '{}' does not exist. Add the secret using --secrets".format(registry_pass))

        return registry_pass
    else:
        # If user passed in registry password
        if urlparse(registry_server).hostname is not None:
            registry_secret_name = "{server}-{user}".format(server=urlparse(registry_server).hostname.replace('.', ''), user=registry_user.lower())
        else:
            registry_secret_name = "{server}-{user}".format(server=registry_server.replace('.', ''), user=registry_user.lower())

        for secret in secrets_list:
            if secret['name'].lower() == registry_secret_name.lower():
                if secret['value'].lower() != registry_pass.lower():
                    if update_existing_secret:
                        secret['value'] = registry_pass
                    else:
                        raise ValidationError('Found secret with name \"{}\" but value does not equal the supplied registry password.'.format(registry_secret_name))
                return registry_secret_name

        if not disable_warnings:
            logger.warning('Adding registry password as a secret with name \"{}\"'.format(registry_secret_name))  # pylint: disable=logging-format-interpolation
        secrets_list.append({
            "name": registry_secret_name,
            "value": registry_pass
        })

        return registry_secret_name


def parse_list_of_strings(comma_separated_string):
    comma_separated = comma_separated_string.split(',')
    return [s.strip() for s in comma_separated]


def raise_missing_token_suggestion():
    pat_documentation = "https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line"
    raise RequiredArgumentMissingError("GitHub access token is required to authenticate to your repositories. "
                                       "If you need to create a Github Personal Access Token, "
                                       "please run with the '--login-with-github' flag or follow "
                                       "the steps found at the following link:\n{0}".format(pat_documentation))


def _get_default_log_analytics_location(cmd):
    default_location = "eastus"
    providers_client = None
    try:
        providers_client = providers_client_factory(cmd.cli_ctx, get_subscription_id(cmd.cli_ctx))
        resource_types = getattr(providers_client.get(LOG_ANALYTICS_RP), 'resource_types', [])
        res_locations = []
        for res in resource_types:
            if res and getattr(res, 'resource_type', "") == "workspaces":
                res_locations = getattr(res, 'locations', [])

        if len(res_locations) > 0:
            location = res_locations[0].lower().replace(" ", "").replace("(", "").replace(")", "")
            if location:
                return location

    except Exception:  # pylint: disable=broad-except
        return default_location
    return default_location


def get_container_app_if_exists(cmd, resource_group_name, name):
    app = None
    try:
        app = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:  # pylint: disable=bare-except
        pass
    return app


def _get_name(name_or_rid):
    if is_valid_resource_id(name_or_rid):
        return parse_resource_id(name_or_rid)["name"]
    return name_or_rid


def _get_default_containerapps_location(cmd, location=None):
    if location:
        return location
    default_location = "eastus"
    providers_client = None
    try:
        providers_client = providers_client_factory(cmd.cli_ctx, get_subscription_id(cmd.cli_ctx))
        resource_types = getattr(providers_client.get(CONTAINER_APPS_RP), 'resource_types', [])
        res_locations = []
        for res in resource_types:
            if res and getattr(res, 'resource_type', "") == "workspaces":
                res_locations = getattr(res, 'locations', [])

        if len(res_locations) > 0:
            location = res_locations[0].lower().replace(" ", "").replace("(", "").replace(")", "")
            if location:
                return location

    except Exception:  # pylint: disable=broad-except
        return default_location
    return default_location


# Generate random 4 character string
def _new_tiny_guid():
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=4))


# Follow same naming convention as Portal
def _generate_log_analytics_workspace_name(resource_group_name):
    import re
    prefix = "workspace"
    suffix = _new_tiny_guid()
    alphaNumericRG = resource_group_name
    alphaNumericRG = re.sub(r'[^0-9a-z]', '', resource_group_name)
    maxLength = 40

    name = "{}-{}{}".format(
        prefix,
        alphaNumericRG,
        suffix
    )

    if len(name) > maxLength:
        name = name[:maxLength]
    return name


def _get_log_analytics_workspace_name(cmd, logs_customer_id, resource_group_name):
    log_analytics_client = log_analytics_client_factory(cmd.cli_ctx)
    logs_list = log_analytics_client.list_by_resource_group(resource_group_name)
    for log in logs_list:
        if log.customer_id.lower() == logs_customer_id.lower():
            return log.name
    raise ResourceNotFoundError("Cannot find Log Analytics workspace with customer ID {}".format(logs_customer_id))


def _generate_log_analytics_if_not_provided(cmd, logs_customer_id, logs_key, location, resource_group_name):
    if logs_customer_id is None and logs_key is None:
        logger.warning("No Log Analytics workspace provided.")
        _validate_subscription_registered(cmd, LOG_ANALYTICS_RP)

        try:
            log_analytics_client = log_analytics_client_factory(cmd.cli_ctx)
            log_analytics_shared_key_client = log_analytics_shared_key_client_factory(cmd.cli_ctx)
        except Exception as ex:
            handle_raw_exception(ex)

        log_analytics_location = location
        try:
            _ensure_location_allowed(cmd, log_analytics_location, LOG_ANALYTICS_RP, "workspaces")
        except ValidationError:  # pylint: disable=broad-except
            log_analytics_location = _get_default_log_analytics_location(cmd)

        from azure.cli.core.commands import LongRunningOperation
        from azure.mgmt.loganalytics.models import Workspace

        workspace_name = _generate_log_analytics_workspace_name(resource_group_name)
        workspace_instance = Workspace(location=log_analytics_location)
        logger.warning("Generating a Log Analytics workspace with name \"{}\"".format(workspace_name))  # pylint: disable=logging-format-interpolation

        try:
            poller = log_analytics_client.begin_create_or_update(resource_group_name, workspace_name, workspace_instance)
            log_analytics_workspace = LongRunningOperation(cmd.cli_ctx)(poller)
        except Exception as ex:
            handle_raw_exception(ex)

        logs_customer_id = log_analytics_workspace.customer_id
        try:
            logs_key = log_analytics_shared_key_client.get_shared_keys(
                workspace_name=workspace_name,
                resource_group_name=resource_group_name).primary_shared_key
        except Exception as ex:
            handle_raw_exception(ex)

    elif logs_customer_id is None:
        raise ValidationError("Usage error: Supply the --logs-customer-id associated with the --logs-key")
    elif logs_key is None:  # Try finding the logs-key
        log_analytics_client = log_analytics_client_factory(cmd.cli_ctx)
        log_analytics_shared_key_client = log_analytics_shared_key_client_factory(cmd.cli_ctx)

        log_analytics_name = None
        log_analytics_rg = None

        try:
            log_analytics = log_analytics_client.list()
        except Exception as ex:
            handle_raw_exception(ex)

        for la in log_analytics:
            if la.customer_id and la.customer_id.lower() == logs_customer_id.lower():
                log_analytics_name = la.name
                parsed_la = parse_resource_id(la.id)
                log_analytics_rg = parsed_la['resource_group']

        if log_analytics_name is None:
            raise ValidationError('Usage error: Supply the --logs-key associated with the --logs-customer-id')

        try:
            shared_keys = log_analytics_shared_key_client.get_shared_keys(workspace_name=log_analytics_name, resource_group_name=log_analytics_rg)
        except Exception as ex:
            handle_raw_exception(ex)

        if not shared_keys or not shared_keys.primary_shared_key:
            raise ValidationError('Usage error: Supply the --logs-key associated with the --logs-customer-id')

        logs_key = shared_keys.primary_shared_key

    return logs_customer_id, logs_key


def _get_existing_secrets(cmd, resource_group_name, name, containerapp_def):
    if "secrets" not in containerapp_def["properties"]["configuration"]:
        containerapp_def["properties"]["configuration"]["secrets"] = []
    else:
        secrets = []
        try:
            secrets = ContainerAppClient.list_secrets(cmd=cmd, resource_group_name=resource_group_name, name=name)
        except Exception as e:  # pylint: disable=broad-except
            handle_raw_exception(e)

        containerapp_def["properties"]["configuration"]["secrets"] = secrets["value"]


def _ensure_identity_resource_id(subscription_id, resource_group, resource):
    if is_valid_resource_id(resource):
        return resource

    return resource_id(subscription=subscription_id,
                       resource_group=resource_group,
                       namespace='Microsoft.ManagedIdentity',
                       type='userAssignedIdentities',
                       name=resource)


def _add_or_update_secrets(containerapp_def, add_secrets):
    if "secrets" not in containerapp_def["properties"]["configuration"]:
        containerapp_def["properties"]["configuration"]["secrets"] = []

    for new_secret in add_secrets:
        is_existing = False
        for existing_secret in containerapp_def["properties"]["configuration"]["secrets"]:
            if existing_secret["name"].lower() == new_secret["name"].lower():
                is_existing = True
                existing_secret["value"] = new_secret["value"]
                break

        if not is_existing:
            containerapp_def["properties"]["configuration"]["secrets"].append(new_secret)


def _remove_registry_secret(containerapp_def, server, username):
    if urlparse(server).hostname is not None:
        registry_secret_name = "{server}-{user}".format(server=urlparse(server).hostname.replace('.', ''), user=username.lower())
    else:
        registry_secret_name = "{server}-{user}".format(server=server.replace('.', ''), user=username.lower())

    _remove_secret(containerapp_def, secret_name=registry_secret_name)


def _remove_secret(containerapp_def, secret_name):
    if "secrets" not in containerapp_def["properties"]["configuration"]:
        containerapp_def["properties"]["configuration"]["secrets"] = []

    for index, value in enumerate(containerapp_def["properties"]["configuration"]["secrets"]):
        existing_secret = value
        if existing_secret["name"].lower() == secret_name.lower():
            containerapp_def["properties"]["configuration"]["secrets"].pop(index)
            break


def _add_or_update_env_vars(existing_env_vars, new_env_vars):
    for new_env_var in new_env_vars:

        # Check if updating existing env var
        is_existing = False
        for existing_env_var in existing_env_vars:
            if existing_env_var["name"].lower() == new_env_var["name"].lower():
                is_existing = True

                if "value" in new_env_var:
                    existing_env_var["value"] = new_env_var["value"]
                else:
                    existing_env_var["value"] = None

                if "secretRef" in new_env_var:
                    existing_env_var["secretRef"] = new_env_var["secretRef"]
                else:
                    existing_env_var["secretRef"] = None
                break

        # If not updating existing env var, add it as a new env var
        if not is_existing:
            existing_env_vars.append(new_env_var)


def _remove_env_vars(existing_env_vars, remove_env_vars):
    for old_env_var in remove_env_vars:

        # Check if updating existing env var
        is_existing = False
        for i, value in enumerate(existing_env_vars):
            existing_env_var = value
            if existing_env_var["name"].lower() == old_env_var.lower():
                is_existing = True
                existing_env_vars.pop(i)
                break

        # If not updating existing env var, add it as a new env var
        if not is_existing:
            logger.warning("Environment variable {} does not exist.".format(old_env_var))  # pylint: disable=logging-format-interpolation


def _remove_env_vars(existing_env_vars, remove_env_vars):
    for old_env_var in remove_env_vars:

        # Check if updating existing env var
        is_existing = False
        for index, value in enumerate(existing_env_vars):
            existing_env_var = value
            if existing_env_var["name"].lower() == old_env_var.lower():
                is_existing = True
                existing_env_vars.pop(index)
                break

        # If not updating existing env var, add it as a new env var
        if not is_existing:
            logger.warning("Environment variable {} does not exist.".format(old_env_var))  # pylint: disable=logging-format-interpolation


def _add_or_update_tags(containerapp_def, tags):
    if 'tags' not in containerapp_def:
        if tags:
            containerapp_def['tags'] = tags
        else:
            containerapp_def['tags'] = {}
    else:
        for key in tags:
            containerapp_def['tags'][key] = tags[key]


def _object_to_dict(obj):

    def default_handler(x):
        if isinstance(x, datetime):
            return x.isoformat()
        return x.__dict__

    return json.loads(json.dumps(obj, default=default_handler))


def _to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def _convert_object_from_snake_to_camel_case(o):
    if isinstance(o, list):
        return [_convert_object_from_snake_to_camel_case(i) if isinstance(i, (dict, list)) else i for i in o]
    return {
        _to_camel_case(a): _convert_object_from_snake_to_camel_case(b) if isinstance(b, (dict, list)) else b for a, b in o.items()
    }


def _remove_additional_attributes(o):
    if isinstance(o, list):
        for i in o:
            _remove_additional_attributes(i)
    elif isinstance(o, dict):
        if "additionalProperties" in o:
            del o["additionalProperties"]

        for key in o:
            _remove_additional_attributes(o[key])


def _remove_readonly_attributes(containerapp_def):
    unneeded_properties = [
        "id",
        "name",
        "type",
        "systemData",
        "provisioningState",
        "latestRevisionName",
        "latestRevisionFqdn",
        "customDomainVerificationId",
        "outboundIpAddresses",
        "fqdn"
    ]

    for unneeded_property in unneeded_properties:
        if unneeded_property in containerapp_def:
            del containerapp_def[unneeded_property]
        elif unneeded_property in containerapp_def['properties']:
            del containerapp_def['properties'][unneeded_property]


def _remove_dapr_readonly_attributes(daprcomponent_def):
    unneeded_properties = [
        "id",
        "name",
        "type",
        "systemData",
        "provisioningState",
        "latestRevisionName",
        "latestRevisionFqdn",
        "customDomainVerificationId",
        "outboundIpAddresses",
        "fqdn"
    ]

    for unneeded_property in unneeded_properties:
        if unneeded_property in daprcomponent_def:
            del daprcomponent_def[unneeded_property]


def update_nested_dictionary(orig_dict, new_dict):
    # Recursively update a nested dictionary. If the value is a list, replace the old list with new list
    from collections.abc import Mapping

    for key, val in new_dict.items():
        if isinstance(val, Mapping):
            tmp = update_nested_dictionary(orig_dict.get(key, {}), val)
            orig_dict[key] = tmp
        elif isinstance(val, list):
            if new_dict[key]:
                orig_dict[key] = new_dict[key]
        else:
            if new_dict[key] is not None:
                orig_dict[key] = new_dict[key]
    return orig_dict


def _validate_weight(weight):
    try:
        n = int(weight)
        if 0 <= n <= 100:
            return True
        raise ValidationError('Traffic weights must be integers between 0 and 100')
    except ValueError as ex:
        raise ValidationError('Traffic weights must be integers between 0 and 100') from ex


def _update_revision_weights(containerapp_def, list_weights):
    old_weight_sum = 0
    if "traffic" not in containerapp_def["properties"]["configuration"]["ingress"]:
        containerapp_def["properties"]["configuration"]["ingress"]["traffic"] = []

    if not list_weights:
        return 0

    for new_weight in list_weights:
        key_val = new_weight.split('=', 1)
        if len(key_val) != 2:
            raise ValidationError('Traffic weights must be in format \"<revision>=<weight> <revision2>=<weight2> ...\"')
        revision = key_val[0]
        weight = key_val[1]
        _validate_weight(weight)
        is_existing = False

        for existing_weight in containerapp_def["properties"]["configuration"]["ingress"]["traffic"]:
            if "latestRevision" in existing_weight and existing_weight["latestRevision"]:
                if revision.lower() == "latest":
                    old_weight_sum += existing_weight["weight"]
                    existing_weight["weight"] = weight
                    is_existing = True
                    break
            elif "revisionName" in existing_weight and existing_weight["revisionName"].lower() == revision.lower():
                old_weight_sum += existing_weight["weight"]
                existing_weight["weight"] = weight
                is_existing = True
                break
        if not is_existing:
            containerapp_def["properties"]["configuration"]["ingress"]["traffic"].append({
                "revisionName": revision if revision.lower() != "latest" else None,
                "weight": int(weight),
                "latestRevision": revision.lower() == "latest"
            })
    return old_weight_sum


def _validate_revision_name(cmd, revision, resource_group_name, name):
    if revision.lower() == "latest":
        return
    revision_def = None
    try:
        revision_def = ContainerAppClient.show_revision(cmd, resource_group_name, name, revision)
    except:  # pylint: disable=bare-except
        pass

    if not revision_def:
        raise ValidationError(f"Revision '{revision}' is not a valid revision name.")


def _append_label_weights(containerapp_def, label_weights, revision_weights):
    if "traffic" not in containerapp_def["properties"]["configuration"]["ingress"]:
        containerapp_def["properties"]["configuration"]["ingress"]["traffic"] = []

    if not label_weights:
        return

    bad_labels = []
    revision_weight_names = [w.split('=', 1)[0].lower() for w in revision_weights]  # this is to check if we already have that revision weight passed
    for new_weight in label_weights:
        key_val = new_weight.split('=', 1)
        if len(key_val) != 2:
            raise ValidationError('Traffic weights must be in format \"<revision>=<weight> <revision2>=<weight2> ...\"')
        label = key_val[0]
        weight = key_val[1]
        _validate_weight(weight)
        is_existing = False

        for existing_weight in containerapp_def["properties"]["configuration"]["ingress"]["traffic"]:
            if "label" in existing_weight and existing_weight["label"].lower() == label.lower():
                if "revisionName" in existing_weight and existing_weight["revisionName"] and existing_weight["revisionName"].lower() in revision_weight_names:
                    logger.warning("Already passed value for revision {}, will not overwrite with {}.".format(existing_weight["revisionName"], new_weight))  # pylint: disable=logging-format-interpolation
                    is_existing = True
                    break
                revision_weights.append("{}={}".format(existing_weight["revisionName"] if "revisionName" in existing_weight and existing_weight["revisionName"] else "latest", weight))
                is_existing = True
                break

        if not is_existing:
            bad_labels.append(label)

    if len(bad_labels) > 0:
        raise ValidationError(f"No labels '{', '.join(bad_labels)}' assigned to any traffic weight.")


def _update_weights(containerapp_def, revision_weights, old_weight_sum):

    new_weight_sum = sum([int(w.split('=', 1)[1]) for w in revision_weights])
    revision_weight_names = [w.split('=', 1)[0].lower() for w in revision_weights]
    divisor = sum([int(w["weight"]) for w in containerapp_def["properties"]["configuration"]["ingress"]["traffic"]]) - new_weight_sum
    # if there is no change to be made, don't even try (also can't divide by zero)
    if divisor == 0:
        return

    scale_factor = (old_weight_sum - new_weight_sum) / divisor + 1

    for existing_weight in containerapp_def["properties"]["configuration"]["ingress"]["traffic"]:
        if "latestRevision" in existing_weight and existing_weight["latestRevision"]:
            if "latest" not in revision_weight_names:
                existing_weight["weight"] = round(scale_factor * existing_weight["weight"])
        elif "revisionName" in existing_weight and existing_weight["revisionName"].lower() not in revision_weight_names:
            existing_weight["weight"] = round(scale_factor * existing_weight["weight"])

    total_sum = sum([int(w["weight"]) for w in containerapp_def["properties"]["configuration"]["ingress"]["traffic"]])
    index = 0
    while total_sum < 100:
        weight = containerapp_def["properties"]["configuration"]["ingress"]["traffic"][index % len(containerapp_def["properties"]["configuration"]["ingress"]["traffic"])]
        index += 1
        total_sum += 1
        weight["weight"] += 1


def _validate_traffic_sum(revision_weights):
    weight_sum = sum([int(w.split('=', 1)[1]) for w in revision_weights if len(w.split('=', 1)) == 2 and _validate_weight(w.split('=', 1)[1])])
    if weight_sum > 100:
        raise ValidationError("Traffic sums may not exceed 100.")


def _get_app_from_revision(revision):
    if not revision:
        raise ValidationError('Invalid revision. Revision must not be empty')
    if revision.lower() == "latest":
        raise ValidationError('Please provide a name for your containerapp. Cannot lookup name of containerapp without a full revision name.')
    revision = revision.split('--')
    revision.pop()
    revision = "--".join(revision)
    return revision


def _infer_acr_credentials(cmd, registry_server, disable_warnings=False):
    # If registry is Azure Container Registry, we can try inferring credentials
    if ACR_IMAGE_SUFFIX not in registry_server:
        raise RequiredArgumentMissingError('Registry username and password are required if not using Azure Container Registry.')
    not disable_warnings and logger.warning('No credential was provided to access Azure Container Registry. Trying to look up credentials...')
    parsed = urlparse(registry_server)
    registry_name = (parsed.netloc if parsed.scheme else parsed.path).split('.')[0]

    try:
        registry_user, registry_pass, registry_rg = _get_acr_cred(cmd.cli_ctx, registry_name)  # pylint: disable=unused-variable
        return (registry_user, registry_pass)
    except Exception as ex:
        raise RequiredArgumentMissingError('Failed to retrieve credentials for container registry {}. Please provide the registry username and password'.format(registry_name)) from ex


def _registry_exists(containerapp_def, registry_server):
    exists = False
    if "properties" in containerapp_def and "configuration" in containerapp_def["properties"] and "registries" in containerapp_def["properties"]["configuration"]:
        for registry in containerapp_def["properties"]["configuration"]["registries"]:
            if "server" in registry and registry["server"] and registry["server"].lower() == registry_server.lower():
                exists = True
                break
    return exists


# get a value from nested dict without getting IndexError (returns None instead)
# for example, model["key1"]["key2"]["key3"] would become safe_get(model, "key1", "key2", "key3")
def safe_get(model, *keys, default=None):
    if not model:
        return default
    for k in keys[:-1]:
        model = model.get(k, {})
    return model.get(keys[-1], default)


def is_platform_windows():
    return platform.system() == "Windows"


def get_randomized_name(prefix, name=None, initial="rg"):
    from random import randint
    default = "{}_{}_{:04}".format(prefix, initial, randint(0, 9999))
    if name is not None:
        return name
    return default


def generate_randomized_cert_name(thumbprint, prefix, initial="rg"):
    from random import randint
    cert_name = "{}-{}-{}-{:04}".format(prefix[:14], initial[:14], thumbprint[:4].lower(), randint(0, 9999))
    for c in cert_name:
        if not (c.isalnum() or c == '-' or c == '.'):
            cert_name.replace(c, '-')
    return cert_name.lower()


def _set_webapp_up_default_args(cmd, resource_group_name, location, name, registry_server):
    from azure.cli.core.util import ConfiguredDefaultSetter
    with ConfiguredDefaultSetter(cmd.cli_ctx.config, True):
        logger.warning("Setting 'az containerapp up' default arguments for current directory. "
                       "Manage defaults with 'az configure --scope local'")

        cmd.cli_ctx.config.set_value('defaults', 'resource_group_name', resource_group_name)
        logger.warning("--resource-group/-g default: %s", resource_group_name)

        cmd.cli_ctx.config.set_value('defaults', 'location', location)
        logger.warning("--location/-l default: %s", location)

        cmd.cli_ctx.config.set_value('defaults', 'name', name)
        logger.warning("--name/-n default: %s", name)

        # cmd.cli_ctx.config.set_value('defaults', 'managed_env', managed_env)
        # logger.warning("--environment default: %s", managed_env)

        cmd.cli_ctx.config.set_value('defaults', 'registry_server', registry_server)
        logger.warning("--registry-server default: %s", registry_server)


def get_profile_username():
    from azure.cli.core._profile import Profile
    user = Profile().get_current_account_user()
    user = user.split('@', 1)[0]
    if len(user.split('#', 1)) > 1:  # on cloudShell user is in format live.com#user@domain.com
        user = user.split('#', 1)[1]
    return user


def create_resource_group(cmd, rg_name, location):
    from azure.cli.core.profiles import ResourceType, get_sdk
    rcf = _resource_client_factory(cmd.cli_ctx)
    resource_group = get_sdk(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES, 'ResourceGroup', mod='models')
    rg_params = resource_group(location=location)
    return rcf.resource_groups.create_or_update(rg_name, rg_params)


def get_resource_group(cmd, rg_name):
    rcf = _resource_client_factory(cmd.cli_ctx)
    return rcf.resource_groups.get(rg_name)


def _resource_client_factory(cli_ctx, **_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.cli.core.profiles import ResourceType
    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)


def queue_acr_build(cmd, registry_rg, registry_name, img_name, src_dir, dockerfile="Dockerfile", quiet=False):
    import os
    import uuid
    import tempfile
    from ._archive_utils import upload_source_code
    from azure.cli.command_modules.acr._stream_utils import stream_logs
    from azure.cli.command_modules.acr._client_factory import cf_acr_registries_tasks
    from azure.cli.core.commands import LongRunningOperation

    # client_registries = get_acr_service_client(cmd.cli_ctx).registries
    client_registries = cf_acr_registries_tasks(cmd.cli_ctx)

    if not os.path.isdir(src_dir):
        raise ValidationError("Source directory should be a local directory path.")

    docker_file_path = os.path.join(src_dir, dockerfile)
    if not os.path.isfile(docker_file_path):
        raise ValidationError("Unable to find '{}'.".format(docker_file_path))

    # NOTE: os.path.basename is unable to parse "\" in the file path
    original_docker_file_name = os.path.basename(docker_file_path.replace("\\", "/"))
    docker_file_in_tar = '{}_{}'.format(uuid.uuid4().hex, original_docker_file_name)
    tar_file_path = os.path.join(tempfile.gettempdir(), 'build_archive_{}.tar.gz'.format(uuid.uuid4().hex))

    source_location = upload_source_code(cmd, client_registries, registry_name, registry_rg, src_dir, tar_file_path, docker_file_path, docker_file_in_tar)

    # For local source, the docker file is added separately into tar as the new file name (docker_file_in_tar)
    # So we need to update the docker_file_path
    docker_file_path = docker_file_in_tar

    from azure.cli.core.profiles import ResourceType
    OS, Architecture = cmd.get_models('OS', 'Architecture', resource_type=ResourceType.MGMT_CONTAINERREGISTRY, operation_group='runs')
    # Default platform values
    platform_os = OS.linux.value
    platform_arch = Architecture.amd64.value
    platform_variant = None

    DockerBuildRequest, PlatformProperties = cmd.get_models('DockerBuildRequest', 'PlatformProperties',
                                                            resource_type=ResourceType.MGMT_CONTAINERREGISTRY, operation_group='runs')
    docker_build_request = DockerBuildRequest(
        image_names=[img_name],
        is_push_enabled=True,
        source_location=source_location,
        platform=PlatformProperties(
            os=platform_os,
            architecture=platform_arch,
            variant=platform_variant
        ),
        docker_file_path=docker_file_path,
        timeout=None,
        arguments=[])

    queued_build = LongRunningOperation(cmd.cli_ctx)(client_registries.begin_schedule_run(
        resource_group_name=registry_rg,
        registry_name=registry_name,
        run_request=docker_build_request))

    run_id = queued_build.run_id
    logger.info("Queued a build with ID: %s", run_id)
    not quiet and logger.info("Waiting for agent...")

    from azure.cli.command_modules.acr._client_factory import (cf_acr_runs)
    from ._acr_run_polling import get_run_with_polling
    client_runs = cf_acr_runs(cmd.cli_ctx)

    if quiet:
        lro_poller = get_run_with_polling(cmd, client_runs, run_id, registry_name, registry_rg)
        acr = LongRunningOperation(cmd.cli_ctx)(lro_poller)
        logger.info("Build {}.".format(acr.status.lower()))  # pylint: disable=logging-format-interpolation
        if acr.status.lower() != "succeeded":
            raise CLIInternalError("ACR build {}.".format(acr.status.lower()))
        return acr

    return stream_logs(cmd, client_runs, run_id, registry_name, registry_rg, None, False, True)


def _get_acr_cred(cli_ctx, registry_name):
    from azure.mgmt.containerregistry import ContainerRegistryManagementClient
    from azure.cli.core.commands.parameters import get_resources_in_subscription
    from azure.cli.core.commands.client_factory import get_mgmt_service_client

    client = get_mgmt_service_client(cli_ctx, ContainerRegistryManagementClient).registries

    result = get_resources_in_subscription(cli_ctx, 'Microsoft.ContainerRegistry/registries')
    result = [item for item in result if item.name.lower() == registry_name]
    if not result or len(result) > 1:
        raise ResourceNotFoundError("No resource or more than one were found with name '{}'.".format(registry_name))
    resource_group_name = parse_resource_id(result[0].id)['resource_group']

    registry = client.get(resource_group_name, registry_name)

    if registry.admin_user_enabled:  # pylint: disable=no-member
        cred = client.list_credentials(resource_group_name, registry_name)
        return cred.username, cred.passwords[0].value, resource_group_name
    raise ResourceNotFoundError("Failed to retrieve container registry credentials. Please either provide the "
                                "credentials or run 'az acr update -n {} --admin-enabled true' to enable "
                                "admin first.".format(registry_name))


def create_new_acr(cmd, registry_name, resource_group_name, location=None, sku="Basic"):
    # from azure.cli.command_modules.acr.custom import acr_create
    from azure.cli.command_modules.acr._client_factory import cf_acr_registries
    from azure.cli.core.profiles import ResourceType
    from azure.cli.core.commands import LongRunningOperation

    client = cf_acr_registries(cmd.cli_ctx)
    # return acr_create(cmd, client, registry_name, resource_group_name, sku, location)

    Registry, Sku = cmd.get_models('Registry', 'Sku', resource_type=ResourceType.MGMT_CONTAINERREGISTRY, operation_group="registries")
    registry = Registry(location=location, sku=Sku(name=sku), admin_user_enabled=True,
                        zone_redundancy=None, tags=None)

    lro_poller = client.begin_create(resource_group_name, registry_name, registry)
    acr = LongRunningOperation(cmd.cli_ctx)(lro_poller)
    return acr


def set_field_in_auth_settings(auth_settings, set_string):
    if set_string is not None:
        split1 = set_string.split("=")
        fieldName = split1[0]
        fieldValue = split1[1]
        split2 = fieldName.split(".")
        auth_settings = set_field_in_auth_settings_recursive(split2, fieldValue, auth_settings)
    return auth_settings


def set_field_in_auth_settings_recursive(field_name_split, field_value, auth_settings):
    if len(field_name_split) == 1:
        if not field_value.startswith('[') or not field_value.endswith(']'):
            auth_settings[field_name_split[0]] = field_value
        else:
            field_value_list_string = field_value[1:-1]
            auth_settings[field_name_split[0]] = field_value_list_string.split(",")
        return auth_settings

    remaining_field_names = field_name_split[1:]
    if field_name_split[0] not in auth_settings:
        auth_settings[field_name_split[0]] = {}
    auth_settings[field_name_split[0]] = set_field_in_auth_settings_recursive(remaining_field_names,
                                                                              field_value,
                                                                              auth_settings[field_name_split[0]])
    return auth_settings


def update_http_settings_in_auth_settings(auth_settings, require_https, proxy_convention,
                                          proxy_custom_host_header, proxy_custom_proto_header):
    if require_https is not None:
        if "httpSettings" not in auth_settings:
            auth_settings["httpSettings"] = {}
        auth_settings["httpSettings"]["requireHttps"] = require_https

    if proxy_convention is not None:
        if "httpSettings" not in auth_settings:
            auth_settings["httpSettings"] = {}
        if "forwardProxy" not in auth_settings["httpSettings"]:
            auth_settings["httpSettings"]["forwardProxy"] = {}
        auth_settings["httpSettings"]["forwardProxy"]["convention"] = proxy_convention

    if proxy_custom_host_header is not None:
        if "httpSettings" not in auth_settings:
            auth_settings["httpSettings"] = {}
        if "forwardProxy" not in auth_settings["httpSettings"]:
            auth_settings["httpSettings"]["forwardProxy"] = {}
        auth_settings["httpSettings"]["forwardProxy"]["customHostHeaderName"] = proxy_custom_host_header

    if proxy_custom_proto_header is not None:
        if "httpSettings" not in auth_settings:
            auth_settings["httpSettings"] = {}
        if "forwardProxy" not in auth_settings["httpSettings"]:
            auth_settings["httpSettings"]["forwardProxy"] = {}
        auth_settings["httpSettings"]["forwardProxy"]["customProtoHeaderName"] = proxy_custom_proto_header

    return auth_settings


def get_oidc_client_setting_app_setting_name(provider_name):
    provider_name_prefix = provider_name.lower()[:10]  # secret names can't be too long
    return provider_name_prefix + "-authentication-secret"


# only accept .pfx or .pem file
def load_cert_file(file_path, cert_password=None):
    from base64 import b64encode
    from OpenSSL import crypto
    import os

    cert_data = None
    thumbprint = None
    blob = None
    try:
        with open(file_path, "rb") as f:
            if os.path.splitext(file_path)[1] in ['.pem']:
                cert_data = f.read()
                x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
                digest_algorithm = 'sha256'
                thumbprint = x509.digest(digest_algorithm).decode("utf-8").replace(':', '')
                blob = b64encode(cert_data).decode("utf-8")
            elif os.path.splitext(file_path)[1] in ['.pfx']:
                cert_data = f.read()
                try:
                    p12 = crypto.load_pkcs12(cert_data, cert_password)
                except Exception as e:
                    raise FileOperationError('Failed to load the certificate file. This may be due to an incorrect or missing password. Please double check and try again.\nError: {}'.format(e)) from e
                x509 = p12.get_certificate()
                digest_algorithm = 'sha256'
                thumbprint = x509.digest(digest_algorithm).decode("utf-8").replace(':', '')
                pem_data = crypto.dump_certificate(crypto.FILETYPE_PEM, x509)
                blob = b64encode(pem_data).decode("utf-8")
            else:
                raise FileOperationError('Not a valid file type. Only .PFX and .PEM files are supported.')
    except Exception as e:
        raise CLIInternalError(e) from e
    return blob, thumbprint


def check_cert_name_availability(cmd, resource_group_name, name, cert_name):
    name_availability_request = {}
    name_availability_request["name"] = cert_name
    name_availability_request["type"] = CHECK_CERTIFICATE_NAME_AVAILABILITY_TYPE
    try:
        r = ManagedEnvironmentClient.check_name_availability(cmd, resource_group_name, name, name_availability_request)
    except CLIError as e:
        handle_raw_exception(e)
    return r


def validate_hostname(cmd, resource_group_name, name, hostname):
    passed = False
    message = None
    try:
        r = ContainerAppClient.validate_domain(cmd, resource_group_name, name, hostname)
        passed = r["customDomainVerificationTest"] == "Passed" and not r["hasConflictOnManagedEnvironment"]
        if "customDomainVerificationFailureInfo" in r:
            message = r["customDomainVerificationFailureInfo"]["message"]
        elif r["hasConflictOnManagedEnvironment"] and ("conflictingContainerAppResourceId" in r):
            message = "Custom Domain {} Conflicts on the same environment with {}.".format(hostname, r["conflictingContainerAppResourceId"])
    except CLIError as e:
        handle_raw_exception(e)
    return passed, message


def patch_new_custom_domain(cmd, resource_group_name, name, new_custom_domains):
    envelope = ContainerAppCustomDomainEnvelopeModel
    envelope["properties"]["configuration"]["ingress"]["customDomains"] = new_custom_domains
    try:
        r = ContainerAppClient.update(cmd, resource_group_name, name, envelope)
    except CLIError as e:
        handle_raw_exception(e)
    if "customDomains" in r["properties"]["configuration"]["ingress"]:
        return list(r["properties"]["configuration"]["ingress"]["customDomains"])
    else:
        return []


def get_custom_domains(cmd, resource_group_name, name, location=None, environment=None):
    try:
        app = ContainerAppClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
        if location:
            _ensure_location_allowed(cmd, location, "Microsoft.App", "containerApps")
            if _normalize_location(cmd, app["location"]) != _normalize_location(cmd, location):
                raise ResourceNotFoundError('Container app {} is not in location {}.'.format(name, location))
        if environment and (_get_name(environment) != _get_name(app["properties"]["managedEnvironmentId"])):
            raise ResourceNotFoundError('Container app {} is not under environment {}.'.format(name, environment))
        if "ingress" in app["properties"]["configuration"] and "customDomains" in app["properties"]["configuration"]["ingress"]:
            custom_domains = app["properties"]["configuration"]["ingress"]["customDomains"]
        else:
            custom_domains = []
    except CLIError as e:
        handle_raw_exception(e)
    return custom_domains


def set_managed_identity(cmd, resource_group_name, containerapp_def, system_assigned=False, user_assigned=None):
    assign_system_identity = system_assigned
    if not user_assigned:
        user_assigned = []
    assign_user_identities = [x.lower() for x in user_assigned]

    # If identity not returned
    try:
        containerapp_def["identity"]
        containerapp_def["identity"]["type"]
    except:
        containerapp_def["identity"] = {}
        containerapp_def["identity"]["type"] = "None"

    if assign_system_identity and containerapp_def["identity"]["type"].__contains__("SystemAssigned"):
        logger.warning("System identity is already assigned to containerapp")

    # Assign correct type
    try:
        if containerapp_def["identity"]["type"] != "None":
            if containerapp_def["identity"]["type"] == "SystemAssigned" and assign_user_identities:
                containerapp_def["identity"]["type"] = "SystemAssigned,UserAssigned"
            if containerapp_def["identity"]["type"] == "UserAssigned" and assign_system_identity:
                containerapp_def["identity"]["type"] = "SystemAssigned,UserAssigned"
        else:
            if assign_system_identity and assign_user_identities:
                containerapp_def["identity"]["type"] = "SystemAssigned,UserAssigned"
            elif assign_system_identity:
                containerapp_def["identity"]["type"] = "SystemAssigned"
            elif assign_user_identities:
                containerapp_def["identity"]["type"] = "UserAssigned"
    except:
        # Always returns "type": "None" when CA has no previous identities
        pass

    if assign_user_identities:
        try:
            containerapp_def["identity"]["userAssignedIdentities"]
        except:
            containerapp_def["identity"]["userAssignedIdentities"] = {}

        subscription_id = get_subscription_id(cmd.cli_ctx)

        for r in assign_user_identities:
            r = _ensure_identity_resource_id(subscription_id, resource_group_name, r).replace("resourceGroup", "resourcegroup")
            isExisting = False

            if not containerapp_def["identity"].get("userAssignedIdentities"):
                containerapp_def["identity"]["userAssignedIdentities"] = {}

            for old_user_identity in containerapp_def["identity"]["userAssignedIdentities"]:
                if old_user_identity.lower() == r.lower():
                    isExisting = True
                    logger.warning("User identity %s is already assigned to containerapp", old_user_identity)
                    break

            if not isExisting:
                containerapp_def["identity"]["userAssignedIdentities"][r] = {}
