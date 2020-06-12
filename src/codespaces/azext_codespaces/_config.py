# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

DEFAULT_SERVICE_DOMAIN = "online.visualstudio.com"


def get_rp_api_version(cli_ctx):
    return cli_ctx.config.get('codespaces', 'rp_api_version', fallback=None)


def get_service_domain(cli_ctx):
    return cli_ctx.config.get('codespaces', 'service_domain', fallback=DEFAULT_SERVICE_DOMAIN)
