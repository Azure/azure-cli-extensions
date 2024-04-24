# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.util import CLIError
from azure.cli.command_modules.keyvault._validators import (
    _show_vault_only_deprecate_message, _get_resource_group_from_resource_name
)


def validate_resource_group_name(cmd, ns):
    """
    Populate resource_group_name, if not provided
    """
    if 'keyvault purge' in cmd.name or 'keyvault recover' in cmd.name:
        return

    vault_name = getattr(ns, 'vault_name', None)
    hsm_name = getattr(ns, 'hsm_name', None)
    if 'keyvault update-hsm' in cmd.name or 'keyvault region':
        hsm_name = getattr(ns, 'name', None)

    if vault_name and hsm_name:
        raise CLIError('--name/-n and --hsm-name are mutually exclusive.')

    if vault_name:
        # This is a temporary solution for showing deprecation message only for vaults
        _show_vault_only_deprecate_message(ns)

    if not ns.resource_group_name:
        group_name = _get_resource_group_from_resource_name(cmd.cli_ctx, vault_name, hsm_name)
        if group_name:
            ns.resource_group_name = group_name
        else:
            if vault_name:
                resource_type = 'Vault'
            else:
                resource_type = 'HSM'
            msg = "The {} '{}' not found within subscription."
            raise CLIError(msg.format(resource_type, vault_name if vault_name else hsm_name))
