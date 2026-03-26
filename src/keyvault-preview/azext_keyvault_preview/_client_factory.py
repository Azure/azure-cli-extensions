# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.util import CLIError
from .profiles import CUSTOM_MGMT_KEYVAULT


def keyvault_mgmt_client_factory(cli_ctx, **_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    return get_mgmt_service_client(cli_ctx, CUSTOM_MGMT_KEYVAULT)


def cf_mhsm(cli_ctx, _):
    return keyvault_mgmt_client_factory(cli_ctx).managed_hsms


def cf_mhsm_region(cli_ctx, _):
    return keyvault_mgmt_client_factory(cli_ctx).mhsm_regions


def is_azure_stack_profile(cmd=None, cli_ctx=None):
    cli_ctx = cmd.cli_ctx if cmd else cli_ctx
    if not cli_ctx:
        raise CLIError("Can't judge profile without cli_ctx!")
    return cli_ctx.cloud.profile in [
        '2020-09-01-hybrid',
        '2019-03-01-hybrid',
        '2018-03-01-hybrid',
        '2017-03-09-profile'
    ]
