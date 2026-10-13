# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=import-outside-toplevel

from azure.cli.core.azclierror import InvalidArgumentValueError


# ---- input parsing: compact colon separated syntax ----

def as_list(value, option):
    from azure.cli.core.util import shell_safe_json_parse
    if not value:
        return None
    if isinstance(value, str):
        value = shell_safe_json_parse(value)
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise InvalidArgumentValueError('{} expects a JSON list of objects.'.format(option))
    return value


def _split(value, minimum, option, fmt):
    terms = value.split(':')
    if len(terms) < minimum:
        raise InvalidArgumentValueError("Invalid value '{}' for {}. Expected format: {}".format(value, option, fmt))
    return terms


def parse_roles(roles):
    """Example, ContosoFrontend:Standard_D1_v2:1:Standard"""
    if not roles:
        return None
    roles_json = []
    for role in roles:
        terms = _split(role, 4, '--roles', 'RoleName:SkuName:SkuCapacity:SkuTier')
        roles_json.append({'sku': {'name': terms[1], 'capacity': terms[2], 'tier': terms[3]}, 'name': terms[0]})
    return roles_json


def parse_lbs(lbs, cmd, resource_group_name):
    from azure.mgmt.core.tools import resource_id, is_valid_resource_id
    from azure.cli.core.commands.client_factory import get_subscription_id

    if not lbs:
        return None
    lbs_json = []
    for lb in lbs:
        terms = _split(lb, 5, '--load-balancer-configurations',
                       'LBName:FrontendIPConfiguration:PublicIPAddress:Subnet:PrivateIP')
        ip = terms[2]
        subnet = terms[3]
        private_ip = terms[4]
        if ip and not is_valid_resource_id(ip):
            ip = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx), resource_group=resource_group_name,
                namespace='Microsoft.Network', type='publicIPAddresses', name=ip)
        lbs_json.append({
            'properties': {
                'frontendIPConfigurations': [
                    {
                        'properties': {
                            'publicIPAddress': {'id': ip} if ip else None,
                            'subnet': {'id': subnet} if subnet else None,
                            'privateIPAddress': private_ip if private_ip else None
                        },
                        'name': terms[1]
                    }
                ]
            },
            'name': terms[0]
        })
    return lbs_json


def parse_secrets(secrets, cmd, resource_group_name):
    from azure.mgmt.core.tools import resource_id, is_valid_resource_id
    from azure.cli.core.commands.client_factory import get_subscription_id

    if not secrets:
        return None
    secrets_json = []
    for secret in secrets:
        terms = _split(secret, 1, '--secrets', 'KeyVaultName:CertificateUrl:CertificateUrl2:...:CertificateUrlN')
        vault = terms[0]
        certs = terms[1:]
        if vault and not is_valid_resource_id(vault):
            vault = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx), resource_group=resource_group_name,
                namespace='Microsoft.KeyVault', type='vaults', name=vault)
        secrets_json.append({
            'sourceVault': {'id': vault},
            'vaultCertificates': [{'certificateUrl': cert} for cert in certs]
        })
    return secrets_json


# ---- conversion of the Swagger shaped values to the generated AAZ argument schema ----

def drop_none(value):
    return {k: v for k, v in value.items() if v is not None}


def _get(data, name):
    """Case-insensitive lookup so JSON written for the old CLI keeps working."""
    if not isinstance(data, dict):
        return None
    for key, value in data.items():
        if key.lower() == name.lower():
            return value
    return None


def _sub_resource(data):
    resource_id_ = _get(data, 'id')
    return {'id': resource_id_} if resource_id_ else None


def convert_roles(roles):
    if not roles:
        return None
    result = []
    for role in roles:
        sku = _get(role, 'sku') or {}
        capacity = _get(sku, 'capacity')
        if capacity is not None:
            try:
                capacity = int(capacity)
            except (TypeError, ValueError):
                raise InvalidArgumentValueError("Invalid role capacity '{}'. It must be an integer.".format(capacity))
        result.append(drop_none({
            'name': _get(role, 'name'),
            'sku': drop_none({'name': _get(sku, 'name'), 'capacity': capacity, 'tier': _get(sku, 'tier')}) or None,
        }))
    return result


def convert_lbs(lbs):
    if not lbs:
        return None
    result = []
    for lb in lbs:
        properties = _get(lb, 'properties') or {}
        frontends = []
        for frontend in _get(properties, 'frontendIPConfigurations') or []:
            frontend_props = _get(frontend, 'properties') or {}
            frontends.append(drop_none({
                'name': _get(frontend, 'name'),
                'private_ip_address': _get(frontend_props, 'privateIPAddress'),
                'public_ip_address': _sub_resource(_get(frontend_props, 'publicIPAddress')),
                'subnet': _sub_resource(_get(frontend_props, 'subnet')),
            }))
        result.append(drop_none({
            'id': _get(lb, 'id'),
            'name': _get(lb, 'name'),
            'frontend_ip_configurations': frontends,
        }))
    return result


def convert_secrets(secrets):
    if not secrets:
        return None
    result = []
    for secret in secrets:
        certs = [drop_none({'certificate_url': _get(cert, 'certificateUrl')})
                 for cert in _get(secret, 'vaultCertificates') or []]
        result.append(drop_none({
            'source_vault': _sub_resource(_get(secret, 'sourceVault')),
            'vault_certificates': certs,
        }))
    return result


def convert_extensions(extensions):
    """Return the converted extensions and, per extension, the free-form settings kept out of the schema."""
    result = []
    raw = []
    for extension in extensions:
        props = _get(extension, 'properties') or {}
        key_vault = _get(props, 'protectedSettingsFromKeyVault')
        result.append(drop_none({
            'name': _get(extension, 'name'),
            'auto_upgrade_minor_version': _get(props, 'autoUpgradeMinorVersion'),
            'force_update_tag': _get(props, 'forceUpdateTag'),
            'protected_settings_from_key_vault': drop_none({
                'secret_url': _get(key_vault, 'secretUrl'),
                'source_vault': _sub_resource(_get(key_vault, 'sourceVault')),
            }) if key_vault else None,
            'publisher': _get(props, 'publisher'),
            'roles_applied_to': _get(props, 'rolesAppliedTo'),
            'type': _get(props, 'type'),
            'type_handler_version': _get(props, 'typeHandlerVersion'),
        }))
        raw.append(drop_none({
            'settings': _get(props, 'settings'),
            'protected_settings': _get(props, 'protectedSettings'),
        }))
    return result, raw
