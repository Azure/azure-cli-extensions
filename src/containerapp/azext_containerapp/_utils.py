# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, consider-using-f-string, no-else-return, duplicate-string-formatting-argument

from urllib.parse import urlparse
from azure.cli.command_modules.appservice.custom import (_get_acr_cred)
from azure.cli.core.azclierror import (ValidationError, RequiredArgumentMissingError)
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.log import get_logger
from msrestazure.tools import parse_resource_id

from ._clients import ContainerAppClient
from ._client_factory import handle_raw_exception, providers_client_factory, cf_resource_groups, log_analytics_client_factory, log_analytics_shared_key_client_factory

logger = get_logger(__name__)


def _get_location_from_resource_group(cli_ctx, resource_group_name):
    client = cf_resource_groups(cli_ctx)
    group = client.get(resource_group_name)
    return group.location


def _validate_subscription_registered(cmd, resource_provider, subscription_id=None):
    providers_client = None
    if not subscription_id:
        subscription_id = get_subscription_id(cmd.cli_ctx)

    try:
        providers_client = providers_client_factory(cmd.cli_ctx, subscription_id)
        registration_state = getattr(providers_client.get(resource_provider), 'registration_state', "NotRegistered")

        if not (registration_state and registration_state.lower() == 'registered'):
            raise ValidationError('Subscription {} is not registered for the {} resource provider. Please run \"az provider register -n {} --wait\" to register your subscription.'.format(
                subscription_id, resource_provider, resource_provider))
    except ValidationError as ex:
        raise ex
    except Exception:  # pylint: disable=broad-except
        pass


def _ensure_location_allowed(cmd, location, resource_provider, resource_type):
    providers_client = None
    try:
        providers_client = providers_client_factory(cmd.cli_ctx, get_subscription_id(cmd.cli_ctx))

        if providers_client is not None:
            resource_types = getattr(providers_client.get(resource_provider), 'resource_types', [])
            res_locations = []
            for res in resource_types:
                if res and getattr(res, 'resource_type', "") == resource_type:
                    res_locations = getattr(res, 'locations', [])

            res_locations = [res_loc.lower().replace(" ", "").replace("(", "").replace(")", "") for res_loc in res_locations if res_loc.strip()]

            location_formatted = location.lower().replace(" ", "")
            if location_formatted not in res_locations:
                raise ValidationError("Location '{}' is not currently supported. To get list of supported locations, run `az provider show -n {} --query \"resourceTypes[?resourceType=='{}'].locations\"`".format(
                    location, resource_provider, resource_type))
    except ValidationError as ex:
        raise ex
    except Exception:  # pylint: disable=broad-except
        pass


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


def store_as_secret_and_return_secret_ref(secrets_list, registry_user, registry_server, registry_pass, update_existing_secret=False):
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
        resource_types = getattr(providers_client.get("Microsoft.OperationalInsights"), 'resource_types', [])
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


