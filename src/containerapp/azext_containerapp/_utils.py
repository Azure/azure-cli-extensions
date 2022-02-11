# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import (ResourceNotFoundError, ValidationError)
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.log import get_logger
from urllib.parse import urlparse

from ._client_factory import providers_client_factory, cf_resource_groups

logger = get_logger(__name__)


def _get_location_from_resource_group(cli_ctx, resource_group_name):
    client = cf_resource_groups(cli_ctx)
    group = client.get(resource_group_name)
    return group.location


def _validate_subscription_registered(cmd, resource_provider):
    providers_client = None
    try:
        providers_client = providers_client_factory(cmd.cli_ctx, get_subscription_id(cmd.cli_ctx))
        registration_state = getattr(providers_client.get(resource_provider), 'registration_state', "NotRegistered")

        if not (registration_state and registration_state.lower() == 'registered'):
            raise ValidationError('Subscription is not registered for the {} resource provider. Please run \"az provider register -n {} --wait\" to register your subscription.'.format(
                resource_provider, resource_provider))
    except ValidationError as ex:
        raise ex
    except Exception:
        pass


def _ensure_location_allowed(cmd, location, resource_provider):
    providers_client = None
    try:
        providers_client = providers_client_factory(cmd.cli_ctx, get_subscription_id(cmd.cli_ctx))

        if providers_client is not None:
            resource_types = getattr(providers_client.get(resource_provider), 'resource_types', [])
            res_locations = []
            for res in resource_types:
                if res and getattr(res, 'resource_type', "") == 'containerApps':
                    res_locations = getattr(res, 'locations', [])

            res_locations = [res_loc.lower().replace(" ", "") for res_loc in res_locations if res_loc.strip()]

            location_formatted = location.lower().replace(" ", "")
            if location_formatted not in res_locations:
                raise ValidationError("Location '{}' is not currently supported. To get list of supported locations, run `az provider show -n {} --query \"resourceTypes[?resourceType=='containerApps'].locations\"`".format(
                    location, resource_provider))
    except ValidationError as ex:
        raise ex
    except Exception:
        pass


def parse_env_var_flags(env_string, is_update_containerapp=False):
    env_pair_strings = env_string.split(',')
    env_pairs = {}

    for pair in env_pair_strings:
        key_val = pair.split('=')
        if len(key_val) is not 2:
            if is_update_containerapp:
                raise ValidationError("Environment variables must be in the format \"<key>=<value>,<key>=secretref:<value>,...\". If you are updating a Containerapp, did you pass in the flag \"--environment\"? Updating a containerapp environment is not supported, please re-run the command without this flag.")
            raise ValidationError("Environment variables must be in the format \"<key>=<value>,<key>=secretref:<value>,...\".")
        if key_val[0] in env_pairs:
            raise ValidationError("Duplicate environment variable {env} found, environment variable names must be unique.".format(env = key_val[0]))
        value = key_val[1].split('secretref:')
        env_pairs[key_val[0]] = value

    env_var_def = []
    for key, value in env_pairs.items():
        if len(value) is 2:
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


def parse_secret_flags(secret_string):
    secret_pair_strings = secret_string.split(',')
    secret_pairs = {}

    for pair in secret_pair_strings:
        key_val = pair.split('=', 1)
        if len(key_val) is not 2:
            raise ValidationError("--secrets: must be in format \"<key>=<value>,<key>=<value>,...\"")
        if key_val[0] in secret_pairs:
            raise ValidationError("--secrets: duplicate secret {secret} found, secret names must be unique.".format(secret = key_val[0]))
        secret_pairs[key_val[0]] = key_val[1]

    secret_var_def = []
    for key, value in secret_pairs.items():
        secret_var_def.append({
            "name": key,
            "value": value
        })

    return secret_var_def


def store_as_secret_and_return_secret_ref(secrets_list, registry_user, registry_server, registry_pass):
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
            if (urlparse(registry_server).hostname is not None):
                registry_secret_name = "{server}-{user}".format(server=urlparse(registry_server).hostname.replace('.', ''), user=registry_user.lower())
            else:
                registry_secret_name = "{server}-{user}".format(server=registry_server.replace('.', ''), user=registry_user.lower())
            
            for secret in secrets_list:
                if secret['name'].lower() == registry_secret_name.lower():
                    if secret['value'].lower() != registry_pass.lower():
                        raise ValidationError('Found secret with name \"{}\" but value does not equal the supplied registry password.'.format(registry_secret_name))
                    else:
                        return registry_secret_name

            logger.warning('Adding registry password as a secret with name \"{}\"'.format(registry_secret_name))
            secrets_list.append({
                "name": registry_secret_name,
                "value": registry_pass
            })

            return registry_secret_name


def parse_list_of_strings(comma_separated_string):
    comma_separated = comma_separated_string.split(',')
    return [s.strip() for s in comma_separated]