def _generate_log_analytics_if_not_provided(cmd, logs_customer_id, logs_key, location, resource_group_name):
    if logs_customer_id is None and logs_key is None:
        logger.warning("No Log Analytics workspace provided.")
        try:
            _validate_subscription_registered(cmd, "Microsoft.OperationalInsights")
            log_analytics_client = log_analytics_client_factory(cmd.cli_ctx)
            log_analytics_shared_key_client = log_analytics_shared_key_client_factory(cmd.cli_ctx)

            log_analytics_location = location
            try:
                _ensure_location_allowed(cmd, log_analytics_location, "Microsoft.OperationalInsights", "workspaces")
            except Exception:  # pylint: disable=broad-except
                log_analytics_location = _get_default_log_analytics_location(cmd)

            from azure.cli.core.commands import LongRunningOperation
            from azure.mgmt.loganalytics.models import Workspace

            workspace_name = _generate_log_analytics_workspace_name(resource_group_name)
            workspace_instance = Workspace(location=log_analytics_location)
            logger.warning("Generating a Log Analytics workspace with name \"{}\"".format(workspace_name))  # pylint: disable=logging-format-interpolation

            poller = log_analytics_client.begin_create_or_update(resource_group_name, workspace_name, workspace_instance)
            log_analytics_workspace = LongRunningOperation(cmd.cli_ctx)(poller)

            logs_customer_id = log_analytics_workspace.customer_id
            logs_key = log_analytics_shared_key_client.get_shared_keys(
                workspace_name=workspace_name,
                resource_group_name=resource_group_name).primary_shared_key

        except Exception as ex:
            raise ValidationError("Unable to generate a Log Analytics workspace. You can use \"az monitor log-analytics workspace create\" to create one and supply --logs-customer-id and --logs-key") from ex
    elif logs_customer_id is None:
        raise ValidationError("Usage error: Supply the --logs-customer-id associated with the --logs-key")
    elif logs_key is None:  # Try finding the logs-key
        log_analytics_client = log_analytics_client_factory(cmd.cli_ctx)
        log_analytics_shared_key_client = log_analytics_shared_key_client_factory(cmd.cli_ctx)

        log_analytics_name = None
        log_analytics_rg = None
        log_analytics = log_analytics_client.list()

        for la in log_analytics:
            if la.customer_id and la.customer_id.lower() == logs_customer_id.lower():
                log_analytics_name = la.name
                parsed_la = parse_resource_id(la.id)
                log_analytics_rg = parsed_la['resource_group']

        if log_analytics_name is None:
            raise ValidationError('Usage error: Supply the --logs-key associated with the --logs-customer-id')

        shared_keys = log_analytics_shared_key_client.get_shared_keys(workspace_name=log_analytics_name, resource_group_name=log_analytics_rg)

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
    from msrestazure.tools import resource_id, is_valid_resource_id
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


def _add_or_update_env_vars(existing_env_vars, new_env_vars, is_add=False):
    for new_env_var in new_env_vars:

        # Check if updating existing env var
        is_existing = False
        for existing_env_var in existing_env_vars:
            if existing_env_var["name"].lower() == new_env_var["name"].lower():
                is_existing = True
                if is_add:
                    logger.warning("Environment variable {} already exists. Replacing environment variable value.".format(new_env_var["name"]))  # pylint: disable=logging-format-interpolation

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
            if not is_add:
                logger.warning("Environment variable {} does not exist. Adding as new environment variable.".format(new_env_var["name"]))  # pylint: disable=logging-format-interpolation
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
    import json
    import datetime

    def default_handler(x):
        if isinstance(x, datetime.datetime):
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


def _is_valid_weight(weight):
    try:
        n = int(weight)
        if 0 <= n <= 100:
            return True
        return False
    except ValueError:
        return False


def _update_traffic_weights(containerapp_def, list_weights):
    if "traffic" not in containerapp_def["properties"]["configuration"]["ingress"] or list_weights and len(list_weights):
        containerapp_def["properties"]["configuration"]["ingress"]["traffic"] = []

    for new_weight in list_weights:
        key_val = new_weight.split('=', 1)
        is_existing = False

        if len(key_val) != 2:
            raise ValidationError('Traffic weights must be in format \"<revision>=weight <revision2>=<weigh2> ...\"')

        if not _is_valid_weight(key_val[1]):
            raise ValidationError('Traffic weights must be integers between 0 and 100')

        if not is_existing:
            containerapp_def["properties"]["configuration"]["ingress"]["traffic"].append({
                "revisionName": key_val[0],
                "weight": int(key_val[1])
            })


def _get_app_from_revision(revision):
    if not revision:
        raise ValidationError('Invalid revision. Revision must not be empty')

    revision = revision.split('--')
    revision.pop()
    revision = "--".join(revision)
    return revision


def _infer_acr_credentials(cmd, registry_server):
    # If registry is Azure Container Registry, we can try inferring credentials
    if '.azurecr.io' not in registry_server:
        raise RequiredArgumentMissingError('Registry username and password are required if not using Azure Container Registry.')
    logger.warning('No credential was provided to access Azure Container Registry. Trying to look up credentials...')
    parsed = urlparse(registry_server)
    registry_name = (parsed.netloc if parsed.scheme else parsed.path).split('.')[0]

    try:
        registry_user, registry_pass = _get_acr_cred(cmd.cli_ctx, registry_name)
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
